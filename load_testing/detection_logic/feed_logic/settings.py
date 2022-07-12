"""Settings file for detection module
Author: Prabal Pathak
"""
from easydict import EasyDict as edict

__APP_SETTINGS__ = edict()
__APP_SETTINGS__.GAIN = 16.0
__APP_SETTINGS__.EXPOSURE_TIME = 5000
__APP_SETTINGS__.CAMERA_NAME = "camLeft"


__APP_SETTINGS__.ROI_LEFT = 0  # 600
__APP_SETTINGS__.ROI_RIGHT = 800  # 650
__APP_SETTINGS__.ROI_UPPER = 250  # 250
__APP_SETTINGS__.ROI_LOWER = 300  # 300
__APP_SETTINGS__.GAP_THRESHOLD = 200  # 300


__APP_SETTINGS__.IP = "127.0.0.1"
__APP_SETTINGS__.MODEL_PATH = "v3"