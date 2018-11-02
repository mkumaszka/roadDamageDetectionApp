import os
import xml.etree.ElementTree as ET

from PIL import Image
from tqdm import tqdm
import numpy as np

from ..metrics.object_detection import calculate_precision_recall, \
    calculate_precision_recall_classification_separate_classes, calculate_precision_recall_classification
from ...prediction.road_prediction import detect_tables_image, load_yolo_model

TEST_DIR = r'C:\Users\Martyna\Desktop\Studia\INZ\dane\RoadDamageDataset\val'
ANNO_PATH = os.path.join(TEST_DIR, 'anno')
IMG_PATH = os.path.join(TEST_DIR, 'img')
VISUALIZE = True
classes = ["D00", "D01", "D10", "D11", "D20", "D40", "D43", "D44"]


def parse_annotation(anno_path):
    tree = ET.parse(anno_path)
    root = tree.getroot()
    boxes = []
    labels = []
    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls not in classes:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('xmax').text), float(xmlbox.find('ymax').text))
        boxes.append(b)
        labels.append(cls_id)
    return boxes, labels


def pred_single_image(img_path, yolo, vizualize=VISUALIZE):
    image = Image.open(img_path)
    out_path = img_path.replace('.jpg', '-pred.jpg')
    predictions = detect_tables_image(image, yolo, path_to_save=out_path, visualize=vizualize)
    if len(predictions[0]) is 0:
        return [], [], []
    return predictions


def evaluate_set():
    yolo = load_yolo_model()
    prec = 0
    rec = 0
    counter = 0
    results_dict = {damage_class: [] for damage_class in classes}
    for filename in tqdm(os.listdir(ANNO_PATH)):
        img_path = os.path.join(IMG_PATH, filename)
        img_path = img_path.replace('.xml', '.jpg')
        anno_path = os.path.join(ANNO_PATH, filename)
        true_objects = parse_annotation(anno_path)
        pred_objects = pred_single_image(img_path, yolo)
        # precision, recall = calculate_precision_recall_classification(true_objects, pred_objects, classes)
        precision, recall = calculate_precision_recall(true_objects, pred_objects)
        calculate_precision_recall_classification_separate_classes(true_objects, pred_objects, classes, results_dict)
        if precision is not None:
            prec += precision
            rec += recall
        counter += 1
    print('Avg prec: {}'.format(prec/counter))
    print('Avg rec: {}'.format(rec/counter))

    for d_class, value in results_dict.items():
        precision = [prec for prec, recall in value]
        recall = [recall for prec, recall in value]
        avg_prec = np.mean(precision)
        avg_recall = np.mean(recall)
        print('------ {} ------'.format(d_class))
        print('Avg precision: {}'.format(avg_prec))
        print('Avg recall: {}'.format(avg_recall))
