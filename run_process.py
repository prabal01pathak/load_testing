#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run every possible combinations from max_process and max_thread arguments
"""
import os
import time
from pathlib import Path

from typer import Typer

from load_testing.utils.save_data import create_process_folder

app = Typer()

VIDEO_PATH = "testing_video/demo1.mp4"
DEFAULT_RUN_TIME = 10
RUN_DETECTIONS = True
SAVE_LOG = False


@app.command()
def run(
    process_count: int = 1,
    thread_count: int = 1,
    run_time: int = DEFAULT_RUN_TIME,
    video_path: str = VIDEO_PATH,
    run_detections: bool = RUN_DETECTIONS,
    create_log: bool = SAVE_LOG,
    wait_time: int = 1,
) -> None:
    """run number of combinations from combinations value

    Args:
        run_time (int, optional): _description_. Defaults to DEFAULT_RUN_TIME.
        video_path (str, optional): _description_. Defaults to VIDEO_PATH.
        run_detections (bool, optional): _description_. Defaults to RUN_DETECTIONS.
        create_log (bool, optional): _description_. Defaults to SAVE_LOG.
    """
    log_file = " >> logs/logs.json" if create_log else ""
    create_log = "--create-log" if create_log else "--no-create-log"
    run_detections = "--run-detections" if run_detections else "--no-run-detections"
    for process_number in range(1, process_count+1):
        process_path_dir: Path = create_process_folder(process_number)
        process_path_file = process_path_dir / f"process_data_{process_number}.csv"
        script = f"""\\
                gnome-terminal --tab -- bash -c \\
                \"python3 runapp.py \\
                --process-count 1 \\
                --thread-count {thread_count} \\
                --run-time {run_time} \\
                --video-path {video_path} \\
                --csv-save-path {process_path_file} \\
                {create_log} \\
                {run_detections} \\
                {log_file}\";"""
        print(script)
        os.system(script)
        time.sleep(wait_time)
    print("Completed all combinations")


if __name__ == "__main__":
    app()
