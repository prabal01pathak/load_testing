#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: Nothing more that command line utility
Author: Prabal Pathak
"""

import time
from pathlib import Path
from typing import Optional, Iterable
from multiprocessing import Process, Queue
import threading
from threading import Thread

from rich import print
from typer import Typer
from loguru import logger

from .utils.read_video import ReadVideo
from .utils.save_data import start_save_process

cmd_app = Typer()

QUEUE_BUS = Queue()
DATA_QUEUE = Queue()
VIDEO_PATH = "/home/prabal/Desktop/Auto_Bottle_Counter/backend/demo_video/demo1.mp4"
DATA_PATH = "/home/prabal/Desktop/Resolute_Projects/load_testing/data_files/"


@cmd_app.command()
def process(
    process_count: Optional[int] = 1,
    video_path: str = VIDEO_PATH,
    thread_count: int = 1,
) -> None:
    """initiate process number=number
    Args:
            number(int): number of processes to run
    Return:
            none
    """
    kwargs = {"video_path": video_path, "thread_count": thread_count}
    data_file_name = Path(f"{DATA_PATH}data_file_{process_count}{thread_count}_0.json")
    start_save_process(path=data_file_name, queue=DATA_QUEUE)
    for i in range(process_count):
        kwargs.update({"process_number": i + 1, "data_queue": DATA_QUEUE})
        Process(target=create_process, args=[QUEUE_BUS], kwargs=kwargs).start()
        # print("Created Process Number: ", i + 1)
    # print("[bold red]How are you")


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


@logger.catch
def read_video_thread(queue: Queue, **kwargs) -> None:
    """read the video from ReadVideo class

    Args:
            path (str, optional): path to video
    """
    # no threading module before multiprocessing

    video_path = kwargs.get("video_path")
    read_video = ReadVideo(video_path, **kwargs)
    read_video.read()
    start_time = time.time()
    total_time = None
    data_queue = kwargs.get("data_queue")
    for _ in read_video.agument_video():
        try:
            end_time = time.time()
            total_time = end_time - start_time
            start_time = time.time()
        except ValueError as _e:
            print("Exception when showing the frame: ", _e)

        finally:
            data = {
                f'frame{kwargs.get("process_number")}_{threading.get_native_id()}': total_time
            }
            data_queue.put(data)
            print(data)
        if not queue.empty():
            print(
                f"Stopping the Process: \
{kwargs.get('process_number')} \nthread Number: {kwargs.get('thread_number')}"
            )
            break


# @atexit.register
def stop_threads():
    """stop all running thread"""
    QUEUE_BUS.put(False)


if __name__ == "__main__":
    cmd_app()
