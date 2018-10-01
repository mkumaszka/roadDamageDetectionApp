import numpy as np

from yolo3.yolo import YOLO


def load_yolo_model(model_path, anchors_path, classes_path, score=0.3, iou=0.45):
    """
    Loads saved yolo model.
    """
    kwargs = {"model_path": model_path,
              "anchors_path": anchors_path,
              "classes_path": classes_path,
              "score": score,
              "iou": iou}
    return YOLO(**kwargs)


def detect_tables_image(image, yolo):
    tables = {}
    out_boxes, out_scores, out_classes = yolo.detect_image_boxes(image)
    page_size = [image.size[1], image.size[0]]
    out_boxes = [get_true_box(box, image) for box in out_boxes]
    # tables[k] = out_boxes, page_size
    return out_boxes


def get_true_box(box, image):
    top, left, bottom, right = box
    top = max(0, np.floor(top + 0.5).astype('int32'))
    left = max(0, np.floor(left + 0.5).astype('int32'))
    bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
    right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
    return left, right, top, bottom

