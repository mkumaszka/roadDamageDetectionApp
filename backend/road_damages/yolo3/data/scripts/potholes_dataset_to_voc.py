import os
from itertools import zip_longest

IMG_DIR = r'C:\Users\Martyna\Desktop\Studia\INZ\dane\Subset 2 (Complex)\TrainData'
ANNO_FILE_PATH = r'C:\Users\Martyna\Desktop\Studia\INZ\dane\Subset 2 (Complex)\complexTrainFullSizeAllPotholes.txt'


def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)


def convert_anno(IMG_DIR, ANNO_FILE_PATH):
    list_file = open(ANNO_FILE_PATH.replace('.txt', '-mod.txt'), 'w')
    with open(ANNO_FILE_PATH) as f:
        content = f.readlines()
        for single_c in content:
            stripped = single_c.split(' ')
            out_str = os.path.join(IMG_DIR, stripped[2].split('\\')[1])
            for bbox in list(grouper(4, stripped[4:])):
                x, y, w, h = bbox
                x = float(x)
                y = float(y)
                w = float(w)
                h = float(h)
                b = (x, y, x+w, y+h)
                out_str += ("<>" + ",".join([str(a) for a in b]) + ',' + str(0))
            list_file.write(out_str)
            list_file.write('\n')
    list_file.close()


convert_anno(IMG_DIR, ANNO_FILE_PATH)
