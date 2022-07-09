#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: Nothing more that command line utility
Author: Prabal Pathak
"""

import time
from pathlib import Path
from typing import Optional, Iterable, List
from multiprocessing import Process, Queue

from rich import print
from typer import Typer

cmd_app = Typer()

QUEUE_BUS = Queue()
VIDEO_PATH = ""


@cmd_app.command()
def process(
    number: Optional[int] = 1, video_path: List[Path] = [VIDEO_PATH, VIDEO_PATH]
) -> None:
    """initiate process number=number
    Args:
        number(int): number of processes to run
    Return:
        none
    """
    args = [1, 2, 3]
    kwargs = {"Name": "Prabal", "video_path": video_path}
    for i in range(number):
        QUEUE_BUS.put(i)
        kwargs.update({"Number": i})
        Process(target=print_function, args=[QUEUE_BUS, args], kwargs=kwargs).start()
    print("How are [bold red]you")


def print_function(queue: Iterable[Queue], *args: List[int], **kwargs: dict) -> None:
    """print process id

    Args:
        queue (Queue): queue bus
    """
    _no = queue.get()
    while True:
        print(_no, args, kwargs)
        time.sleep(1)
        if _no < 0:
            break
    print("Hey bro i'm going down!: ", _no)


if __name__ == "__main__":
    cmd_app()
