#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: Nothing more that command line utility
Author: Prabal Pathak
"""

import atexit
import time
from pathlib import Path
from datetime import datetime
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


from .utils.read_video import ReadVideo
from .utils.save_data import check_exists  # , start_save_process
from .utils.convertocsv import Converter
from .data_collection.app import app

cmd_app = Typer()

QUEUE_BUS = Queue()
DATA_QUEUE = Queue()
VIDEO_PATH = "/home/prabal/Desktop/Auto_Bottle_Counter/backend/demo_video/demo1.mp4"
DATA_PATH = "/home/prabal/Desktop/Resolute_Projects/load_testing/data_files/"
DEFAULT_RUN_TIME = 300
SERVER_URL = "http://127.0.0.1:8000"
RUN_DETECTIONS = True
SHOW_VIDEO = False
SAVE_FILE_PATH: Path = None

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
    global SAVE_FILE_PATH, SAVE_LOG, RUN_DETECTIONS
    SAVE_LOG = create_log
    RUN_DETECTIONS = run_detections
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
    }
    print("[")
    print(
        json.dumps(
            {"run_time": run_time, "time": datetime.now().strftime("%y:%m:%d-%H:%m:%s")}
        ),
        end=",",
    )
    if SAVE_QUEUE:
        from .utils.save_data import Save

        _save = Save(queue=DATA_QUEUE, path=path, **kwargs)
        _save.write_initial_json()
        # start_save_process(path=data_file_name, queue=DATA_QUEUE, **kwargs)
        kwargs["saving_instance"] = _save
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
    for i in range(number):
        kwargs.update({"thread_number": i})
        Thread(target=read_video_thread, args=[queue], kwargs=kwargs).start()
        # print("Started thread Number: ", i + 1)


def read_video_thread(queue: Queue, **kwargs) -> None:
    """read the video from ReadVideo class

    Args:
            path (str, optional): path to video
    """
    data_queue = kwargs.get("data_queue")
    thread_start_time = time.time()
    detection_worker = kwargs.get("detection_worker")
    thread_run_time: int = kwargs.get("run_time")
    video_path = kwargs.get("video_path")
    read_video = ReadVideo(video_path, **kwargs)
    read_video.read()
    start_time = time.time()
    total_time = None

    for frame in read_video.agument_video():
        try:
            if kwargs.get("run_detections"):
                detection_details: dict = detection_worker.detect(frame)

            end_time = time.time()
            total_time = end_time - start_time
            start_time = time.time()

            # collect data according to parameters
            data_collection(data_queue, {"total_time": total_time}, **kwargs)
            if SHOW_VIDEO:
                try:
                    cv2.imshow("frame", detection_details["processed_frame"])
                except cv2.error as _e:
                    print("error when showing frame: ", _e)
        except ValueError as _e:
            print("Exception when showing the frame: ", _e)

        if not queue.empty() or not check_running_status(
            thread_start_time, thread_run_time
        ):
            if not SAVE_LOG:
                print(
                    f"Stopping the Process: {kwargs.get('process_number')} \
                \nthread Number: {kwargs.get('thread_number')}"
                )
            break


def data_collection(queue: Queue, running_data: dict, **kwargs) -> dict:
    """collect the data according to kwargs

    Args:
        queue (Queue): queue if any
        data (dict): details of running time and other details

    Returns:
        dict: acknowledgment
    """
    # if send to server flag set to true then create server data and send that
    if SEND_TO_SERVER:
        data = {
            "name": f"thread-{kwargs.get('process_number')}{kwargs.get('thread_number')}",
            "time": running_data["total_time"],
        }
        Thread(target=requests_util, args=["", data]).start()
    else:
        data = {
            f"thread-{kwargs.get('process_number')}{kwargs.get('thread_number')}": running_data[
                "total_time"
            ]
        }
        print(json.dumps(data), end=",")
        if SAVE_QUEUE:
            queue.put(data)
            _save = kwargs.get("saving_instance")
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
    except json.decoder.JSONDecodeError as _:
        pass


def create_log_to_csv():
    """convert log file to csv"""
    csv_converter = Converter("logs/logs.json", SAVE_FILE_PATH)
    csv_converter.convert_json_to_csv()
    os.remove("logs/logs.json")


if __name__ == "__main__":
    cmd_app()
