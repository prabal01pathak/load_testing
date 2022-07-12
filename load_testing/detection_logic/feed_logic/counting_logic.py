"""Module for counting objects
Author: Prabal Pathak
"""
import collections

import cv2
import numpy as np

from .settings import __APP_SETTINGS__


class CountingLogic:
    """counting logic class"""

    def __init__(self):

        # Bath
        self.ROI_LEFT = __APP_SETTINGS__.ROI_LEFT
        self.ROI_RIGHT = __APP_SETTINGS__.ROI_RIGHT
        self.ROI_UPPER = __APP_SETTINGS__.ROI_UPPER
        self.ROI_LOWER = __APP_SETTINGS__.ROI_LOWER

    def draw_lines(self, frame: np.ndarray) -> np.ndarray:
        """Drawing the Upper and Lower ROI lines on Frame

        Args:
             [ndarray]: Frame

        Returns:
             [ndarray]: Frame after drawing upper and lower ROI Lines
        """

        cv2.line(
            frame,
            (self.ROI_LEFT, self.ROI_UPPER),
            (self.ROI_RIGHT, self.ROI_UPPER),
            (0, 255, 0),
            1,
        )  # green roi
        cv2.line(
            frame,
            (self.ROI_LEFT, self.ROI_LOWER),
            (self.ROI_RIGHT, self.ROI_LOWER),
            (0, 255, 0),
            1,
        )  # blue roi

        cv2.line(
            frame,
            (self.ROI_LEFT, self.ROI_UPPER),
            (self.ROI_LEFT, self.ROI_LOWER),
            (0, 0, 255),
            1,
        )  # red roi
        cv2.line(
            frame,
            (self.ROI_RIGHT, self.ROI_UPPER),
            (self.ROI_RIGHT, self.ROI_LOWER),
            (0, 0, 255),
            1,
        )  # red roi

        return frame

    def count_bottles(
        self,
        frame: np.ndarray,
        rois: np.ndarray,
        total_bottles_count: int,
        bottle_threshold: int,
        prev_bottle: int,
        xcentroid_avg: list,
        bottle_index: list,
    ) -> dict:
        """_summary_

        Args:
            frame (_type_): _description_
            rois (_type_): _description_
            total_bottles_count (_type_): _description_
            bottle_threshold (_type_): _description_
            prev_bottle (_type_): _description_
            xcentroid_avg (_type_): _description_
            bottle_index (_type_): _description_

        Returns:
            _type_: _description_
        """
        bottles = 0
        func_thresh = collections.deque([False], maxlen=2)

        for roi in rois:
            # creating the centroid
            centroid = (int((roi[0] + roi[2]) / 2), int((roi[1] + roi[3]) / 2))
            # if centroid is inside the roi region
            if (
                (roi[4] == 0 or roi[4] == 1)
                and self.ROI_UPPER < centroid[1] < self.ROI_LOWER
                and self.ROI_LEFT < centroid[0] < self.ROI_RIGHT
            ):  # bottles
                bottles = bottles + 1
                xcentroid_avg.append(centroid[0])

        if bottles == 0:
            bottle_threshold = 0
            func_thresh.append(False)
            bottle_index.append(0)
        if bottles > 0:
            bottle_threshold = bottle_threshold + 1
            bottle_index.append(1)
            func_thresh.append(True)
        if bottle_threshold == 2:  # change
            total_bottles_count = total_bottles_count + bottles
            func_thresh.append(False)

        try:
            if (
                (xcentroid_avg[-1] - xcentroid_avg[-2] > 50)
                and bottle_index[-1] == 1
                and bottle_index[-2] == 1
                and bottles < 2
                and not func_thresh[0]
            ):
                total_bottles_count = total_bottles_count + bottles
                func_thresh.append(False)
            if (
                (xcentroid_avg[-1] - xcentroid_avg[-2] < -50)
                and bottle_index[-1] == 1
                and bottle_index[-2] == 1
                and bottles < 2
                and not func_thresh[0]
            ):
                total_bottles_count = total_bottles_count + bottles
                func_thresh.append(False)
        except Exception as _e:
            # print("Exception creating centroids: ", _e)
            pass

        # 4
        if bottle_threshold > 2 and (bottles >= prev_bottle) and not func_thresh[0]:
            total_bottles_count = total_bottles_count + (bottles - prev_bottle)
            func_thresh.append(False)
        prev_bottle = bottles
        frame = self.draw_lines(frame)
        analysis = total_bottles_count
        return (
            analysis,
            frame,
            rois,
            total_bottles_count,
            bottle_threshold,
            prev_bottle,
            xcentroid_avg,
            bottle_index,
        )
