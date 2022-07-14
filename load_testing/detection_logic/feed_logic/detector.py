"""
Description: Detection logic module
"""
import os
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "3"

import tensorflow as tf
from tensorflow.compat.v1 import InteractiveSession
from tensorflow.compat.v1 import ConfigProto
from tensorflow.python.saved_model import tag_constants
import numpy as np
import cv2

from .settings import __APP_SETTINGS__

physical_devices = tf.config.experimental.list_physical_devices("GPU")
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

# Fweights = 'feed_logic/yolo_model_updated/v3'
# Fclasses = 'feed_logic/yolo_model/data/classes/towel.names'
home_path = os.getcwd()
Fweights = Path(
    f"load_testing/detection_logic/feed_logic/yolo_model_updated/{__APP_SETTINGS__.MODEL_PATH}",
)

# Flags
Ftiny = True
Fmodel = "yolov4"
Fsize = 416
Fiou = 0.50


config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(
#     Ftiny, Fmodel, Fclasses)
saved_model_loaded = tf.saved_model.load(Fweights, tags=[tag_constants.SERVING])
infer = saved_model_loaded.signatures["serving_default"]


def format_boxes(boxes, height, width):
    """Returns formated list of normalised coordinates for auto_annotator

    Args:
        boxes ([list]): List of coordinates with detection scores
        height (int): Height of the image
        width (int): Width of the image

    Returns:
        [list[list]]: list of lists of coordinates
                      Format of roi = [xmin,ymin,xmax,ymax,classid]
    """
    # out_boxes -> coordinates
    # out_scores -> scores
    # out_classes -> classes
    # num_boxes -> number of predictions
    out_boxes, _, out_classes, num_boxes = list(boxes)
    rois = []

    for itr in range(num_boxes[0]):
        xmin = int(out_boxes[0][itr][1] * width)
        ymin = int(out_boxes[0][itr][0] * height)
        xmax = int(out_boxes[0][itr][3] * width)
        ymax = int(out_boxes[0][itr][2] * height)
        class_id = int(out_classes[0][itr])
        rois.append([xmin, ymin, xmax, ymax, class_id])
    return rois


def detect(frame, threshold=0.20):
    """Returns formated list of coordinates

    Args:
        frame ([ndarray]):image
        threshold (float): Minimum score value to be considered. Defaults to 0.35.

    Returns:
        [list[list]]: list of lists of coordinates
                      Format of roi = [xmin,ymin,xmax,ymax,classid]
    """

    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_data = cv2.resize(frame, (Fsize, Fsize))
    image_data = image_data / 255.0

    images_data = []
    images_data.append(image_data)
    images_data = np.asarray(images_data).astype(np.float32)

    batch_data = tf.constant(images_data)

    pred_bbox: dict = infer(batch_data)

    for value in pred_bbox.values():
        boxes = value[:, :, 0:4]
        pred_conf = value[:, :, 4:]
    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])
        ),
        max_output_size_per_class=100,
        max_total_size=100,
        iou_threshold=Fiou,
        score_threshold=threshold,
    )

    pred_bbox = [
        boxes.numpy(),
        scores.numpy(),
        classes.numpy(),
        valid_detections.numpy(),
    ]
    height, width, _ = frame.shape
    rois = format_boxes(pred_bbox, height, width)
    return rois
