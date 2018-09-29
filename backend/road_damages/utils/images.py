import io

from PIL import Image


def open_image(bytes_arr):
    return Image.open(io.BytesIO(bytes_arr))


def image_to_byte_array(image_path):
    img = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
