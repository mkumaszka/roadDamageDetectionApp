import io

import os
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .files import save_binary, hash_file
from ..settings import IMAGES_ROOT, MEDIA_ROOT


def open_image(bytes_arr):
    return Image.open(io.BytesIO(bytes_arr))


def image_to_byte_array(image_path):
    img = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def save_uploaded_photo_as_binary_array(photo):
    photo_path = default_storage.save(photo.name, ContentFile(photo.read()))
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
