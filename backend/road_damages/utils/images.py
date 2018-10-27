import io

import os
import cv2
from PIL import Image

from .files import save_binary, hash_file
from ..settings import IMAGES_ROOT, MEDIA_ROOT


def open_image(bytes_arr):
    return Image.open(io.BytesIO(bytes_arr))


def image_to_byte_array(image_path):
    img = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def save_uploaded_photo_as_binary_array(photo_path):
    curr_dir = os.getcwd()
    path = os.path.join(MEDIA_ROOT, photo_path)
    image_byte_array = image_to_byte_array(path)
    filename = hash_file(image_byte_array)
    filename = filename + '.png'
    path_to_save = os.path.join(IMAGES_ROOT, filename)
    save_binary(path_to_save, image_byte_array)
    path_to_remove = os.path.join(curr_dir, path)
    os.remove(path_to_remove)
    return filename


def extract_images(video_path, fps=1):
    count = 0
    video_path = os.path.join(MEDIA_ROOT, video_path)
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    success = True
    extracted_images = []
    while success:
        success, image = vidcap.read()
        print('Read a new frame: ', success)
        if success:
            photo_name = "frame%d.jpg" % count
            cv2.imwrite(MEDIA_ROOT + photo_name, image)  # save frame as JPEG file
            count = count + fps
            filename = save_uploaded_photo_as_binary_array(photo_name)
            extracted_images.append(filename)
    os.remove(video_path)
    return extracted_images
