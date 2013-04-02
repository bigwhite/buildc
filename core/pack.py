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

sys.path.append('..')

import os
import shutil
import string
import time
import re
import itertools
import glob
from ftplib import FTP

from utils import command
from utils import config
from utils import env
from utils import errnos
import core

SETUP_CFG_FILE = "./setup.cfg"
DEPENDENCE_LONG_NUM  = 3
DEPENDENCE_SHORT_NUM = 2

def __pack_init():
  c = config.load_config(SETUP_CFG_FILE)
  return c

def __build_component_deps(build_home, url, cmode):
    command.execute('mkdir -p ' + build_home + '/.build')
    os.chdir(build_home + '/.build')
    print "Create dir [.build] OK!"

    command.execute('rm -rf ' + url[url.rindex("/")+1:])
    command.execute('svn export ' + url)
    print "Export [" + url + "] OK!"

    source_home = build_home + '/.build/' + url[url.rindex("/")+1:]
    os.chdir(source_home)
    print "Cd " + source_home

    dotrc = config.dot_buildc_rc_path()
    if not os.path.exists(dotrc):
        print('Can not found ' + dotrc)
        print('Please run buildc init and then config .buildc.rc!')
        sys.exit(errnos.errors['conf_file_not_found'])
    c1 = config.load_config(dotrc)

    c2 = config.load_config('buildc.cfg')
    for dependence in c2.external_libs:
        __copy_dependent_all(dependence, c1.external_repositories, build_home, cmode)

    os.chdir(build_home)
    print "Cd " + build_home

    print 'Build deps [' + url + '] OK!'

def __build_component_src(buildc_home, build_home, url, cmode):
    command.execute('mkdir -p ' + build_home + '/.build')
    os.chdir(build_home + '/.build')
    print "Create dir [.build] OK!"

    command.execute('rm -rf ' + url[url.rindex("/")+1:])
    command.execute('svn export ' + url)
    print "Export [" + url + "] OK!"

    source_home = build_home + '/.build/' + url[url.rindex("/")+1:]
    os.chdir(source_home)
    print "Cd " + source_home

    core.config_make(buildc_home, cmode, "$(shell cd ../.; pwd)/deps", "$(shell cd .; pwd)")
    print "Config Make.rules OK!"
    command.execute('rm -f buildc.cfg')
    print "Remove buildc.cfg OK!"

    cmd_str =\
"""#! /bin/sh

topdir=`pwd`
parentdir=`cd ../.; pwd`
sed -e "1,$ s%=.*@topdir@%= $topdir#@topdir@%g" Make.rules |\
sed -e "1,$ s%\$(shell cd ../.; pwd)/deps%$parentdir/deps%g"\
> .Make.rules
mv .Make.rules Make.rules

echo "config Make.rules OK!"
"""
    file = open("configure", "w")
    file.write(cmd_str)
    file.close()
    command.execute('chmod +x configure')
    print "Create configure OK!"

    os.chdir(build_home)
    print "Cd " + build_home

    print 'Build src [' + url + '] OK!'

def __build_source(build_home, url, cmode, binary_prefix, pack_path):
  command.execute('mkdir -p ' + build_home + '/.build')
  os.chdir(build_home + '/.build')
  print "Create dir [.build] OK!"

  command.execute('svn export ' + url)
  print "Export [" + url + "] OK!"

  source_home = build_home + '/.build/' + url[url.rindex("/")+1:]
  os.chdir(source_home)
  print "Cd " + source_home

  command.execute('buildc config make --cmode=' + cmode)
  print "Config Make.rules OK!"

  command.execute('make CMODE=' + cmode)
  print "Make Ok"

  if pack_path != "":
    command.execute('cp ' + binary_prefix + '* ' + build_home + '/src/' + pack_path)
    print "Copy binary file to [" + build_home + '/src/' + pack_path + ']' + " Ok!"

  os.chdir(build_home)
  print "Cd " + build_home

  print 'Build source [' + url + '] OK!'

def __get_svn_info_revision_code(url):
    svn_info_str = str(command.execute('svn info ' + url)[1])

    revision_code = re.findall(" (\d+)\n", svn_info_str)
    #revision_code: list of two elements, a revision number, a last changed rev

    if len(revision_code) == 0:
        return ""

    return revision_code[0]

def __build_version(build_home, source, tag, cmode):
    information_str = env.cpu() + '-' + env.os() + '-' + cmode[:2] + 'bit';
    cur_time_str    = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    project_reversion_list = list()

    if tag != None:
        url = tag
        project_name   = url[url.rindex("/")+1:]
        revision_code = __get_svn_info_revision_code(url)
        project_reversion_list.append("project name: %s, revision: %s" % (project_name, revision_code))
    else:
        for index in range(len(source)):
            url = source[index]["trunk"]
            project_name   = url[url.rindex("/")+1:]
            revision_code = __get_svn_info_revision_code(url)
            project_reversion_list.append("project name: %s, revision: %s" % (project_name, revision_code))

    info_str  = "";
    info_str += "information: " + information_str + os.linesep;
    info_str += "build time: "  + cur_time_str + os.linesep;
    for index in range(len(project_reversion_list)):
        info_str += project_reversion_list[index] + os.linesep;

    version_file = open(build_home + os.sep + 'src' + os.sep + 'VERSION', 'w')
    version_file.write(info_str)
    version_file.close()

    print('Build VERSION OK!')

def __make_component_deps_package(build_home, distribution, cmode):
    os.chdir(build_home)

    command.execute('mkdir -p ' + build_home + '/.package')
    print "Create dir [.package] OK!"

    target_prefix = distribution["packname"] + \
           '-' + distribution["version"] + \
           '-' + env.cpu() + \
           '-' + env.os() + \
           '-' + cmode[:2] + 'bit' + '-deps'

    os.makedirs(build_home + '/.package/' + target_prefix)
    print "Create dir [.package/" + target_prefix + "] OK!"
    if sys.version_info[0] == 2 and sys.version_info[1] < 6:
        shutil.copytree(build_home + '/src/deps', build_home + '/.package/' + target_prefix + '/deps')
    else:
        shutil.copytree(build_home + '/src/deps', build_home + '/.package/' + target_prefix + '/deps',
                        ignore = shutil.ignore_patterns('*.pyc', '.svn'))
    shutil.copy2(build_home + '/src/VERSION', build_home + '/.package/' + target_prefix)

    os.chdir(build_home + '/.package')
    print "Cd " + build_home + '/.package'

    command.execute('tar cvf ' + target_prefix + '.tar ' + target_prefix)
    print 'Generate ' + target_prefix + '.tar' + ' OK!'

    command.execute('gzip ' + target_prefix + '.tar')
    print('Zip ' + target_prefix + '.tar' + ' OK!')

    os.chdir(build_home)
    print('Cd ' + build_home)

    command.execute('mv .package/' + target_prefix + '.tar.gz ' + 'distributions')
    command.execute('rm -fr ' + build_home + '/.package')
    print 'Del [.package] OK!'

    print 'Make target [' + target_prefix + '.tar.gz] OK!'

def __make_component_src_package(build_home, distribution, cmode):
    os.chdir(build_home)

    command.execute('mkdir -p ' + build_home + '/.package')
    print "Create dir [.package] OK!"

    target_prefix = distribution["packname"] + \
           '-' + distribution["version"] + \
           '-' + env.cpu() + \
           '-' + env.os() + \
           '-' + cmode[:2] + 'bit' + '-src'

    if sys.version_info[0] == 2 and sys.version_info[1] < 6:
        shutil.copytree(build_home + '/.build', build_home + '/.package/' + target_prefix)
    else:
        shutil.copytree(build_home + '/.build', build_home + '/.package/' + target_prefix,
                        ignore = shutil.ignore_patterns('*.pyc', '.svn'))
    shutil.copy2(build_home + '/src/VERSION', build_home + '/.package/' + target_prefix)

    os.chdir(build_home + '/.package')
    print "Cd " + build_home + '/.package'

    command.execute('tar cvf ' + target_prefix + '.tar ' + target_prefix)
    print 'Generate ' + target_prefix + '.tar' + ' OK!'

    command.execute('gzip ' + target_prefix + '.tar')
    print('Zip ' + target_prefix + '.tar' + ' OK!')

    os.chdir(build_home)
    print('Cd ' + build_home)

    command.execute('mv .package/' + target_prefix + '.tar.gz ' + 'distributions')
    command.execute('rm -fr ' + build_home + '/.package')
    print 'Del [.package] OK!'

    print 'Make target [' + target_prefix + '.tar.gz] OK!'

def __make_component_all_package(build_home, distribution, cmode):
    os.chdir(build_home)

    command.execute('mkdir -p ' + build_home + '/.package')
    print "Create dir [.package] OK!"

    target_prefix = distribution["packname"] + \
           '-' + distribution["version"] + \
           '-' + env.cpu() + \
           '-' + env.os() + \
           '-' + cmode[:2] + 'bit' + '-full'

    src_path = build_home + '/src/deps'
    dst_path = build_home + '/.package/' + target_prefix + '/deps'
    __copy_tree(src_path, dst_path, [".svn"], ["*"])
    print "copy %s to %s" % (src_path, dst_path)

    src_path = build_home + '/.build'
    dst_path = build_home + '/.package/' + target_prefix
    __copy_tree(src_path, dst_path, [".svn"], ["*"])
    print "copy %s to %s" % (src_path, dst_path)
    shutil.copy2(build_home + '/src/VERSION', build_home + '/.package/' + target_prefix)

    os.chdir(build_home + '/.package')
    print "Cd " + build_home + '/.package'

    command.execute('tar cvf ' + target_prefix + '.tar ' + target_prefix)
    print 'Generate ' + target_prefix + '.tar' + ' OK!'

    command.execute('gzip ' + target_prefix + '.tar')
    print('Zip ' + target_prefix + '.tar' + ' OK!')

    os.chdir(build_home)
    print('Cd ' + build_home)

    command.execute('mv .package/' + target_prefix + '.tar.gz ' + 'distributions')
    command.execute('rm -fr ' + build_home + '/.package')
    print 'Del [.package] OK!'

    print 'Make target [' + target_prefix + '.tar.gz] OK!'

def __make_package(build_home, distribution, cmode):
  os.chdir(build_home)

  command.execute('mkdir -p ' + build_home + '/.package')
  print "Create dir [.package] OK!"

  target_prefix = distribution["packname"] + \
           '-' + distribution["version"] + \
           '-' + env.cpu() + \
           '-' + env.os() + \
           '-' + cmode[:2] + 'bit'

  if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    shutil.copytree(build_home + '/src', build_home + '/.package/' + target_prefix)
  else:
    shutil.copytree(build_home + '/src', build_home + '/.package/' + target_prefix,
                    ignore = shutil.ignore_patterns('*.pyc', '.svn'))

  os.chdir(build_home + '/.package')
  print "Cd " + build_home + '/.package'

  command.execute('tar cvf ' + target_prefix + '.tar ' + target_prefix)
  print 'Generate ' + target_prefix + '.tar' + ' OK!'

  command.execute('gzip ' + target_prefix + '.tar')
  print('Zip ' + target_prefix + '.tar' + ' OK!')

  os.chdir(build_home)
  print('Cd ' + build_home)

  command.execute('mv .package/' + target_prefix + '.tar.gz ' + 'distributions')
  command.execute('rm -fr ' + build_home + '/.package')
  print 'Del [.package] OK!'

  print('Make target [' + target_prefix + '.tar.gz] OK!')

def __do_clean(build_home):
  command.execute('rm -fr ' + build_home + '/.build')
  print 'Clean [.build] OK!'

  command.execute('rm -fr ' + build_home + '/.package')
  print 'Clean [.package] OK!'

  command.execute('rm -f ' + build_home + '/src/app/*')
  print 'Clean [./src/app] OK!'

  command.execute('rm -fr ' + build_home + '/src/deps/*')
  print 'Clean [./src/deps] OK!'

  command.execute('rm -f ' + build_home + '/distributions/*.tar.gz')
  print 'Clean [./distributions] OK!'

  print 'Package distribution clean OK!'

def __do_component_deps_pack(build_home, source, distribution, tag, cmode):
    url = ''
    if tag != None:
        url = tag
        __build_component_deps(build_home, url, cmode)
    else:
        for index in range(len(source)):
            url = source[index]["trunk"]
            __build_component_deps(build_home, url, cmode)

    __build_version(build_home, source, tag, cmode)

    command.execute('rm -fr ' + build_home + '/.build')
    print 'Del [.build] OK!'

    __make_component_deps_package(build_home, distribution, cmode)

def __do_component_src_pack(buildc_home, build_home, source, distribution, tag, cmode):
    url = ''
    if tag != None:
        url = tag
        __build_component_src(buildc_home, build_home, url, cmode)
    else:
        for index in range(len(source)):
            url = source[index]["trunk"]
            __build_component_src(buildc_home, build_home, url, cmode)

    __build_version(build_home, source, tag, cmode)

    __make_component_src_package(build_home, distribution, cmode)

    command.execute('rm -fr ' + build_home + '/.build')
    print 'Del [.build] OK!'

def __do_component_all_pack(buildc_home, build_home, source, distribution, tag, cmode):
    url = ''
    if tag != None:
        url = tag
        __build_component_deps(build_home, url, cmode)
        __build_component_src(buildc_home, build_home, url, cmode)
    else:
        for index in range(len(source)):
            url = source[index]["trunk"]
            __build_component_deps(build_home, url, cmode)
            __build_component_src(buildc_home, build_home, url, cmode)

    __build_version(build_home, source, tag, cmode)

    __make_component_all_package(build_home, distribution, cmode)

    command.execute('rm -fr ' + build_home + '/.build')
    print 'Del [.build] OK!'

def __do_pack(build_home, source, distribution, opts):
    url = ''

    cmode = opts.cmode

    pack_path = ""
    if opts.tag != None:
        url       = opts.tag
        pack_path = 'app'
        __build_source(build_home, url, cmode, source[0]["binary_prefix"], pack_path)
    else:
        for index in range(len(source)):
            url = source[index]["trunk"]
            if dict(source[index]).get("pack_path") == None:
                pack_path = 'app'
            else:
                pack_path = source[index]["pack_path"]
            __build_source(build_home, url, cmode, source[index]["binary_prefix"], pack_path)

    __build_version(build_home, source, opts.tag, opts.cmode)

    command.execute('rm -fr ' + build_home + '/.build')
    print('Del [.build] OK!')

    __make_package(build_home, distribution, cmode)

def __do_upload(build_home, distribution, opts):
    target_prefix = distribution["packname"] + \
            '-' + distribution["version"] + \
            '-' + env.cpu() + \
            '-' + env.os() + \
            '-' + opts.cmode[:2] + 'bit'

    os.chdir(build_home + '/distributions')
    print('Cd ' + 'distributions')

    ftp = FTP()

    if opts.port != None:
        ftp.connect(host = opts.host, port = opts.port)
    else:
        ftp.connect(host = opts.host)

    if opts.user != None:
        ftp.login(user = opts.user, passwd = opts.passwd)
    else:
        ftp.login()

    if opts.dir == None:
        print "Error: no remote dir is given!"
        sys.exit(errnos.errors['args_invalid'])

    ftp.cwd(opts.dir)
    f = file(target_prefix + '.tar.gz', 'r')
    ftp.storbinary("STOR " + target_prefix + '.tar.gz', f)
    f.close()
    ftp.quit()
    ftp.close()

    os.chdir(build_home)
    print 'Upload [' + target_prefix + '.tar.gz] OK!'

def pack_create(buildc_home, opts):
    if opts.project == None:
        print "Error: no project name is given!"
        sys.exit(errnos.errors['args_invalid'])

    if os.path.exists(opts.project):
        print "Error: [" + opts.project + "] has already existed!"
        sys.exit(errnos.errors['file_or_dir_exists'])

    command.execute('mkdir -p ' + opts.project)
    command.execute('cp ' + buildc_home + '/templates/setup.cfg.in ' + opts.project + '/' + SETUP_CFG_FILE)
    command.execute('mkdir -p ' + opts.project + '/distributions')
    command.execute('mkdir -p ' + opts.project + '/src/app')
    command.execute('cp ' + buildc_home + '/templates/setup.py.in ' + opts.project + '/src/setup.py')
    command.execute('cp ' + buildc_home + '/templates/layout.cfg.in ' + opts.project + '/src/layout.cfg')
    command.execute('touch ' + opts.project + '/src/README')
    command.execute('mkdir -p ' + opts.project + '/src/deps')
    command.execute('mkdir -p ' + opts.project + '/src/conf')
    command.execute('mkdir -p ' + opts.project + '/src/others')
    command.execute('mkdir -p ' + opts.project + '/src/scripts')
    command.execute('cp ' + buildc_home + '/templates/deps_check.py.in ' + opts.project + '/src/scripts/deps_check.py')
    command.execute('cp ' + buildc_home + '/templates/env_gen.py.in ' + opts.project + '/src/scripts/env_gen.py')
    command.execute('touch ' + opts.project + '/src/scripts/__init__.py')

    print "Setup project [" + opts.project + "] create OK!"
    sys.exit(0)

def __copy_tree(src, dst, excludable_dirs=[], filters=["*"]):
    '''copy SRC directory into DST

    filters are like ["*.txt", "*.xml"]
    '''
    dest = os.path.expandvars(dst)
    srcf = os.path.expandvars(src)
    if not os.path.isdir(dest):
        os.makedirs(dest)

    names = os.listdir(srcf)
    for name in names:
        srcname = os.path.join(srcf, name)
        dstname = os.path.join(dest, name)
        if os.path.isdir(srcname):
            excludable_flag = False
            for excludable_dir in excludable_dirs:
                if name == excludable_dir:
                    excludable_flag = True
            if not excludable_flag:
                __copy_tree(srcname, dstname, excludable_dirs, filters)
    files = [glob.glob(os.path.join(srcf, fl)) for fl in filters]
    names = list(itertools.chain(*files))

    for name in names:
        if not os.path.isdir(name):
            try:
                shutil.copy2(name, dest)
            except IOError:
                command.execute('cp -r %s %s' % (name, dest))

def __copy_dependent_file(src_path, dst_path, tagfiles):
    if tagfiles == None or len(tagfiles) == 0:
        __copy_tree(src_path, dst_path, [".svn"], ["*"])
        print "copy %s to %s" % (src_path, dst_path)
        return

    if not os.path.isdir(dst_path):
        os.makedirs(dst_path)

    for tagfile in tagfiles:
        if not os.path.exists(src_path + '/' + tagfile):
            print 'Can not found ' + src_path + '/' + tagfile
            sys.exit(errnos.errors['file_not_found'])

        shutil.copyfile(src_path + '/' + tagfile, dst_path + '/' + tagfile)

    return

def __copy_dependent(dependence, external_repositories, build_home, cmode, dirname):
    if dirname != "include" and dirname != "lib" and dirname != "":
        print 'dirname args invalid'
        sys.exit(errnos.errors['args_invalid'])

    deps_libname    = None
    deps_libversion = None
    deps_tagfile    = None

    if len(dependence) == DEPENDENCE_LONG_NUM:
        (deps_libname, deps_libversion, deps_tagfile) = dependence
    elif len(dependence) == DEPENDENCE_SHORT_NUM:
        (deps_libname, deps_libversion) = dependence
    else:
        print 'dependences args invalid in setup.cfg'
        sys.exit(errnos.errors['args_invalid'])

    lib_flag = False

    for repository in external_repositories:
        (url, local_path, libs) = repository
        cache_path = os.path.abspath(os.path.expanduser(local_path))

        for (libname, libversion, tagfile) in libs:
            if deps_libname == libname and deps_libversion == libversion:
                lib_flag = True

                lib_path = cache_path + '/' + libname + '/' + libversion + '/' + env.cpu() + '_' + cmode[0:2] + '_' + env.os() + '/' + dirname
                deps_lib_path = build_home + '/src/deps/' + libname + '/' + libversion + '/' + env.cpu() + '_' + cmode[0:2] + '_' + env.os() + '/' + dirname

                if dirname == "lib":
                    __copy_dependent_file(lib_path, deps_lib_path, deps_tagfile)
                else:
                    __copy_dependent_file(lib_path, deps_lib_path, None)

                return

    if lib_flag == False:
        print('Can not found ' + deps_libname + '/' + deps_libversion + '/' + env.cpu() + '_' + cmode[0:2] + '_' + env.os() + \
            ' in external repositories.')
        sys.exit(errnos.errors['file_not_found'])

def __copy_dependent_include(dependence, external_repositories, build_home, cmode):
    __copy_dependent(dependence, external_repositories, build_home, cmode, "include")

def __copy_dependent_library(dependence, external_repositories, build_home, cmode):
    __copy_dependent(dependence, external_repositories, build_home, cmode, "lib")

def __copy_dependent_all(dependence, external_repositories, build_home, cmode):
    __copy_dependent(dependence, external_repositories, build_home, cmode, "")

def pack_component_deps(opts):
    build_home = os.getcwd()

    attribute_lists = __pack_init()
    distribution = attribute_lists.distribution
    source       = attribute_lists.source

    __do_clean(build_home)
    __do_component_deps_pack(build_home, source, distribution, opts.tag, opts.cmode)
    sys.exit(0)

def pack_component_src(buildc_home, opts):
    build_home = os.getcwd()

    attribute_lists = __pack_init()
    distribution = attribute_lists.distribution
    source       = attribute_lists.source

    __do_clean(build_home)
    __do_component_src_pack(buildc_home, build_home, source, distribution, opts.tag, opts.cmode)
    sys.exit(0)

def pack_component_all(buildc_home, opts):
    build_home = os.getcwd()

    attribute_lists = __pack_init()
    distribution = attribute_lists.distribution
    source       = attribute_lists.source

    __do_clean(build_home)
    __do_component_all_pack(buildc_home, build_home, source, distribution, opts.tag, opts.cmode)
    sys.exit(0)

def pack_build(opts):
    build_home = os.getcwd()

    attribute_lists = __pack_init()
    distribution = attribute_lists.distribution
    source       = attribute_lists.source

    __do_clean(build_home)

    if "dependences" in list(dir(attribute_lists)):
        dependences = attribute_lists.dependences

        dotrc = config.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print('Can not found ' + dotrc)
            print('Please run buildc init and then config .buildc.rc!')
            sys.exit(errnos.errors['conf_file_not_found'])
        c = config.load_config(dotrc)

        for dependence in dependences:
            __copy_dependent_library(dependence, c.external_repositories, build_home, opts.cmode)

    __do_pack(build_home, source, distribution, opts)
    sys.exit(0)

def pack_clean():
    build_home = os.getcwd()
    __do_clean(build_home)
    sys.exit(0)

def pack_upload(opts):
    build_home = os.getcwd()
    distribution, source = __pack_init()
    __do_upload(build_home, distribution, opts)
    sys.exit(0)

def pack_source(buildc_home, opts):
    if opts.component == "src":
        pack_component_src(buildc_home, opts)
    elif opts.component == "deps":
        pack_component_deps(opts)
    else:
        pack_component_all(buildc_home, opts)

    sys.exit(0)

if __name__ == '__main__':
    print 'pack'
