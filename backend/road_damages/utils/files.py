import hashlib


def save_binary(filename, binary):
    with open(filename, "wb") as file:
        file.write(binary)


def hash_file(readed_file):
    md5hash = hashlib.md5(readed_file)
    return md5hash.hexdigest()

