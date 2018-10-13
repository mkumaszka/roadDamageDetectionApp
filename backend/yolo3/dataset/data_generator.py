import numpy as np
from PIL import Image
from imgaug import augmenters as iaa

from ..model.utils import rand


class BatchGenerator:

    def __init__(self, batch_size, input_shape, anchors, num_classes,
                 real_annotation_lines, is_training=True):
        self.batch_size = batch_size
        self.input_shape = input_shape
        self.anchors = anchors
        self.num_classes = num_classes
        self.real_annotation_lines = real_annotation_lines
        self.is_training = is_training

        sometimes = lambda aug: iaa.Sometimes(0.5, aug)
        self.aug_pipe = iaa.Sequential([iaa.SomeOf((0, 5),
                                                   [iaa.Sharpen(alpha=1.0, lightness=(0.75, 1.5)),
                                                    iaa.EdgeDetect(alpha=(0, 0.5)),
                                                    iaa.AdditiveGaussianNoise(loc=0, scale=(
                                                        0.0, 0.05 * 255)), iaa.OneOf(
                                                       [iaa.Dropout((0.01, 0.05)),
                                                        iaa.Salt((0.03, 0.15)), ]),
                                                    iaa.Add((-10, 10)), iaa.Multiply((0.5, 1.5)),
                                                    iaa.ContrastNormalization((0.5, 2.0)),
                                                    sometimes(iaa.ElasticTransformation(
                                                        alpha=(0.1, 2.0), sigma=0.25)), ],
                                                   random_order=True)], random_order=True)

    @property
    def __len__(self):
        return len(self.real_annotation_lines)

    def _data_generator(self):
        single_instance_counter = 0
        idx = 0
        while True:
            image_data = []
            box_data = []
            l_bound = idx * self.batch_size
            r_bound = (idx + 1) * self.batch_size

            if r_bound > len(self.real_annotation_lines):
                r_bound = len(self.real_annotation_lines)
                l_bound = r_bound - self.batch_size

            batch = self.real_annotation_lines[l_bound:r_bound]
            for train_instance in batch:
                if single_instance_counter == 0:
                    np.random.shuffle(self.real_annotation_lines)
                image, box = self.get_random_data(train_instance, self.input_shape,
                                                  random=self.is_training)
                image_data.append(image)
                box_data.append(box)
                single_instance_counter = (single_instance_counter + 1) % self.__len__
            image_data = np.array(image_data)
            box_data = np.array(box_data)
            y_true = preprocess_true_boxes(box_data, self.input_shape, self.anchors,
                                           self.num_classes)
            idx += 1
            yield [image_data, *y_true], np.zeros(self.batch_size)

    def data_generator_wrapper(self):
        return self._data_generator()

    def get_random_data(self, annotation_line, input_shape, random=True, max_boxes=20, jitter=.3, proc_img=True):
        """
        random preprocessing for real-time data augmentation
        """
        line = annotation_line.split("<>")
        image = Image.open(line[0])
        iw, ih = image.size
        h, w = input_shape
        box = np.array([np.array(list(map(float, box.split(',')))) for box in line[1:]])

        if not random:
            # resize image
            scale = min(w / iw, h / ih)
            nw = int(iw * scale)
            nh = int(ih * scale)
            dx = (w - nw) // 2
            dy = (h - nh) // 2
            image_data = 0
            if proc_img:
                image = image.resize((nw, nh), Image.BICUBIC)
                new_image = Image.new('RGB', (w, h), (128, 128, 128))
                new_image.paste(image, (dx, dy))
                image_data = np.array(new_image) / 255.

            # correct boxes
            box_data = np.zeros((max_boxes, 5))
            if len(box) > 0:
                np.random.shuffle(box)
                if len(box) > max_boxes:
                    box = box[:max_boxes]
                box[:, [0, 2]] = box[:, [0, 2]] * scale + dx
                box[:, [1, 3]] = box[:, [1, 3]] * scale + dy
                box_data[:len(box)] = box

            return image_data, box_data

        # resize image
        new_ar = w / h * rand(1 - jitter, 1 + jitter) / rand(1 - jitter, 1 + jitter)
        scale = rand(.25, 2)
        if new_ar < 1:
            nh = int(scale * h)
            nw = int(nh * new_ar)
        else:
            nw = int(scale * w)
            nh = int(nw / new_ar)
        image = image.resize((nw, nh), Image.BICUBIC)

        # place image
        dx = int(rand(0, w - nw))
        dy = int(rand(0, h - nh))
        new_image = Image.new('RGB', (w, h), (128, 128, 128))
        new_image.paste(image, (dx, dy))
        image = new_image

        # flip image or not
        flip = rand() < .5
        if flip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        # # distort image
        # hue = rand(-hue, hue)
        # sat = rand(1, sat) if rand()<.5 else 1/rand(1, sat)
        # val = rand(1, val) if rand()<.5 else 1/rand(1, val)
        # x = rgb_to_hsv(np.array(image)/255.)
        # x[..., 0] += hue
        # x[..., 0][x[..., 0]>1] -= 1
        # x[..., 0][x[..., 0]<0] += 1
        # x[..., 1] *= sat
        # x[..., 2] *= val
        # x[x>1] = 1
        # x[x<0] = 0
        # image_data = hsv_to_rgb(x)  # numpy array, 0 to 1

        image = self.aug_pipe.augment_image(np.array(image) / 255.)

        # correct boxes
        box_data = np.zeros((max_boxes, 5))
        if len(box) > 0:
            np.random.shuffle(box)
            box[:, [0, 2]] = box[:, [0, 2]] * nw / iw + dx
            box[:, [1, 3]] = box[:, [1, 3]] * nh / ih + dy
            if flip: box[:, [0, 2]] = w - box[:, [2, 0]]
            box[:, 0:2][box[:, 0:2] < 0] = 0
            box[:, 2][box[:, 2] > w] = w
            box[:, 3][box[:, 3] > h] = h
            box_w = box[:, 2] - box[:, 0]
            box_h = box[:, 3] - box[:, 1]
            box = box[np.logical_and(box_w > 1, box_h > 1)]  # discard invalid box
            if len(box) > max_boxes:
                box = box[:max_boxes]
            box_data[:len(box)] = box

        return image, box_data


def preprocess_true_boxes(true_boxes, input_shape, anchors, num_classes):
    '''Preprocess true boxes to training input format

    Parameters
    ----------
    true_boxes: array, shape=(m, T, 5)
        Absolute x_min, y_min, x_max, y_max, class_id relative to input_shape.
    input_shape: array-like, hw, multiples of 32
    anchors: array, shape=(N, 2), wh
    num_classes: integer

    Returns
    -------
    y_true: list of array, shape like yolo_outputs, xywh are reletive value

    '''
    assert (true_boxes[..., 4]<num_classes).all(), 'class id must be less than num_classes'
    num_layers = len(anchors)//3 # default setting
    anchor_mask = [[6,7,8], [3,4,5], [0,1,2]] if num_layers==3 else [[3,4,5], [1,2,3]]

    true_boxes = np.array(true_boxes, dtype='float32')
    input_shape = np.array(input_shape, dtype='int32')
    boxes_xy = (true_boxes[..., 0:2] + true_boxes[..., 2:4]) // 2
    boxes_wh = true_boxes[..., 2:4] - true_boxes[..., 0:2]
    true_boxes[..., 0:2] = boxes_xy/input_shape[::-1]
    true_boxes[..., 2:4] = boxes_wh/input_shape[::-1]

    m = true_boxes.shape[0]
    grid_shapes = [input_shape//{0:32, 1:16, 2:8}[l] for l in range(num_layers)]
    y_true = [np.zeros((m,grid_shapes[l][0],grid_shapes[l][1],len(anchor_mask[l]),5+num_classes),
        dtype='float32') for l in range(num_layers)]

    # Expand dim to apply broadcasting.
    anchors = np.expand_dims(anchors, 0)
    anchor_maxes = anchors / 2.
    anchor_mins = -anchor_maxes
    valid_mask = boxes_wh[..., 0]>0

    for b in range(m):
        # Discard zero rows.
        wh = boxes_wh[b, valid_mask[b]]
        if len(wh)==0: continue
        # Expand dim to apply broadcasting.
        wh = np.expand_dims(wh, -2)
        box_maxes = wh / 2.
        box_mins = -box_maxes

        intersect_mins = np.maximum(box_mins, anchor_mins)
        intersect_maxes = np.minimum(box_maxes, anchor_maxes)
        intersect_wh = np.maximum(intersect_maxes - intersect_mins, 0.)
        intersect_area = intersect_wh[..., 0] * intersect_wh[..., 1]
        box_area = wh[..., 0] * wh[..., 1]
        anchor_area = anchors[..., 0] * anchors[..., 1]
        iou = intersect_area / (box_area + anchor_area - intersect_area)

        # Find best anchor for each true box
        best_anchor = np.argmax(iou, axis=-1)

        for t, n in enumerate(best_anchor):
            for l in range(num_layers):
                if n in anchor_mask[l]:
                    i = np.floor(true_boxes[b,t,0]*grid_shapes[l][1]).astype('int32')
                    j = np.floor(true_boxes[b,t,1]*grid_shapes[l][0]).astype('int32')
                    k = anchor_mask[l].index(n)
                    c = true_boxes[b,t, 4].astype('int32')
                    y_true[l][b, j, i, k, 0:4] = true_boxes[b,t, 0:4]
                    y_true[l][b, j, i, k, 4] = 1
                    y_true[l][b, j, i, k, 5+c] = 1

    return y_true