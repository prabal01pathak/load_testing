"""
test detection logic
"""
import cv2


from load_testing.detection_logic.feed_logic.saved_driver import Worker


VIDEO_PATH = "testing_video/demo1.mp4"
cap = cv2.VideoCapture(VIDEO_PATH)
DETECTION_WORKER = Worker()


def test_detect():
    """test Worker.detect function"""
    _, frame = cap.read()
    detection_details = DETECTION_WORKER.detect(frame=frame)
    assert isinstance(detection_details, dict) is True
