#! /usr/bin/env python

import sys
import os
import shutil

DEFAULT_INSTALL_ROOT = '/usr/share/buildc'
BIN_SYMBOL_LINK = '/usr/bin/buildc'

def get_args():
    argv = sys.argv
    if len(argv) > 3 or len(argv) <= 1:
        print 'error: too many or too few options!'
        print 'usage: %s %s' % (argv[0], ' install|uninstall [--prefix=INSTALL_PATH]')
        sys.exit(0)

    action = ''
    install_root = ''

    for arg in argv[1:]:
        if arg == 'install':
            action = 'install'
        elif arg == 'uninstall':
            action = 'uninstall'
        elif arg.find('--prefix=') == 0:
            install_root = os.path.expanduser(arg[arg.rindex('=')+1:]) + '/buildc'
        else:
            print 'error: unsupport option: %s' % arg
            print 'usage: %s %s' % (argv[0], ' install|uninstall [--prefix=INSTALL_PATH]')

    if action == '':
        print 'usage: %s %s' % (argv[0], ' install|uninstall [--prefix=INSTALL_PATH]')

    if install_root == '':
        install_root = DEFAULT_INSTALL_ROOT

    return action, install_root

def do_install(install_root):
    if os.path.exists(install_root):
        print 'error: buildc has been already installed on this host'
        print """if you want to reinstall buildc, please run 'setup.py uninstall [--prefix=INSTALL_PATH]' first!"""
        sys.exit(-1)

    package_root = os.path.dirname(os.path.realpath(__file__))

    if sys.version_info[0] == 2 and sys.version_info[1] < 6:
        shutil.copytree(package_root, install_root)
    else:
        shutil.copytree(package_root, install_root, ignore = shutil.ignore_patterns('*.pyc', '.svn'))
    print 'Install buildc to [%s] OK!' % install_root

    if install_root == DEFAULT_INSTALL_ROOT:
        os.symlink(install_root + '/buildc', BIN_SYMBOL_LINK)
        print 'Create symbol link [%s] OK!' % BIN_SYMBOL_LINK

    print 'install buildc ok!'

def do_uninstall(install_root):
    if install_root == DEFAULT_INSTALL_ROOT:
        if os.path.exists(BIN_SYMBOL_LINK):
            os.remove(BIN_SYMBOL_LINK)

    if os.path.exists(install_root):
        shutil.rmtree(install_root)

    print 'uninstall buildc ok!'

def setup_main():
    action, install_root = get_args()

    if action == 'install':
        do_install(install_root)
    else:
        do_uninstall(install_root)

if __name__ == '__main__':
    setup_main()
