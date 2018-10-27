import hashlib
import os

import filetype

from ..settings import MEDIA_ROOT


def save_binary(filename, binary):
    with open(filename, "wb") as file:
        file.write(binary)


def hash_file(readed_file):
    md5hash = hashlib.md5(readed_file)
    return md5hash.hexdigest()


def check_file_extension(file_path):
    path = os.path.join(MEDIA_ROOT, file_path)
    kind = filetype.guess(path)
    kind = kind.mime
    if 'image' in kind:
        return 'image'
    if 'video' in kind:
        return 'video'
    return 'other_type'
