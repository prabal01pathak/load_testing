#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: Read video file and yield it
Author: Prabal Pathak
"""

from typing import Iterable
from pathlib import Path
from dataclasses import dataclass

import cv2


@dataclass
class ReadVideo:
    """Read video stream"""

    def __init__(self, video_path_main: Path, **kwargs) -> None:
        self.video_path = video_path_main
        self.cap = None
        self.kwargs = kwargs

    def read(self):
        """read video"""
        self.cap = cv2.VideoCapture(self.video_path)

    def agument_video(self) -> Iterable[list]:
        """Read and agument images"""
        # print(self.kwargs)
        while True:
            try:
                _, frame = self.cap.read()
                # print(
                #     f"Showing for Frame{self.kwargs.get('process_number')}{self.kwargs.get('thread_number')}"
                # )
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.cap.release()
                    break
                yield frame
            except cv2.error as _e:
                print(_e)


def main():
    """Main function to run the ReadVideo class"""
    video_path = "testing_video/demo1.mp4"
    read_video = ReadVideo(video_path_main=video_path)
    read_video.read()
    for frame in read_video.agument_video():
        cv2.imshow("frame", frame)
        # print(frame)


if __name__ == "__main__":
    main()
