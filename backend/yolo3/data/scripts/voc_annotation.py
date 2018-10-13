import xml.etree.ElementTree as ET
import os


classes = ["D00", "D01", "D10", "D11", "D20", "D40", "D43", "D44"]
ANNO_PATH = r'C:\Users\Martyna\Desktop\Studia\INZ\dane\RoadDamageDataset\test\anno'
IMG_PATH = r'C:\Users\Martyna\Desktop\Studia\INZ\dane\RoadDamageDataset\test\img'
list_file_dir = r'C:\Users\Martyna\Desktop\Studia\INZ\dane\RoadDamageDataset'
list_file_name = 'test_annotations.txt'


def convert_annotation(in_file, list_file):
    saved_obj = False
    anno_filename = os.path.join(ANNO_PATH, in_file)
    img_filename = os.path.join(IMG_PATH, in_file).replace('.xml', '.jpg')
    tree = ET.parse(anno_filename)
    root = tree.getroot()
    out_str = img_filename
    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls not in classes:
            continue
        saved_obj = True
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('xmax').text), float(xmlbox.find('ymax').text))
        out_str += ("<>" + ",".join([str(a) for a in b]) + ',' + str(cls_id))
    if saved_obj:
        list_file.write(out_str)
        list_file.write('\n')


list_file = open(os.path.join(list_file_dir, list_file_name), 'w')
for filename in os.listdir(ANNO_PATH):
    convert_annotation(filename, list_file)
list_file.close()

