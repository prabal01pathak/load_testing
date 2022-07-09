#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: Read video file and yield it
Author: Prabal Pathak
"""

from typing import Iterable
from pathlib import Path
import cv2


class ReadVideo:
    """Read video stream"""

    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path
        self.cap = None

    def read(self):
        """read video"""
        self.cap = cv2.VideoCapture(self.video_path)

    def agument_video(self) -> Iterable[list]:
        """Read and agument images"""
        while True:
            try:
                _, frame = self.cap.read()
                if cv2.waitKey("q" | 1):
                    break
                yield frame
            except cv2.error as _e:
                print(_e)
