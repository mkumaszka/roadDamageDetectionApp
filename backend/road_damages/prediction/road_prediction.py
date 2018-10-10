import numpy as np

from ..yolo3.model.yolo import YOLO
from ..settings import ANCHORS_PATH, CLASSES_PATH, MODEL_PATH


def load_yolo_model(model_path=MODEL_PATH, anchors_path=ANCHORS_PATH, classes_path=CLASSES_PATH, score=0.3, iou=0.45):
    """
    Loads saved yolo model.
    """
    kwargs = {"model_path": model_path,
              "anchors_path": anchors_path,
              "classes_path": classes_path,
              "score": score,
              "iou": iou}
    return YOLO(**kwargs)


def detect_tables_image(image):
    yolo = load_yolo_model()
    out_boxes, out_scores, out_classes = yolo.detect_image_boxes(image)
    out_boxes = [get_true_box(box, image) for box in out_boxes]
    return out_boxes, out_scores, out_classes


def get_true_box(box, image):
    top, left, bottom, right = box
    top = max(0, np.floor(top + 0.5).astype('int32'))
    left = max(0, np.floor(left + 0.5).astype('int32'))
    bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
    right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
    return left, right, top, bottom

