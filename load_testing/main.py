#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: Nothing more that command line utility
"""

import atexit
import time
from pathlib import Path
import os
from typing import Optional, Iterable
import multiprocessing
from multiprocessing import Process, Queue
from threading import Thread
import json

import cv2
from rich import print
from typer import Typer
import uvicorn
import requests
import numpy as np


from .utils.read_video import ReadVideo
from .utils.save_data import (
    Save,
    check_exists,
    create_process_folder,
)  # , start_save_process
from .utils.convertocsv import Converter
from .utils.system_details import ProcessDetails
from .data_collection.app import app

cmd_app = Typer()

QUEUE_BUS = Queue()  # it'll stop all process if put anyting
DATA_QUEUE = Queue()  # data queue to save the data from queue
VIDEO_PATH = "testing_video/demo1.mp4"
DATA_PATH = "./data_files/"
DEFAULT_RUN_TIME = 300  # run processes till that time. should be in seconds
SERVER_URL = "http://127.0.0.1:8000"
RUN_DETECTIONS = True
SHOW_VIDEO = False
SAVE_FILE_PATH: Path = None
SAVE_TO_CSV: bool = True
SAVE_TIME = 2  # after that time save the data to csv. should be in seconds

# set any one of these true and others false
SEND_TO_SERVER = False
SAVE_QUEUE = False
SAVE_LOG = False


@cmd_app.command()
def process(
    process_count: Optional[int] = 1,
    thread_count: int = 1,
    run_time: int = DEFAULT_RUN_TIME,
    video_path: str = VIDEO_PATH,
    run_detections: bool = RUN_DETECTIONS,
    create_log: bool = SAVE_LOG,
    save_to_csv: bool = SAVE_TO_CSV,
    csv_save_path: Path = None
) -> None:
    """initiate process number=number
    Args:
            process_count(int): number of processes to run
            video_path(str): path to video
            thread_count(int): total number of threads to run
            run_time: Running time for application in seconds
    Return:
            None
    """
    global SAVE_FILE_PATH, SAVE_LOG, RUN_DETECTIONS, SAVE_TO_CSV
    SAVE_LOG = create_log
    RUN_DETECTIONS = run_detections
    SAVE_TO_CSV = save_to_csv
    if SAVE_LOG:
        data_file_name = Path(
            f"{DATA_PATH}data_file_{process_count}{thread_count}_0.csv",
        )
        ext = "csv"
    else:
        print("not saving log")
        data_file_name = Path(
            f"{DATA_PATH}data_file_{process_count}{thread_count}_0.json"
        )
        ext = "json"
    path = check_exists(data_file_name, ext=ext)
    SAVE_FILE_PATH = path
    kwargs = {
        "video_path": video_path,
        "thread_count": thread_count,
        "run_time": run_time,
        "data_file": path,
        "run_detections": run_detections,
        "create_log": create_log,
        "saving_instance": None,
        "process_number": None,
        "data_queue": None,
        "thread_number": None,
        "detection_worker": None,
        "process_utils": None,
        "csv_save_path": csv_save_path
    }
    print("[")
    # print(
    #     json.dumps({"run_time": run_time}),
    #     ",",
    #     json.dumps({"time": datetime.now().strftime("%y:%m:%d-%H:%m:%s")}),
    #     end=",",
    # )
    if SEND_TO_SERVER:
        Process(target=run_server).start()
        while not ping_server():
            continue
        requests_util("create", {"path": str(path)})
    for i in range(process_count):
        kwargs.update({"process_number": i + 1, "data_queue": DATA_QUEUE})
        Process(target=create_process, args=[QUEUE_BUS], kwargs=kwargs).start()
        # print("Created Process Number: ", i + 1)


def create_process(queue: Iterable[Queue], **kwargs: dict) -> None:
    """# print process id

    Args:
            queue (Queue): queue bus
    """
    if SAVE_TO_CSV:
        process_path_file: Path = kwargs.get("csv_save_path")
        _save = Save(queue=queue, path=process_path_file, **kwargs)
        kwargs["saving_instance"] = _save
    if RUN_DETECTIONS:
        from .detection_logic.feed_logic.saved_driver import Worker

        detection_worker = Worker()
        kwargs["detection_worker"] = detection_worker
    thread_count = kwargs.get("thread_count")
    create_thread(queue=queue, number=thread_count, **kwargs)
    # print(kwargs)
    # print("created process")


def create_thread(queue: Queue, number: int = 1, **kwargs: dict) -> None:
    """create given number of threads

    Args:
            number (int, optional): Defaults to 1.
    """
    process_utils = ProcessDetails()
    kwargs["process_utils"] = process_utils
    for i in range(1, number + 1):
        kwargs.update({"thread_number": i})
        Thread(target=read_video_thread, args=[queue], kwargs=kwargs).start()
        # print("Started thread Number: ", i + 1)


def read_video_thread(queue: Queue, **kwargs) -> None:
    """read the video from ReadVideo class

    Args:
            path (str, optional): path to video
    """
    detection_worker = kwargs.get("detection_worker")
    video_path = kwargs.get("video_path")
    read_video = ReadVideo(video_path, **kwargs)  # cam class
    read_video.read()
    process_utils: ProcessDetails = kwargs.get(
        "process_utils"
    )  # process related details
    thread_run_time: int = kwargs.get("run_time")
    thread_start_time = time.time()
    total_frames = 0
    save_clock = time.time()  # timer till SAVE_TIME
    running_time = 0
    _save = kwargs.get("saving_instance")
    for frame in read_video.agument_video():
        result: dict = detection_utils(
            frame=frame, worker=detection_worker, process_util=process_utils
        )
        total_frames += 1
        running_time += result.pop("processing_time")
        # collect data according to parameters
        detection_details = result.pop("func_return")
        if completed_save_time(save_clock):
            result["avg_processing_time"] = running_time / total_frames
            result["total_frames"] = total_frames
            result["process_number"] = kwargs.get("process_number")
            result["thread_number"] = kwargs.get("thread_number")
            print(result)
            data_collection(running_data=result, _save=_save)
            save_clock = time.time()
            total_frames = 0
            running_time = 0
        if SHOW_VIDEO:
            show_video(detection_details["processed_frame"])
        if not queue.empty() or not check_running_status(
            thread_start_time, thread_run_time
        ):
            if not SAVE_LOG:
                print(
                    f"Stopping the Process: {kwargs.get('process_number')} \
                \nthread Number: {kwargs.get('thread_number')}"
                )
            break


def completed_save_time(save_clock: time.time) -> bool:
    """if save time completed then save the data

    Args:
        save_clock (time.time): running time

    Returns:
        bool: completed or not
    """
    return time.time() - save_clock >= SAVE_TIME


def show_video(frame: np.ndarray):
    """show cv2 frames

    Args:
        frame (np.ndarray): frame details
    """
    try:
        cv2.imshow("frame", frame)
    except cv2.error as _e:
        print("error when showing frame: ", _e)


@ProcessDetails.running_time
def detection_utils(frame: np.ndarray, worker, **kwargs) -> dict:
    """send for detection

    Args:
        frame (np.ndarray): frames

    Returns:
        dict: detection details
    """
    if RUN_DETECTIONS:
        result: dict = worker.detect(frame)
        return result
    return {"message": "Not running any detections"}


def data_collection(running_data: dict, _save: Save) -> dict:
    """collect the data according to kwargs

    Args:
        queue (Queue): queue if any
        data (dict): details of running time and other details

    Returns:
        dict: acknowledgment
    """
    # if send to server flag set to true then create server data and send that
    if SAVE_TO_CSV:
        _save.save_to_csv([running_data])
    elif SEND_TO_SERVER:
        data = {
            "name": f"thread-{running_data.get('process_number')}{running_data.get('thread_number')}",
            "time": running_data["total_time"],
        }
        Thread(target=requests_util, args=["", data]).start()
    else:
        data = {
            f"thread-{running_data.get('process_number')}{running_data.get('thread_number')}": running_data[
                "total_time"
            ]
        }
        print(json.dumps(data), end=",")
        if SAVE_QUEUE:
            _save.save_without_run(data)
    return {"message": "saved"}


def check_running_status(start_time: float, total_time: float):
    """check running status to run the app till total_time

    Args:
        start_time (float, second): starting time=time.time
        total_time (float, second): total_time = int

    Returns:
        bool: stop or not
    """
    if time.time() - start_time >= total_time:
        return False
    return True


def ping_server() -> bool:
    """ping server check pingable

    Returns:
        _type_: _description_
    """
    try:
        requests.get(SERVER_URL)
        return True
    except requests.exceptions.ConnectionError as _:
        return False


def requests_util(_r: str, data: dict):
    """_summary_

    Args:
        url (_type_): _description_
        data (_type_): _description_
    """
    if _r == "create":
        url = SERVER_URL + "/create_file"
    else:
        url = SERVER_URL + "/save"
    print(data)
    response = requests.post(url, json=data)
    return response.json()


def run_server():
    """run data saving application"""
    uvicorn.run(app)


@atexit.register
def get_process_count():
    """get number of process running"""
    try:
        if not SEND_TO_SERVER:
            processes = multiprocessing.active_children()
            for children in processes:
                children.join()
            if SAVE_LOG:
                print("{}")
                print("]")
                create_log_to_csv()
            else:
                while True:
                    print("All the process completed press (CTRL + C) to exit")
                    time.sleep(300)
    except json.decoder.JSONDecodeError as _:
        pass


def create_log_to_csv():
    """convert log file to csv"""
    csv_converter = Converter("logs/logs.json", SAVE_FILE_PATH)
    csv_converter.convert_json_to_csv()
    os.remove("logs/logs.json")


if __name__ == "__main__":
    cmd_app()
