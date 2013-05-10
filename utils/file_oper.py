#!/usr/bin/env python
import sys
import os
from utils.errnos import Errors

class FileOper(object):
    @staticmethod
    def write_data(file_path, data):
        data_file = open(file_path, 'w')
        data_file.write(data)
        data_file.close()

    @staticmethod
    def read_data(file_path):
        data_file = open(file_path, 'r')
        text = data_file.read()
        data_file.close()
        return text

    @staticmethod
    def read_textlines(file_path):
        if not os.path.exists(file_path):
            print 'error: %s does not exist', file_path
            sys.exit(Errors.file_or_dir_exists)

        data_file = open(file_path, 'r')
        textlines = data_file.readlines()
        data_file.close()

        return textlines

    @staticmethod
    def textline_exist(file_path, textline):
        data_file = open(file_path, 'r')
        textlines = data_file.readlines()

        for cur_textline in textlines:
            if cur_textline == textline + os.linesep:
                return True

        return False

if __name__ == '__main__':
    file_path = "X:\\ttt.txt"
    FileOper.write_data(file_path, "11111\r\n22222\r\n33333")
    text = None
    text = FileOper.read_data(file_path)
    pass
