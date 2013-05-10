#!/usr/bin/env python

# Copyright (c) 2011 - 2012 Tony Bai <bigwhite.cn@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import shutil

sys.path.append('..')

from utils import errnos
from utils import config
from utils import command
from utils import env

import makerules

BIT32 = '32-bit'
BIT64 = '64-bit'

def init(buildc_home):
    dotrc = config.dot_buildc_rc_path()
    if os.path.exists(dotrc):
        print dotrc + ' has been already existed! Just config it!'
    else:
        buildc_rc_in = buildc_home + '/templates/' + 'buildc.rc.in'
        if os.path.exists(buildc_rc_in):
            shutil.copyfile(buildc_rc_in, dotrc)
            print "Copy " + buildc_rc_in + " to " + dotrc + " OK!"
            print "Please config " +  dotrc  + " before you use other buildc commands!"

    return

def __cache_init(cmode, ignore_error):
    dotrc = config.dot_buildc_rc_path()
    if not os.path.exists(dotrc):
        print 'Can not found ' + dotrc
        print 'Please run buildc init and then config .buildc.rc!'
        sys.exit(errnos.errors['conf_file_not_found'])

    c = config.load_config(dotrc)
    for repository in c.external_repositories:
        (url, local_path, libs) = repository

        print "\n===>Begin init repository [" + url + ']'

        cache_path = os.path.abspath(os.path.expanduser(local_path))
        if not os.path.exists(cache_path):
            command.execute('mkdir -p ' + cache_path)
            print 'Create dir: ' + cache_path
        else:
            print cache_path + ' exists!'

        for (libname, libversion, tagfile) in libs:
            lib_path = cache_path + '/' + libname + '/' + libversion
            lib_url = url + '/' + libname + '/' + libversion + '/' + env.cpu() + '_' + cmode[0:2] + '_' + env.os()
            tagfile_path = lib_path + '/' + env.cpu() + '_' + cmode[0:2] + '_' + env.os() + '/' + tagfile
            if os.path.exists(tagfile_path):
                print 'library [' + libname + '] exists!'
            else:
                print 'library [' + libname + '] does not exist!'
                command.execute('mkdir -p ' + lib_path)
                print 'Checkout [' + lib_url + ']...'
                cwd = os.getcwd()
                os.chdir(lib_path)
                ret = command.execute('svn checkout ' + lib_url, ignore_error)
                if (ret[0] != 0):
                    print 'Checkout [' + lib_url + '] Failed!'
                    if (ignore_error == None):
                        sys.exit(ret[0])
                else:
                    print 'Checkout [' + lib_url + '] OK!'

                os.chdir(cwd)
        print '<=== End init repository [' + url + ']'

def cache_init(cmode, ignore_error):
    if cmode == None:
        __cache_init(BIT32, ignore_error)
        __cache_init(BIT64, ignore_error)
    else:
        __cache_init(cmode, ignore_error)

    sys.exit(0)

def __cache_update(cmode, ignore_error):
    dotrc = config.dot_buildc_rc_path()

    if not os.path.exists(dotrc):
        print 'Can not found ' + dotrc
        print 'Please run buildc init and then config .buildc.rc!'
        sys.exit(errnos.errors['conf_file_not_found'])

    c = config.load_config(dotrc)
    for repository in c.external_repositories:
        (url, local_path, libs) = repository

        if len(libs) == 0:
            continue

        print "\n===>Begin update repository [" + url + ']'

        cache_path = os.path.abspath(os.path.expanduser(local_path))
        if not os.path.exists(cache_path):
            print 'Can not found local cache: [' + cache_path + ']'
            sys.exit(errnos.errors['lib_not_found'])

        for (libname, libversion, tagfile) in libs:
            lib_path = cache_path + '/' + libname + '/' + libversion + '/' + env.cpu() + '_' + cmode[0:2] + '_' + env.os()
            if not os.path.exists(lib_path):
                print 'library [' + libname + '] does not exist!'
                sys.exit(errnos.errors['lib_not_found'])
            else:
                cwd = os.getcwd()
                os.chdir(lib_path)
                print 'Update [' + libname + ']...'
                ret = command.execute('svn update', ignore_error)
                if (ret[0] != 0):
                    print 'Update [' + libname + '] Failed!'
                    if (ignore_error == None):
                        sys.exit(ret[0])
                else:
                    print 'Update [' + libname + '] OK!'

                os.chdir(cwd)
        print '<=== End update repository [' + url + ']'

def cache_update(cmode, ignore_error):
    if cmode == None:
        __cache_update(BIT32, ignore_error)
        __cache_update(BIT64, ignore_error)
    else:
        __cache_update(cmode, ignore_error)

    sys.exit(0)

def __check_buildc_rc(cmode):
    platform_info = env.cpu() + '_' + cmode[0:2] + '_' + env.os()

    c1 = config.load_config(config.dot_buildc_rc_path())

    cache_libs = []
    lib_path = ''
    ret = True

    for repository in c1.external_repositories:
        url, cache_path, libs = repository
        for lib in libs:
            cache_libs.append((lib[0], lib[1], os.path.expanduser(cache_path)))
            lib_path = os.path.expanduser(cache_path) + '/' + lib[0] + '/' + lib[1] + '/' + platform_info
            if not os.path.exists(lib_path):
                print cache_path+ '/' + lib[0] + '/' + lib[1] + '/' + platform_info + ' does not exist in local cache!'
                ret = False

    return ret

def __cache_upgrade(cmode, ignore_error):
    print ".buildc.rc checking starts..."
    if not __check_buildc_rc(cmode):
        print 'The configuration in .buildc.rc is not consistent with the layout of the local library cache!'
        __cache_remove_by_cmode(cmode)
        __cache_init(cmode, ignore_error)
    else:
        print 'The configuration in .buildc.rc is consistent with the layout of the local library cache'
        __cache_update(cmode, ignore_error)
    print "Local cache upgrade Ok!"

def cache_upgrade(cmode, ignore_error):
    if cmode == None:
        __cache_upgrade(BIT32, ignore_error)
        __cache_upgrade(BIT64, ignore_error)
    else:
        __cache_upgrade(cmode, ignore_error)

    sys.exit(0)

def __cache_remove():
    dotrc = config.dot_buildc_rc_path()
    if not os.path.exists(dotrc):
        print 'Can not found ' + dotrc
        print 'Please run buildc init and then config .buildc.rc!'
        sys.exit(errnos.errors['conf_file_not_found'])

    c = config.load_config(dotrc)
    for repository in c.external_repositories:
        (url, local_path, libs) = repository

        print "\n===>Begin remove local cache of repository [" + url + ']'
        cache_path = os.path.abspath(os.path.expanduser(local_path))
        ret = command.execute('rm -fr ' + cache_path)
        if (ret[0] != 0):
            print 'Remove [' + cache_path + '] Failed!'
            sys.exit(ret[0])
        else:
            print 'Remove [' + cache_path + '] OK!'
        print "\n<=== End remove local cache of repository [" + url + ']'

def __cache_remove_by_cmode(cmode):
    dotrc = config.dot_buildc_rc_path()
    if not os.path.exists(dotrc):
        print 'Can not found ' + dotrc
        print 'Please run buildc init and then config .buildc.rc!'
        sys.exit(errnos.errors['conf_file_not_found'])

    c = config.load_config(dotrc)
    for repository in c.external_repositories:
        (url, local_path, libs) = repository

        print "\n===>Begin remove local cache of repository [" + url + ']'

        cache_path = os.path.abspath(os.path.expanduser(local_path))
        if not os.path.exists(cache_path):
            print 'Can not found local cache: [' + cache_path + ']'
            continue

        for (libname, libversion, tagfile) in libs:
            lib_path = cache_path + '/' + libname + '/' + libversion + '/' + env.cpu() + '_' + cmode[0:2] + '_' + env.os()
            libname_path = cache_path + '/' + libname
            libversion_path = cache_path + '/' + libname + '/' + libversion
            if not os.path.exists(lib_path):
                print 'library [' + libname + '] does not exist!'
            else:
                ret = command.execute('rm -fr ' + lib_path)
                if (ret[0] != 0):
                    print 'Remove [' + lib_path + '] Failed!'
                    sys.exit(ret[0])
                else:
                    print 'Remove [' + lib_path + '] OK!'

            if os.path.exists(libversion_path):
                if len(os.listdir(libversion_path)) == 0:
                    os.rmdir(libversion_path)
            if os.path.exists(libname_path):
                if len(os.listdir(libname_path)) == 0:
                    os.rmdir(libname_path)

        if len(os.listdir(cache_path)) == 0:
            os.rmdir(cache_path)
        print "\n<=== End remove local cache of repository [" + url + ']'

def cache_remove(cmode):
    if cmode == None:
        __cache_remove()
    else:
        __cache_remove_by_cmode(cmode)

    sys.exit(0)

def __check_buildc_cfg(cmode, lib_root_path = None):
    platform_info = env.cpu() + '_' + cmode[0:2] + '_' + env.os()

    c1 = config.load_config(config.dot_buildc_rc_path())
    c2 = config.load_config('./buildc.cfg')

    cache_libs = []
    for repository in c1.external_repositories:
        url, cache_path, libs = repository
        for lib in libs:
            cache_libs.append((lib[0], lib[1], os.path.expanduser(cache_path)))

    libs_depend = []
    for (libname, libversion, archives) in c2.external_libs:
        is_found = False
        for (cache_libname, cache_libversion, cache_path) in cache_libs:
            if libname == cache_libname and libversion == cache_libversion:
                path = None
                if lib_root_path == None:
                    path = cache_path + '/' + libname + '/' + libversion + '/' + platform_info
                else:
                    path = lib_root_path + '/' + libname + '/' + libversion + '/' + platform_info

                if not os.path.exists(cache_path + '/' + libname + '/' + libversion + '/' + platform_info):
                    print 'Can not found [' + cache_path + '/' + libname + '/' + libversion + '/' + platform_info + '] in local library cache!'
                    print 'Please make sure the library [' + cache_path + '/' + libname + '/' + libversion + '/' + platform_info + '] is available!'
                    continue

                libs_depend.append((libname, libversion, archives, path))

                is_found = True
                break
        if not is_found:
            print 'Can not found [' + libname + '] in local library cache!'
            print 'Please make sure the library [' + libname + '] is available!'
            sys.exit(errnos.errors['lib_not_found'])

    return libs_depend

def config_init(buildc_home):
    buildc_cfg_in = buildc_home + '/templates/' + 'buildc.cfg.in'
    if not os.path.exists('./buildc.cfg'):
        shutil.copyfile(buildc_cfg_in, 'buildc.cfg')
        print "Copy " + buildc_cfg_in + " to " + './buildc.cfg' + " OK!"
        print "Please config buildc.cfg before you use [buildc config make] command!"
    else:
        print 'buildc.cfg has been already existed! Just config it!'

def config_make(buildc_home, cmode, lib_root_path = None, project_root_path = None):
    if not os.path.exists('./buildc.cfg'):
        print 'Can not found buildc.cfg in current directory!'
        print 'Please run buildc init to generate this file!'
        sys.exit(errnos.errors['conf_file_not_found'])

    if not os.path.exists(config.dot_buildc_rc_path()):
        print 'Can not found ~/.buildc.rc!'
        print 'Please run buildc init to generate this file!'
        sys.exit(errnos.errors['conf_file_not_found'])

    libs_depend = __check_buildc_cfg(cmode, lib_root_path)

    if not os.path.exists('./Make.rules'):
        print 'Can not found Make.rules in current directory!'
        makerules.generate(buildc_home, cmode, libs_depend, project_root_path)
    elif os.path.getsize('./Make.rules') == 0:
        print 'The Make.rules file is empty in current directory!'
        makerules.generate(buildc_home, cmode, libs_depend, project_root_path)
    else:
        makerules.reconfig(cmode, libs_depend, project_root_path)

if __name__ == '__main__':
    print 'core.py'
