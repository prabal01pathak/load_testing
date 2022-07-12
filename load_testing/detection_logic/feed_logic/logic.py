import cv2
from loguru import logger
from statistics import mean
from .settings import __APP_SETTINGS__


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

        cv2.line(frame, (self.ROI_LEFT, self.ROI_UPPER),
                 (self.ROI_RIGHT, self.ROI_UPPER), (0, 255, 0), 1)  # green roi
        cv2.line(frame, (self.ROI_LEFT, self.ROI_LOWER),
                 (self.ROI_RIGHT, self.ROI_LOWER), (0, 255, 0), 1)  # blue roi

        cv2.line(frame, (self.ROI_LEFT, self.ROI_UPPER),
                 (self.ROI_LEFT, self.ROI_LOWER), (0, 0, 255), 1)  # red roi
        cv2.line(frame, (self.ROI_RIGHT, self.ROI_UPPER),
                 (self.ROI_RIGHT, self.ROI_LOWER), (0, 0, 255), 1)  # red roi

        return frame

    # @jit(forceobj=True)
    def count_bottles(self, frame, rois, total_bottles_count, bottle_threshold, prev_bottle, centroid_avg, bottle_index):
        # rois = [[xmin, ymin, xmax, ymax, class_id]]

        bottles = 0
        # centroid_list = []
        # centroid_avg = collections.deque([0],maxlen=3)

        for roi in rois:

            # creating the centroid
            centroid = (int((roi[0] + roi[2]) / 2), int((roi[1] + roi[3]) / 2))
            # if centroid is inside the roi region
            if (roi[4] == 0 or roi[4] == 1) and self.ROI_UPPER < centroid[1] < self.ROI_LOWER and self.ROI_LEFT < centroid[0] < self.ROI_RIGHT:  # bottles
                # print("centroid ",centroid[1])
                # centroid_list.append(centroid[1])
                bottles = bottles+1
                centroid_avg.append(centroid[0])

    # 1
        if bottles == 0:
            bottle_threshold = 0
            bottle_index.append(0)
            # print("#1 bottle_threshold", bottle_threshold)
    # 2
        # if bottle_threshold>1 and prev_bottle>=2:
        #     bottle_threshold=0
        #     print("#2 bottle_threshold, prev_bottle", bottle_threshold, prev_bottle)
    # 3
        if bottles > 0:
            bottle_threshold = bottle_threshold + 1
            bottle_index.append(1)
            # print("#3 bottle_threshold", bottle_threshold)
    # 4
        if bottle_threshold == 1:  # change
            total_bottles_count = total_bottles_count + bottles
            # prev_bottle = bottles
            # print("#4 total_bottles_count, bottles, prev_bottle",total_bottles_count, bottles, prev_bottle)
    # 5
        if bottle_threshold > 1 and (bottles >= prev_bottle):
            total_bottles_count = total_bottles_count + (bottles-prev_bottle)
            # print("#5 bottle_threshold,prev_bottle,bottles", bottle_threshold,prev_bottle,bottles)
        gap_threashold = __APP_SETTINGS__.GAP_THRESHOLD
        try:
            if (centroid_avg[-1] - centroid_avg[-2] > gap_threashold) and bottle_index[-1] == 1 and bottle_index[-2] == 1 and bottles < 2:
                total_bottles_count = total_bottles_count + 1
                print("Bottle on left side")
            if (centroid_avg[-1] - centroid_avg[-2] < -gap_threashold) and bottle_index[-1] == 1 and bottle_index[-2] == 1 and bottles < 2:
                total_bottles_count = total_bottles_count + 1
                print("Bottle on right side")
        except:
            pass

        # print('====================centroid_avg', centroid_avg)
        # print('====================bottle_index', bottle_index)
        # print("====================================Moving Average",mean(centroid_avg))
        prev_bottle = bottles
        frame = self.draw_lines(frame)
        analysis = total_bottles_count

        return analysis, frame, rois, total_bottles_count, bottle_threshold, prev_bottle, centroid_avg, bottle_index
