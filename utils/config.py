#!/usr/bin/env python
import imp
import os
from utils.util import Util

class Config(object):
    @staticmethod
    def load_config(filename):
        f = open(filename, 'rU')
        try:
            m = imp.load_source('', filename, f)
        except SyntaxError, error:
            print error
        f.close()
        Util.execute_and_output('rm -f ' + filename + 'c')

        return m

if __name__ == '__main__':
    exit
