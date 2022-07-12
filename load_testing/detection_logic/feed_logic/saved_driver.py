"""
Description: Play saved video file inplace of camera feed
Author: Prabal Pathak
"""
import sys
from time import time
import collections
from typing import List

from loguru import logger
import cv2
import numpy as np

from .detector import detect
from .counting_logic import CountingLogic


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
            cv2.rectangle(
                frame, (roi[0], roi[1]), (roi[2], roi[3]), (0, 0, 255), thickness=2
            )
            bbox_message = "Defect"
        elif roi[4] == 0:  # Towel
            cv2.rectangle(
                frame, (roi[0], roi[1]), (roi[2], roi[3]), (0, 255, 0), thickness=2
            )
            bbox_message = "Towel"

        cv2.putText(
            frame,
            bbox_message,
            (roi[0], np.float32(roi[1] - 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            lineType=cv2.LINE_AA,
        )
    return frame


def write_analysis(frame: List[List[float]], analysis) -> List[List[float]]:
    """Writes the Total Counted Towels, Direction and Frame No on processed Frame


    Args:
        frame ([ndarray]): Frame
        analysis ([list]): List containing info of total,towels, defects, direction

    Returns:
        [ndarray]: Frame after writing total towel count, direction and frame no.
    """
    cv2.putText(
        frame,
        "Total Objects: " + str(analysis),
        (10, 30),
        0,
        0.75,
        (255, 255, 255),
        2,
    )
    return frame


class Worker:
    """Worker class to detect the objects
    methods: [detect, fetch_frames]
    """

    def __init__(self):
        self.processed_frame: List[List[float]] = None
        self.bottle_count: int = 0
        self.total_bottles_count: int = None
        self.bottle_threshold: int = None
        self.prev_bottle: int = None
        self.bottle_index: collections.deque = None
        self.centroid_avg: collections.deque = None

    def detect(self, frame: List[float]) -> dict:
        """Take image and return it's detections

        Args:
            image (List[float]): Image array of pixels

        Returns:
            Dict: {
                "total_counts",
                "time_taken",
                "rois",
                "processed_frame(frame with rois)
            }
        """
        return self.fetch_frames(frame)

    @logger.catch
    def fetch_frames(self, frame: List[List[float]]) -> dict:
        """Fetches frames and calls detector
           cap.MV_CC_GetOneFrameTimeout(data_pointer, payload_size, frame_info, timeout),
           no idea how timeout works. Unit: milliseconds

        Args:
            run_detector (bool): Flag for choosing between auto_annotator and detector
            cap (int, MvCamera): MvCamera object. Defaults to 0.
            data_pointer (int, Any): Pointer to the memory location
            that holds the frame. Defaults to 0.
            payload_size (int, Any): Optimum payload size. Defaults to 0.
        """
        self.total_bottles_count = 0
        self.bottle_threshold = 0
        self.prev_bottle = 0
        self.bottle_index = collections.deque(maxlen=3)
        self.centroid_avg = collections.deque([0], maxlen=3)

        start = time()
        rois = detect(frame=frame)
        (
            analysis,
            frame,
            rois,
            self.total_bottles_count,
            self.bottle_threshold,
            self.prev_bottle,
            self.centroid_avg,
            self.bottle_index,
        ) = CountingLogic().count_bottles(
            frame,
            rois,
            self.total_bottles_count,
            self.bottle_threshold,
            self.prev_bottle,
            self.centroid_avg,
            self.bottle_index,
        )

        try:
            self.processed_frame = draw_roi(frame.copy(), rois)
        except Exception as _:
            self.processed_frame = frame.copy()
        self.processed_frame = write_analysis(self.processed_frame, analysis)
        # cv2.imshow('frame', self.processed_frame)
        stop = time()
        time_taken = stop - start
        # logger.debug(f"Time: {time_taken}sec")
        return {
            "total_count": self.total_bottles_count,
            "rois": rois,
            "processed_frame": self.processed_frame,
            "time_taken": time_taken,
        }


def camera_feed():
    """Camera feed"""
    cv2.VideoCapture(0)


if __name__ == "__main__":
    dictonary = {}
    camera_feed()
