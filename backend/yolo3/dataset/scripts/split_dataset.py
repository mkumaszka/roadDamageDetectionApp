import os

import xml.etree.ElementTree as ET
import numpy as np
import shutil

damage_types = ["D00", "D01", "D10", "D11", "D20", "D40", "D43", "D44"]
damage_weights = [0.14, 0.19, 0.03, 0.03, 0.12, 0.02, 0.03, 0.19]

zipped_damages = list(zip(damage_types, damage_weights))
zipped_damages.sort(key=lambda x: x[1])
# govs corresponds to municipality name.
govs = ["Adachi", "Chiba", "Ichihara", "Muroran", "Nagakute", "Numazu", "Sumida"]

data_path = "C:\\Users\\Martyna\\Desktop\\Studia\\INZ\\dane\\RoadDamageDataset\\"
annos = "\\Annotations\\"
images = "\\JPEGImages\\"

dir_anno_test = data_path + 'test\\anno\\'
dir_imgs_test = data_path + 'test\\img\\'
dir_anno_train = data_path + 'train\\anno\\'
dir_imgs_train = data_path + 'train\\img\\'

if not os.path.exists(dir_anno_train):
    os.makedirs(dir_anno_train)

if not os.path.exists(dir_anno_test):
    os.makedirs(dir_anno_test)

if not os.path.exists(dir_imgs_train):
    os.makedirs(dir_imgs_train)

if not os.path.exists(dir_imgs_test):
    os.makedirs(dir_imgs_test)


annos_labels_dict = dict()
percent_val = 0.2
seed = 1
rng = np.random.RandomState(seed)

# for gov in govs:
#     file_list = os.listdir(data_path + gov + annos)
#     for file in file_list:
#         if file == '.DS_Store' or '._' in file:
#             continue
#         else:
#             with open(data_path + gov + annos + file) as infile_xml:
#                 tree = ET.parse(infile_xml)
#                 root = tree.getroot()
#                 for obj in root.iter('object'):
#                     cls_name = obj.find('name').text
#                     if cls_name not in annos_labels_dict:
#                         annos_labels_dict[cls_name] = [infile_xml.name]
#                     else:
#                         annos_labels_dict[cls_name].append(infile_xml.name)

for gov in govs:
    file_list = os.listdir(data_path + gov + annos)
    for file in file_list:
        if file == '.DS_Store' or '._' in file:
            continue
        else:
            file = data_path + gov + annos + file
            dir_source_a = file
            dir_source_im = file.replace('.xml', '.jpg')
            dir_source_im = dir_source_im.replace('Annotations', 'JPEGImages')
            anno_filename = dir_source_a.split("\\")[-1]
            img_filename = dir_source_im.split("\\")[-1]
            if np.random.rand() < percent_val:
                dir_dest_a = os.path.join(dir_anno_test, anno_filename)
                dir_dest_im = os.path.join(dir_imgs_test, img_filename)
            else:
                dir_dest_a = os.path.join(dir_anno_train, anno_filename)
                dir_dest_im = os.path.join(dir_imgs_train, img_filename)
            # if (not os.path.exists(os.path.join(dir_anno_test, anno_filename)) and not
            #         os.path.exists(os.path.join(dir_anno_train, anno_filename))):
            shutil.copy(dir_source_a, dir_dest_a)
            shutil.copy(dir_source_im, dir_dest_im)
                # added_files += 1

