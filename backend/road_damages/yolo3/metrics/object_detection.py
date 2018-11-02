from operator import itemgetter

import numpy as np

from ..utils.boxes import correct_boxes
from .similarity import inner_area_similarity_from_boxes


def calculate_precision_recall(true_objects,
                               pred_objects,
                               detection_threshold=0.5):

    pred_boxes, _, _ = pred_objects
    true_boxes, _ = true_objects

    pred_boxes = correct_boxes(pred_boxes)

    found_regions = set()
    true_positives, false_negatives = 0, 0
    for region in true_boxes:
        possible_regions = (
            (b, inner_area_similarity_from_boxes(region, b))
            for b in pred_boxes if b not in found_regions)
        found_region, similarity = max(possible_regions, key=itemgetter(1), default=(None, -1))
        if detection_threshold < similarity:
            true_positives += 1
            found_regions.add(found_region)
        else:
            false_negatives += 1

    if not true_positives:
        return 0, 0

    false_positives = len(set(pred_boxes) - found_regions)

    return (true_positives / (true_positives + false_positives)), \
           (true_positives / (true_positives + false_negatives))


def calculate_precision_recall_classification(true_objects,
                                              pred_objects,
                                              classes,
                                              detection_threshold=0.5):

    pred_boxes, pred_scores, pred_labels = pred_objects
    true_boxes, labels = true_objects

    pred_boxes = correct_boxes(pred_boxes)

    pred_labels_boxes = list(zip(pred_labels, pred_boxes))
    true_objects = zip(true_boxes, labels)
    true_objects = [(b, l) for b, l in true_objects if l in classes]
    if not true_objects:
        return None, None
    found_regions = set()
    true_positives, false_negatives = 0, 0
    for true_box, true_label in true_objects:
        possible_regions = (
            (b, inner_area_similarity_from_boxes(true_box, b))
            for l, b in pred_labels_boxes if b not in found_regions and l == true_label)
        found_region, similarity = max(possible_regions, key=itemgetter(1), default=(None, -1))
        if detection_threshold < similarity:
            true_positives += 1
            found_regions.add(found_region)
        else:
            false_negatives += 1

    if not true_positives:
        return 0, 0

    false_positives = len(set(pred_boxes) - found_regions)

    return (true_positives / (true_positives + false_positives)), \
           (true_positives / (true_positives + false_negatives))


def calculate_precision_recall_classification_separate_classes(true_objects,
                                                               pred_objects,
                                                               classes,
                                                               results_dict,
                                                               detection_threshold=0.5):

    for i, damage_class in enumerate(classes):
        precision, recall = calculate_precision_recall_classification(true_objects, pred_objects, [i])
        if precision is not None and recall is not None:
            results_dict[damage_class].append((precision, recall))

