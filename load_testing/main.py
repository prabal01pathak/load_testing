#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: Nothing more that command line utility
Author: Prabal Pathak
"""

import atexit
import time
from pathlib import Path
from typing import Optional, Iterable
import multiprocessing
from multiprocessing import Process, Queue
from threading import Thread
import json
from xmlrpc.client import SERVER_ERROR

from rich import print
from typer import Typer
import uvicorn
import requests


from .utils.read_video import ReadVideo
from .utils.save_data import Save, check_exists  # , start_save_process
from .data_collection.app import app

cmd_app = Typer()

QUEUE_BUS = Queue()
DATA_QUEUE = Queue()
VIDEO_PATH = "/home/prabal/Desktop/Auto_Bottle_Counter/backend/demo_video/demo1.mp4"
DATA_PATH = "/home/prabal/Desktop/Resolute_Projects/load_testing/data_files/"
DEFAULT_RUN_TIME = 20
SERVER_URL = "http://127.0.0.1:8000"


@cmd_app.command()
def process(
    process_count: Optional[int] = 1,
    thread_count: int = 1,
    run_time: int = DEFAULT_RUN_TIME,
    video_path: str = VIDEO_PATH,
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
    data_file_name = Path(f"{DATA_PATH}data_file_{process_count}{thread_count}_0.json")
    path = check_exists(data_file_name)
    kwargs = {
        "video_path": video_path,
        "thread_count": thread_count,
        "run_time": run_time,
        "data_file": path,
    }
    # _save = Save(queue=DATA_QUEUE, path=path, **kwargs)
    # _save.write_initial_json()
    print("[")
    # start_save_process(path=data_file_name, queue=DATA_QUEUE, **kwargs)
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


# @logger.catch
def read_video_thread(queue: Queue, **kwargs) -> None:
    """read the video from ReadVideo class

    Args:
            path (str, optional): path to video
    """
    # no threading module before multiprocessing
    thread_start_time = time.time()
    thread_run_time: int = kwargs.get("run_time")
    video_path = kwargs.get("video_path")
    read_video = ReadVideo(video_path, **kwargs)
    read_video.read()
    start_time = time.time()
    total_time = None
    # data_queue = kwargs.get("data_queue")
    # path = kwargs.get("data_file")
    # _save = Save(queue=DATA_QUEUE, path=path, **kwargs)
    # kwargs["saving_instance"] = _save

    for _ in read_video.agument_video():
        try:
            end_time = time.time()
            total_time = end_time - start_time
            start_time = time.time()
            data = {
                "name": f"thread-{kwargs.get('process_number')}{kwargs.get('thread_number')}",
                "time": total_time,
            }
            # data_queue.put(data)
            # print(json.dumps(data), end=",")
            Thread(target=requests_util, args=["", data]).start()
            # _save.save_without_run(data)
            # time.sleep(0.0001)
        except ValueError as _e:
            print("Exception when showing the frame: ", _e)
        if not queue.empty() or not check_running_status(
            thread_start_time, thread_run_time
        ):
            # print(
            #     f"Stopping the Process: {kwargs.get('process_number')} \nthread Number: {kwargs.get('thread_number')}"
            # )
            break


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
    except Exception as _:
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
    uvicorn.run(app)


@atexit.register
def get_process_count():
    """get number of process running"""
    # processes = multiprocessing.active_children()
    # for children in processes:
    #     children.join()
    print("{}")
    print("]")
    # print("Completed all tasks I'm done")


if __name__ == "__main__":
    cmd_app()
