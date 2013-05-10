#!/usr/bin/env python
import re
import sys
from utils.errnos import Errors
from utils.util import Util

class SystemLocalInfo:
    error_info_str = None

    @staticmethod
    def system():
        s = Util.execute_and_output('uname -s')

        if (s == 'Linux'):
            return 'linux'
        if (s == 'SunOS'):
            return 'solaris'
        if (s == 'CYGWIN_NT-6.1-WOW64'):
            return 'CYGWIN_NT-6.1-WOW64'
        else:
            return 'unknown'

    @staticmethod
    def cpu():
        s = Util.execute_and_output('uname -p')

        if (s == 'sparc'):
            return 'sparc'
        if (s == 'i386'):
            return 'x86'
        if (s == 'x86_64'):
            return 'x86'
        else:
            return 'unknown'

    @staticmethod
    def system_bit():
        bit = None

        system_name = SystemLocalInfo.system()
        if system_name == 'linux':
            bit = Util.execute_and_output('getconf LONG_BIT')
            return bit
        elif system_name == 'solaris':
            bit = Util.execute_and_output('isainfo -b')
            return bit
        else:
            return 'unknown'

    @staticmethod
    def system_version():
        version = None

        system_name = SystemLocalInfo.system()
        if system_name == 'linux':
            s = Util.execute_and_output('cat /etc/redhat-release')
            s_prefix = 'release'
            s_code   = s[s.find(s_prefix):s.find(s_prefix)+50]
            version = re.findall("((\d+\.)*\d+)", s_code)[0][0]
            return version
        elif system_name == 'solaris':
            version = Util.execute_and_output('uname -r')
            return version
        else:
            return 'unknown'

    @staticmethod
    def memory_total_size():
        size = 0

        system_name = SystemLocalInfo.system()
        if system_name == 'linux':
            s = Util.execute_and_output('free -m', True)
            if s == None:
                SystemLocalInfo.error_info_str = "checking for free -m command fails ... no"
                return -1

            size = re.findall("\d+", s)[0]
            return int(size)
        elif system_name == 'solaris':
            s = Util.execute_and_output('/usr/sbin/prtconf -vp | grep Mem')
            size = re.findall("\d+", s)[0]
            return int(size)
        else:
            SystemLocalInfo.error_info_str = None
            return -1

    @staticmethod
    def memory_free_size():
        size = 0

        system_name = SystemLocalInfo.system()
        if system_name == 'linux':
            s = Util.execute_and_output('free -m', True)
            if s == None:
                SystemLocalInfo.error_info_str = "checking for free -m command fails ... no"
                return -1

            s_prefix = 'buffers/cache'
            s_code   = s[s.find(s_prefix):s.find(s_prefix)+50]
            size = re.findall("\d+", s_code)[1]
            return int(size)
        elif system_name == 'solaris':
            s = Util.execute_and_output('top | head -n 4', True)
            if s == None:
                SystemLocalInfo.error_info_str = "checking for top | head -n 4 command fails ... no"
                return -1

            size = re.findall("(\d+)M free mem", s)[0]
            return int(size)
        else:
            SystemLocalInfo.error_info_str = None
            return -1

    @staticmethod
    def harddisk_total_size():
        size = 0

        system_name = SystemLocalInfo.system()

        s = Util.execute_and_output("df -h | sed \'1d\'")
        step = 6
        unit = 1024
        s_list = re.split('[\t\n]?\s\s*|\n', s)
        if len(s_list) % step != 0:
            print "error: the length of the list is invalid."
            sys.exit(Errors.logical_errors)
        if system_name == 'linux':
            index = 1
            count = len(s_list) / step
            size = 0
            i = 0
            while(i < count):
                if str(s_list[index])[-1] == "G":
                    size += float(str(s_list[index])[:-1])*unit*unit
                elif str(s_list[index])[-1] == "M":
                    size += float(str(s_list[index])[:-1])*unit
                else:
                    size += float(str(s_list[index])[:-1])
                index += step
                i += 1

            size = int(size/unit/unit)
            return size

        elif system_name == 'solaris':
            index = 1
            count = len(s_list) / step
            size = 0

            swap_num = 0
            i = 0
            while(i < count):
                if str(s_list[index-1]).startswith("/dev/dsk") == False and \
                    str(s_list[index-1]) != "swap":
                    index += step
                    i += 1
                    continue

                if str(s_list[index-1]) == "swap":
                    swap_num += 1
                    if swap_num > 1:
                        index += step
                        i += 1
                        continue

                if str(s_list[index])[-1] == "G":
                    size += float(str(s_list[index])[:-1])*unit*unit
                elif str(s_list[index])[-1] == "M":
                    size += float(str(s_list[index])[:-1])*unit
                elif str(s_list[index])[-1] == "K":
                    size += float(str(s_list[index])[:-1])
                else:
                    if str(s_list[index]) == "0":
                        size += 0
                    else:
                        print "error: the list element is invalid."
                        sys.exit(Errors.logical_errors)
                index += step
                i += 1

            size = int(size/unit/unit)
            return size

        else:
            return -1

    @staticmethod
    def harddisk_free_size():
        size = 0

        system_name = SystemLocalInfo.system()

        s = Util.execute_and_output("df -h | sed \'1d\'")
        step = 6
        unit = 1024
        s_list = re.split('[\t\n]?\s\s*|\n', s)
        if len(s_list) % step != 0:
            print "error: the length of the list is invalid."
            sys.exit(Errors.logical_errors)
        if system_name == 'linux':
            index = 3
            count = len(s_list) / step
            size = 0
            i = 0
            while(i < count):
                if str(s_list[index])[-1] == "G":
                    size += float(str(s_list[index])[:-1])*unit*unit
                elif str(s_list[index])[-1] == "M":
                    size += float(str(s_list[index])[:-1])*unit
                elif str(s_list[index])[-1] == "K":
                    size += float(str(s_list[index])[:-1])
                else:
                    if str(s_list[index]) == "0":
                        size += 0
                    else:
                        print "error: the list element is invalid."
                        sys.exit(Errors.logical_errors)
                index += step
                i += 1

            size = int(size/unit/unit)
            return size

        elif system_name == 'solaris':
            index = 3
            count = len(s_list) / step
            size = 0

            swap_num = 0
            i = 0
            while(i < count):
                if str(s_list[index-3]).startswith("/dev/dsk") == False and \
                    str(s_list[index-3]) != "swap":
                    index += step
                    i += 1
                    continue

                if str(s_list[index-3]) == "swap":
                    swap_num += 1
                    if swap_num > 1:
                        index += step
                        i += 1
                        continue

                if str(s_list[index])[-1] == "G":
                    size += float(str(s_list[index])[:-1])*unit*unit
                elif str(s_list[index])[-1] == "M":
                    size += float(str(s_list[index])[:-1])*unit
                elif str(s_list[index])[-1] == "K":
                    size += float(str(s_list[index])[:-1])
                else:
                    if str(s_list[index]) == "0":
                        size += 0
                    else:
                        print "error: the list element is invalid."
                        sys.exit(Errors.logical_errors)

                index += step
                i += 1

            size = int(size/unit/unit)
            return size

        else:
            return -1

    @staticmethod
    def get_shell_type():
        cmd_output = Util.execute_and_output('echo $SHELL')
        match_str = re.findall('\/.*\/.*', cmd_output)[0]

        if match_str == '/bin/csh':
            return 'csh'
        elif match_str == '/bin/bash':
            return 'bash'
        else:
            return 'unknown'

if __name__ == '__main__':
    print "system : "              + SystemLocalInfo.system()
    print "cpu : "                 + SystemLocalInfo.cpu()
    print "system_bit : "          + SystemLocalInfo.system_bit()
    print "system_version : "      + SystemLocalInfo.system_version()
    print "memory_total_size : "   + str(SystemLocalInfo.memory_total_size())
    print "memory_free_size : "    + str(SystemLocalInfo.memory_free_size())
    print "harddisk_total_size : " + str(SystemLocalInfo.harddisk_total_size())
    print "harddisk_free_size : "  + str(SystemLocalInfo.harddisk_free_size())
    print "get_shell_type : "      + SystemLocalInfo.get_shell_type()
    print "test end!"
