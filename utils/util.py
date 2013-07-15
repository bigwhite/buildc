#! /usr/bin/env python
import commands
import os
import sys

class Util:

    @staticmethod
    def usr_home():
        return os.path.expanduser('~')

    @staticmethod
    def go_to_path(path):
        old_path = os.getcwd()
        os.chdir(path)
        #print "Cd " + path
        return old_path

    @staticmethod
    def get_cur_path():
        curdir = os.getcwd()
        return curdir

    @staticmethod
    def execute_and_return(cmd):
        out = commands.getstatusoutput(cmd)
        err = out[0]
        return err

    @staticmethod
    def execute_and_output(cmd, ignore_error = None):
        out = commands.getstatusoutput(cmd)
        err = out[0]
        string = out[1]
        if err != 0:
            print "Failed to execute cmd [%s], errno = [%d]" % (cmd, err)
            if (ignore_error == None):
                sys.exit(err)

        return string

if __name__ == '__main__':
    print "usr_home : "       + Util.usr_home()

    pass
