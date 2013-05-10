#! /usr/bin/env python
import commands

def os():

    s = commands.getoutput('uname -s')
    if (s == 'Linux'):
        return 'linux'
    if (s == 'SunOS'):
        return 'solaris'
    else:
        return 'unknown'

def cpu():

    s = commands.getoutput('uname -p')
    if (s == 'sparc'):
        return 'sparc'
    if (s == 'i386'):
        return 'x86'
    if (s == 'x86_64'):
        return 'x86'
    else:
        return 'unknown'

if __name__ == '__main__':
    print os()
    print cpu()
