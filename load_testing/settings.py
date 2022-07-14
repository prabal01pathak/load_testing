"""
Description: application settings module 
instend of defining settings on top of module define them here
"""
from pathlib import Path
from multiprocessing import Queue
from dataclasses import dataclass


@dataclass
class Settings:
    """define every settings and it's retriving methods"""

    log_file: Path = Path("logs/logs.json")
    test_files: Path = Path("data_files/test_files/")
    video_path: Path = Path("testing_video/demo1.mp4")
    data_path: Path = Path("data_files/")
    default_run_time: int = 10
    run_detections: bool = True
    show_video: bool = False
    queue_bus: Queue = Queue()
    data_queue: Queue = Queue()
