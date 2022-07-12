import cv2
from loguru import logger
from statistics import mean
from .settings import __APP_SETTINGS__
import collections
from loguru import logger
from numba import jit


class CountingLogic():
    def __init__(self):

        # Bath
        self.ROI_LEFT = __APP_SETTINGS__.ROI_LEFT
        self.ROI_RIGHT = __APP_SETTINGS__.ROI_RIGHT
        self.ROI_UPPER = __APP_SETTINGS__.ROI_UPPER
        self.ROI_LOWER = __APP_SETTINGS__.ROI_LOWER

    def draw_lines(self, frame):
        """ Drawing the Upper and Lower ROI lines on Frame

        Args:
             [ndarray]: Frame 

        Returns:
             [ndarray]: Frame after drawing upper and lower ROI Lines
        """

        cv2.line(frame, (self.ROI_LEFT, 250),
                 (self.ROI_RIGHT, 250), (0, 255, 0), 1)  # green roi

        cv2.line(frame, (self.ROI_LEFT, self.ROI_UPPER),
                 (self.ROI_LEFT, self.ROI_LOWER), (0, 0, 255), 1)  # red roi
        cv2.line(frame, (self.ROI_RIGHT, self.ROI_UPPER),
                 (self.ROI_RIGHT, self.ROI_LOWER), (0, 0, 255), 1)  # red roi


        return frame

    @jit(forceobj=True)
    def count_bottles(self, frame, rois, total_bottles_count, bottle_threshold, prev_bottle, Xcentroid_avg, Ycentroid_avg, bottle_index, frame_number):
        # rois = [[xmin, ymin, xmax, ymax, class_id]]

        bottles = 0
        Xcor = []
        Ycor = []

        for roi in rois:

            # creating the centroid
            centroid = (int((roi[0] + roi[2]) / 2), int((roi[1] + roi[3]) / 2))
            # if centroid is inside the roi region
            if (roi[4] == 0 or roi[4] == 1) and self.ROI_UPPER < centroid[1] < self.ROI_LOWER and self.ROI_LEFT < centroid[0] < self.ROI_RIGHT:  # bottles
                diff = centroid[1] - 250
                if 0 <= diff <= __APP_SETTINGS__.GAP_THRESHOLD:
                    bottles = bottles+1
                    Xcentroid_avg.append(centroid[0])
                    Ycentroid_avg.append(centroid[1])
                    # Xcor.append(centroid[0])
                    # Ycor.append(centroid[1])
                    #print("=========== Frame No", frame_number)

    
        logger.debug(f"========================= frame no {bottle_threshold} threshold hit bottles {prev_bottle}")            
        logger.debug(f"========================= frame no {frame_number} threshold hit bottles {bottles}")

        #1
        if bottles > 0 and prev_bottle != bottles and prev_bottle < bottles:
            total_bottles_count = total_bottles_count + bottles
            logger.debug("#1 logic hit")
        #2
        if bottles >= 1 and (frame_number > bottle_threshold) and 0 < prev_bottle < bottles:
            total_bottles_count = total_bottles_count - prev_bottle
            logger.debug("#2 logic hit")
        #3
        if bottles == 1 and prev_bottle == bottles and (-150 <= Xcentroid_avg[-2] - Xcentroid_avg[-1] <= 150) and (Ycentroid_avg[-2] - Ycentroid_avg[-1] <= 5):
            total_bottles_count = total_bottles_count + 1
            #print("#3 logic hit")

        logger.debug(f'====================Xcor {Xcor}')
        logger.debug(f'====================Ycor {Ycor}')
        logger.debug(f'====================Xcentroid_avg {Xcentroid_avg}')
        logger.debug(f'====================Ycentroid_avg {Ycentroid_avg}')
        
        bottle_threshold = frame_number
        prev_bottle = bottles
        frame = self.draw_lines(frame)
        analysis = total_bottles_count

        return analysis, frame, rois, total_bottles_count, bottle_threshold, prev_bottle, Xcentroid_avg, Ycentroid_avg, bottle_index, frame_number
