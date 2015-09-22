__author__ = 'n3k'

import random
import string
import hashlib
import os

class Utils(object):

    @staticmethod
    def get_file_size(fileobject):
        fileobject.seek(0, 2)
        size = fileobject.tell()
        fileobject.seek(0, 0)
        return size

    @staticmethod
    def as_hex(data):
        return "".join(["{:02x}:".format(ord(c)) for c in data])

    @staticmethod
    def get_random_name(size):
        return ''.join(random.choice(string.letters + string.digits) for _ in range(size))

    @staticmethod
    def get_random_unicode_name(size):
        return "".join([unichr(random.choice((0x300, 0x2000)) + random.randint(0, 0xff)) for _ in range(size)])

    @staticmethod
    def get_hashes_of_files(file_list):
        """
        This method calculates the md5 checksum of every CFFILE
        :return: {"filename": checksum, ...}
        """
        result = {}
        for filename in file_list:
            with open(filename, "rb") as f:
                result[os.path.basename(filename)] = hashlib.md5(f.read()).hexdigest()
        return result