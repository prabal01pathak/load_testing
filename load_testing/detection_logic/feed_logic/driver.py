""" 
Description: This function is used to set the exposure time and gain of the camera
Author: Kunal Sahu & Prabal Pathak
"""
from multiprocessing import set_start_method
import sys
from time import sleep, time
import os
import json
from threading import Timer
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import collections
from ctypes import *
from loguru import logger
import numpy as np
from numba import jit
import cv2

from .imports.CameraParams_const import *
from .imports.CameraParams_header import *
from .imports.MvCameraControl_class import *
from .imports.MvCameraControl_header import *
from .imports.MvErrorDefine_const import *
from .imports.PixelType_const import *
from .imports.PixelType_header import *
from .settings import __APP_SETTINGS__
from .detector import detect
from .logic_v2 import CountingLogic
from .excel_handler import write_csv


def is_dir(path):
    """Helper function which creates directory if it does not exist

    Args:
        path ([str]): Path of the directory to be created if does not exist
    """
    if not os.path.isdir(path):
        logger.debug(f'Creating {path}...')
        os.mkdir(path)


def error_message(message):
    """Helper function which logs error message and exits

    Args:
        message ([str]): Message to be displayed
    """
    logger.error(message)
    sys.exit()


def warning_message(message):
    """Helper function which logs warning message

    Args:
        message ([str]): Message to be displayed
    """
    logger.warning(message)


def setup_host():
    """Returns list of devices connected

    Returns:
        [list]: List of connected devices
    """
    SDKVersion = MvCamera.MV_CC_GetSDKVersion()
    logger.debug(f'SDKVersion: {SDKVersion}')

    device_type = MV_GIGE_DEVICE
    device_list = MV_CC_DEVICE_INFO_LIST()

    ret = MvCamera.MV_CC_EnumDevices(device_type, device_list)
    if ret != 0:
        error_message(f'Enum of Devices Failed! ret[0x{ret}]')

    if device_list.nDeviceNum == 0:
        error_message('No Device Found!')

    logger.debug(f'{device_list.nDeviceNum} Devices Found!')

    return device_list


def show_devices_ip(device_list):
    """Prints IP of connected devices

    Args:
        device_list ([list]): List of connected devices
    """
    for itr in range(0, device_list.nDeviceNum):
        mvcc_dev_info = cast(device_list.pDeviceInfo[itr], POINTER(
            MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            logger.debug(f'GIGE Device: {itr}')

            model_name = ""
            for word in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                model_name = model_name + chr(word)

            logger.debug(f'Device Model Name: {model_name}')

            nip1 = (
                (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = (
                (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = (
                (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            logger.debug(f'Current IP: {nip1}.{nip2}.{nip3}.{nip4}')


def get_camera_object(device_list):
    """Returns a camera object for the selected device from device_list

    Args:
        device_list ([list]): List of connected devices

    Returns:
        [MvCamera]: MvCamera object
    """
    # This value holds index of the connected devices
    # During scaling, this value should be changed if more than 1 devices are connected to the host
    # It can also be taken as an input via terminal
    connection_number = int(os.environ['CAM'])

    if int(connection_number) >= device_list.nDeviceNum:
        error_message(f'Invalid Input. {device_list.nDeviceNum} Devices Found')

    cap = MvCamera()

    selected_device = cast(device_list.pDeviceInfo[int(
        connection_number)], POINTER(MV_CC_DEVICE_INFO)).contents

    ret = cap.MV_CC_CreateHandle(selected_device)
    if ret != 0:
        error_message(f'Handle Creation Failed! ret[0x{ret}]')

    ret = cap.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        error_message(f'Opening Device Failed! ret[0x{ret}]')

    ret = cap.MV_CC_SetEnumValueByString("PixelFormat", "BayerGB8")
    if ret == 0:
        # logger.debug('Pixel Format set to BayerGB8')
        logger.info(
            f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}::Pixel Format set to BayerGB8')
    ret = cap.MV_CC_SetFloatValue("Gain", __APP_SETTINGS__.GAIN)
    if ret == 0:
        # logger.debug('Gain set to 0.5')
        logger.info(
            f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}::Gain set to 20')

    ret = cap.MV_CC_SetFloatValue(
        "ExposureTime", __APP_SETTINGS__.EXPOSURE_TIME)
    if ret == 0:
        # logger.debug('Gain set to 0.5')
        logger.info(
            f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}::Exposure set to 1000')

    return cap


def get_payload_size(cap):
    """Returns optimum payload size

    Args:
        cap ([MvCamera]): MvCamera object for selected device

    Returns:
        [Any]: Optimum payload size
    """
    # Detecting Optimal Packet Size for the Network (works only for GIGE Camera)
    packet_size = cap.MV_CC_GetOptimalPacketSize()
    # packet_size = 8192

    logger.info("-------------------------------", packet_size)
    if packet_size > 0:
        ret = cap.MV_CC_SetIntValue('GevSCPSPacketSize', packet_size)
        if ret != 0:
            warning_message(f'Failed when Setting Packet Size! ret[0x{ret}]')
    else:
        warning_message(
            f'Failed when Getting Packet Size! ret[0x{packet_size}]')

    ret = cap.MV_CC_SetEnumValue('TriggerMode', MV_TRIGGER_MODE_OFF)
    if ret != 0:
        error_message(f'Failed when Setting Trigger Mode! ret[0x{ret}]')

    # Get Payload Size
    st_param = MVCC_INTVALUE()

    memset(byref(st_param), 0, sizeof(MVCC_INTVALUE))

    ret = cap.MV_CC_GetIntValue('PayloadSize', st_param)
    if ret != 0:
        error_message(f'Failed when Getting Payload Size! ret[0x{ret}]')

    payload_size = st_param.nCurValue

    ret = cap.MV_CC_StartGrabbing()
    if ret != 0:
        error_message(f'Failed when Starting Grabbing of Frames! ret[0x{ret}]')

    return payload_size


@jit(forceobj=True)
def format_frame(frame, height, width):
    """ Formats the frame to be used in the application"""
    return cv2.cvtColor(np.reshape(frame, (height, width, -1)), cv2.COLOR_BAYER_GB2RGB)


def get_numpy_array(frame_info, data_pointer):
    """Returns frame as an ndarray

    Args:
        frame_info ([Any]): Information of the frame
        data_pointer ([Any]): Pointer to the memory location that holds the frame

    Returns:
        [ndarray]: Image as an ndarray
    """
    if data_pointer is None:
        return None

    st_param = MV_SAVE_IMAGE_PARAM_EX()
    st_param.nWidth = frame_info.nWidth
    st_param.nHeight = frame_info.nHeight
    st_param.nDataLen = frame_info.nFrameLen
    st_param.pData = cast(data_pointer, POINTER(c_ubyte))

    frame_buffer = (c_ubyte * st_param.nDataLen)()
    try:
        memmove(byref(frame_buffer), st_param.pData, st_param.nDataLen)
        frame = np.array(frame_buffer[:], dtype=np.uint8)
        frame = np.reshape(frame, (st_param.nHeight, st_param.nWidth, -1))
        frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_GB2RGB)
    except Exception as e:
        error_message(e)
    if frame_buffer is not None:
        del frame_buffer

    return frame


def draw_roi(frame, rois):
    """Draws centroids, bounding boxes and writes class according to rois

    Args:
        frame ([ndarray]): Frame
        rois ([list[list]]): list of lists of coordinates
                             Format of roi = [xmin,ymin,xmax,ymax,classid]

    Returns:
        [ndarray]: Frame after drawing bounding boxes
    """
    for roi in rois:

        # creating the centroid
        center = (int((roi[0] + roi[2]) / 2), int((roi[1] + roi[3]) / 2))
        cv2.circle(frame, center, 2, (0, 0, 255), 1)

        if roi[4] == 1:  # Defect
            cv2.rectangle(frame, (roi[0], roi[1]),
                          (roi[2], roi[3]), (0, 0, 255), thickness=2)
            bbox_message = 'Bottle'
        elif roi[4] == 0:  # Bottle
            cv2.rectangle(frame, (roi[0], roi[1]),
                          (roi[2], roi[3]), (0, 255, 0), thickness=2)
            bbox_message = 'Bottle'

        # cv2.putText(frame, bbox_message, (roi[0], np.float32(roi[1] - 2)), cv2.FONT_HERSHEY_SIMPLEX,
        #             0.5, (0, 0, 0), 1, lineType=cv2.LINE_AA)
    return frame


def write_analysis(frame, analysis, frame_number):
    """ Writes the Total Counted Bottles, Direction and Frame No on processed Frame


    Args:
        frame ([ndarray]): Frame
        analysis ([list]): List containing info of total,bottles, defects, direction
        frame_number ([int]): contains the No of the executes frame

    Returns:
        [ndarray]: Frame after writing total towel count, direction and frame no.
    """
    cv2.putText(frame, "Total Bottles Counted" + ": " +
                str(analysis), (10, 30), 0, 0.75, (255, 255, 255), 2)

    cv2.putText(frame, "Frame" + ":" +
                str(frame_number), (10, 60), 0, 0.75, (255, 255, 255), 2)
    cv2.putText(frame, "Time" + ":" +
                str(datetime.now().strftime('%H:%M:%S')), (10, 110), 0, 0.75, (255, 255, 255), 2)
    return frame


def save_annotations(rois, filename):
    """Writes annotations and saves .txt file

    Args:
        rois ([list[list]]): list of lists of coordinates
                            Format of annotaion = [class_id, x_center, y_center, width_img, height_img]
        filename ([str]): Text file path with filename
    """
    file_pointer = open(filename, 'w')
    for roi in rois:
        text = f'{roi[0]} {roi[1]} {roi[2]} {roi[3]} {roi[4]}\n'
        file_pointer.write(text)

    file_pointer.close()


class Worker:
    def __init__(self, run_detector=True, save_original=True):
        self.run_detector = run_detector
        self.save_original = save_original
        self.processed_frame = None
        self.frame_number = 0
        self.run_fetch_frames = True
        self.bottle_count = 0
        self.prev_bottle_count = 0
        self.processed_out_folder = None
        self.max_frame_count = 100000
        self.up_time = None
        self.total_bottles_count = 0
        self.bottle_threshold = 0
        self.prev_bottle = 0
        self.bottle_index = None
        self.Xcentroid_avg = None
        self.Ycentroid_avg = None
    @logger.catch
    def fetch_frames(self):
        """Fetches frames and calls detector
        cap.MV_CC_GetOneFrameTimeout(data_pointer, payload_size, frame_info, timeout), no idea how timeout works. Unit: milliseconds

        Args:
            run_detector (bool): Flag for choosing between auto_annotator and detector
            cap (int, MvCamera): MvCamera object. Defaults to 0.
            data_pointer (int, Any): Pointer to the memory location that holds the frame. Defaults to 0.
            payload_size (int, Any): Optimum payload size. Defaults to 0.
        """
        self.up_time = datetime.now().isoformat()
        logger.info("up Time: ", self.up_time)
        self.total_bottles_count = 0
        self.bottle_threshold = 0
        self.prev_bottle = 0
        self.bottle_index = collections.deque(maxlen=3)
        self.Xcentroid_avg = collections.deque(maxlen=3)
        self.Ycentroid_avg = collections.deque(maxlen=3)
        self.frame_number = 0
        parent_processed_folder = 'processed_live_frames'
        is_dir(parent_processed_folder)
        processed_out_folder = __APP_SETTINGS__.FOLDER_NAME + \
            "_" + str(datetime.now().strftime("%H:%M:%S"))
        self.processed_out_folder = processed_out_folder
        processed_out_path = os.path.join(
            parent_processed_folder, processed_out_folder)
        is_dir(processed_out_path)
        evaluation_path = os.path.join(
            parent_processed_folder, f'evaluation{__APP_SETTINGS__.FOLDER_NAME}')
        is_dir(evaluation_path)

        if self.save_original:
            parent_unprocessed_folder = 'unprocessed_frames'
            is_dir(parent_unprocessed_folder)
            unprocessed_out_folder = processed_out_folder
            unprocessed_out_path = os.path.join(
                parent_unprocessed_folder, unprocessed_out_folder)
            is_dir(unprocessed_out_path)

        if not self.run_detector:
            parent_annotation_folder = 'processed_annotations'
            is_dir(parent_annotation_folder)
            annotation_out_folder = processed_out_folder
            annotation_out_path = os.path.join(
                parent_annotation_folder, annotation_out_folder)
            is_dir(annotation_out_path)

        frame_info = MV_FRAME_OUT_INFO_EX()
        memset(byref(frame_info), 0, sizeof(frame_info))
        evaluation_frame = 0
        grab_error = 0
        start_time =time() 
        total_images = 0
        while self.run_fetch_frames:
            start = time()
            ret = self.cap.MV_CC_GetOneFrameTimeout(
                self.data_pointer, self.payload_size, frame_info, 73)
            if ret == 0:
                logger.debug(
                    f'Fetched: Width[{frame_info.nWidth}], Height[{frame_info.nHeight}], PixelType[0x{frame_info.enPixelType}], FrameNumber[{self.frame_number}]')
                frame = get_numpy_array(frame_info, self.data_pointer)
                if frame is None:
                    error_message('Frame is None!')
                if self.run_detector:
                    rois = detect(frame, self.run_detector)
                    analysis, frame, rois, self.total_bottles_count, self.bottle_threshold, self.prev_bottle, self.Xcentroid_avg, self.Ycentroid_avg, self.bottle_index, self.frame_number = CountingLogic(
                    ).count_bottles(frame, rois, self.total_bottles_count, self.bottle_threshold, self.prev_bottle, self.Xcentroid_avg, self.Ycentroid_avg, self.bottle_index, self.frame_number)

                    try:
                        processed_frame = draw_roi(frame, rois)
                    except:
                        processed_frame = frame
                    self.processed_frame = write_analysis(
                        processed_frame, analysis, self.frame_number)
                    # cv2.imwrite(os.path.join(processed_out_path, str(
                    #     self.frame_number)+'.jpg'), self.processed_frame)
                    cv2.imwrite(os.path.join(evaluation_path, str(
                        evaluation_frame)+'.jpg'), self.processed_frame)
                    # write_csv(datetime.now().strftime('%m/%d/%Y'),datetime.now().strftime('%H:%M:%S'),processed_out_folder, analysis)
                    self.bottle_count = analysis
                    # cv2.imshow('Live Feed', self.processed_frame)
                else:
                    # cv2.imwrite(os.path.join(annotation_out_path, str(
                    #     self.frame_number)+'.jpg'), frame)
                    annotations, rois = detect(frame, self.run_detector)
                    filename = os.path.join(annotation_out_path, str(
                        self.frame_number) + '.txt')
                    save_annotations(annotations, filename)
                    self.processed_frame = draw_roi(frame, rois)
                    # cv2.imwrite(os.path.join(processed_out_path, str(
                    #     self.frame_number)+'.jpg'), self.processed_frame)

                logger.debug('Saved!')
                stop = time()
                time_taken = stop-start
                logger.debug(f'Time: {time_taken}sec')
                total_time = time() - start_time
                total_images += 1
                logger.info(f'Total Time: {total_time}sec\n and Images: {total_images}')
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # cv2.destroyAllWindows()
                    ret = self.cap.MV_CC_StopGrabbing()
                    if ret != 0:
                        error_message(
                            f'Failed when Stopping Grabbing of Frames! ret[0x{ret}]')

                    ret = self.cap.MV_CC_CloseDevice()
                    if ret != 0:
                        error_message(f'Closing Device Failed! ret[0x{ret}]')

                    ret = self.cap.MV_CC_DestroyHandle()
                    if ret != 0:
                        error_message(f'Destrying Handle Failed! ret[0x{ret}]')
                self.frame_number += 1
                evaluation_frame += 1
                if self.frame_number > self.max_frame_count:
                    self.frame_number = 0

                if self.frame_number % 12500 == 0:  # 12500
                    # write_csv(datetime.now().strftime(
                    #     '%m/%d/%Y'), datetime.now().strftime('%H:%M:%S'), processed_out_folder, analysis)
                    pass

            else:
                grab_error += 1
                if grab_error == 60:
                    error_message(f'No Data [0x{ret}]')

        if self.frame_number >= 500:
            self.frame_number == 0

    def stop_fetch_frames(self):
        """ Stop fetching frames from camera. """
        self.run_fetch_frames = False

    def yield_video(self):
        """ Yields video frames. """
        while self.run_fetch_frames:
            frame = cv2.imencode('.jpg', self.processed_frame)[1].tobytes()
            sleep(0.7)
            yield (b'--frame\r\n'
                   b'Content-Type:image/jpeg\r\n'
                   b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
                   b'\r\n' + frame + b'\r\n')
            # yield (b'--frame\r\n'
            #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def yield_counting(self):
        """ Yields bottle count. """
        # while self.run_fetch_frames:
        #    sleep(0.01)
        count = self.bottle_count
        data = {
            "count": count
        }
        # yield data
        return data

    def yield_counting2(self):
        """ Yields bottle count. """
        while self.run_fetch_frames:
            count = self.bottle_count
            data = {
                "count": count
            }
            yield json.dumps(data)

    def add_counting_values(self):
        """ Adds bottle count to database. """
        data = {
            "date": datetime.now().strftime('%m/%d/%Y'),
            "time": datetime.now().strftime('%H:%M:%S'),
            "folder_name": self.processed_out_folder,
            "count": self.bottle_count,
            "cam": __APP_SETTINGS__.CAM_NAME
        }
        # crud.add_counting(**data)
        logger.info(data)
        return data
        # bottle_count = self.bottle_count - self.prev_bottle_count
        # write_csv(datetime.now().strftime('%m/%d/%Y'), datetime.now().strftime('%H:%M:%S'),
        #           self.processed_out_folder, self.bottle_count)
        # self.prev_bottle_count = self.bottle_count


    def start_video(self):
        self.device_list = setup_host()
        # if self.print_devices_ip:
        #     show_devices_ip(self.device_list)
        self.cap = get_camera_object(self.device_list)
        self.payload_size = get_payload_size(self.cap)
        self.data_buffer = (c_ubyte * self.payload_size)()
        self.data_pointer = byref(self.data_buffer)
        return self.cap

    def stop_video(self):
        ret = self.cap.MV_CC_StopGrabbing()
        if ret != 0:
            error_message(
                f'Failed when Stopping Grabbing of Frames! ret[0x{ret}]')

        ret = self.cap.MV_CC_CloseDevice()
        if ret != 0:
            error_message(f'Closing Device Failed! ret[0x{ret}]')

        ret = self.cap.MV_CC_DestroyHandle()
        if ret != 0:
            error_message(f'Destrying Handle Failed! ret[0x{ret}]')
        return

    def main(self):
        """Main function which handles the calling

        Args:
            print_devices_ip (bool): Flag for printing IP of connected devices. Defaults to False.
            run_detector (bool): Flag for choosing between auto_annotator and detector. Defaults to True.
        """
        with ThreadPoolExecutor() as executor:
            self.executor = executor
            self.executor.submit(self.fetch_frames)
        # self.fetch_frames()
