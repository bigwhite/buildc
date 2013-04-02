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
import time

from utils import errnos
from utils import config
from utils import env
from utils import default
from utils import command

def __add_backlash(str):
    return str.replace("/", "\/")

def __libname2compile_option(libname):
    return ((libname.replace("lib", "", 1)).replace(".a", "")).replace(".so", "")

def __is_static_lib(libfilename):
    return libfilename.endswith(".a")

def do_config(buildc_home, cmode, libs_depend, project_root_path = None):
    makerules_tpl = buildc_home + '/templates/' + 'Make.rules.in'

    if (env.os() == 'solaris'):
        this_awk = 'nawk'
    else:
        this_awk = 'gawk'

    c = config.load_config('buildc.cfg')
    project_name, version, author = c.project
    date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    if project_root_path == None:
        topdir = os.path.abspath('./')
    else:
        topdir = project_root_path
    this_os  = env.os()
    this_cpu = env.cpu()
    cmode = cmode

    if cmode == '64-bit':
        if this_os == 'solaris' and this_cpu == 'x86':
            cc = '/usr/sfw/bin/gcc -m64'
        else:
            cc = 'gcc -m64'
    else:
        cc = 'gcc -m32'

    libs = ''
    includes = ''
    static_libs = ''
    dynamic_libs = ''

    lib_roots = ''
    lib_roots_count = len(libs_depend)
    if not lib_roots_count == 0:
        last_lib = libs_depend[lib_roots_count - 1]
    for (libname, libversion, archives, libpath) in libs_depend:
        if libname == last_lib[0]:
            lib_roots += (libname + '_ROOT = ' + libpath + "#@lib_roots_end@")
        else:
            lib_roots += (libname + '_ROOT = ' + libpath + "#@lib_roots@\\n")

        includes += ('-I $(' + libname + '_ROOT)' + '/include ')
        libs += (' -L $(' + libname + '_ROOT)' + '/lib')
        for archive in archives:
            libs += (' -l' + __libname2compile_option(archive))
            if __is_static_lib(archive):
                static_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                static_libs += (' -l' + __libname2compile_option(archive))
            else:
                dynamic_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                dynamic_libs += (' -l' + __libname2compile_option(archive))

    custom_defs = ''
    custom_defs_count = len(c.custom_defs)
    for cdef in c.custom_defs:
        custom_defs += (cdef + ' ')

    custom_vars = ''
    custom_vars_count = len(c.custom_vars)
    for var in c.custom_vars:
        custom_vars += (var[0] + ' = ' + str(var[1]))
        if var == c.custom_vars[custom_vars_count - 1]:
            custom_vars += "#@custom_vars_end@"
        else:
            custom_vars += "#@custom_vars@\\n"

    custom_includes = ''
    custom_includes_count = len(c.custom_includes)
    for inc in c.custom_includes:
        custom_includes += ('-I ' + inc + ' ')

    custom_libs = ''
    custom_libs_count = len(c.custom_libs)
    for (libpath, archives) in c.custom_libs:
        if not len(libpath) == 0:
            custom_libs += (' -L ' + libpath)

        for archive in archives:
            custom_libs += (' -l' + __libname2compile_option(archive))
            if __is_static_lib(archive):
                if not len(libpath) == 0:
                    static_libs += (' -L ' + libpath)
                static_libs += (' -l' + __libname2compile_option(archive))
            else:
                if not len(libpath) == 0:
                    dynamic_libs += (' -L ' + libpath)
                dynamic_libs += (' -l' + __libname2compile_option(archive))

    system_libs = ''
    system_libs_count = len(c.system_libs)
    for (libpath, archives) in c.system_libs:
        if not len(libpath) == 0:
            system_libs += (' -L ' + libpath)

        for archive in archives:
            system_libs += (' -l' + __libname2compile_option(archive))

    cmd = "sed -e '1,$ s/@project_name@/" + project_name + "/g' " + makerules_tpl + '|'\
          + "sed -e '1,$ s/@author@/"+ author + "/g'"+ '|'\
          + "sed -e '1,$ s/@date@/"+ date + "/g'"+ '|'\
          + "sed -e '1,$ s/@topdir@/"+ __add_backlash(topdir) + "#@topdir@/g'"+ '|'\
          + "sed -e '1,$ s/@os@/"+ this_os + "#@os@/g'"+ '|'\
          + "sed -e '1,$ s/@cpu@/"+ this_cpu + "#@cpu@/g'"+ '|'\
          + "sed -e '1,$ s/@cmode@/"+ cmode + "#@cmode@/g'"+ '|'\
          + "sed -e '1,$ s/@version@/"+ version + "#@version@/g'"+ '|'\
          + "sed -e '1,$ s/@cc@/"+ __add_backlash(cc) + "#@cc@/g'" + '|' \
          + "sed -e '1,$ s/@default_includes@/"+ __add_backlash(default.default_includes) + "#@default_includes@/g'"+ '|'\
          + "sed -e '1,$ s/@default_libs@/"+ __add_backlash(default.default_libs) + "#@default_libs@/g'"+ '|'\
          + "sed -e '1,$ s/@custom_defs@/"+ custom_defs + "#@custom_defs@/g'"+ '|'\
          + "sed -e '1,$ s/@custom_includes@/"+ __add_backlash(custom_includes) + "#@custom_includes@/g'"+ '|'\
          + "sed -e '1,$ s/@custom_libs@/"+ __add_backlash(custom_libs) + "#@custom_libs@/g'" + '|'\
          + "sed -e '1,$ s/@system_libs@/"+ __add_backlash(system_libs) + "#@system_libs@/g'" + '|'\
          + "sed -e '1,$ s/@static_libs@/"+ __add_backlash(static_libs) + "#@static_libs@/g'" + '|'\
          + "sed -e '1,$ s/@dynamic_libs@/"+ __add_backlash(dynamic_libs) + "#@dynamic_libs@/g'" + '|'\
          + "sed -e '1,$ s/@lib_includes@/"+ __add_backlash(includes) + "#@lib_includes@/g'" + '|'\
          + "sed -e '1,$ s/@libs_depend@/"+ __add_backlash(libs) + "#@libs_depend@/g'" + '|'

    if lib_roots_count == 0:
        cmd += ("sed -e '1,$ s/@lib_roots@/#@lib_roots_end@/g'" + '|')
    else:
        cmd += (this_awk + " '{ sub(/@lib_roots@/, \"" + lib_roots + "\"); print }'" + '|')

    if custom_vars_count == 0:
        cmd += ("sed -e '1,$ s/@custom_vars@/#@custom_vars_end@/g'")
    else:
        cmd += (this_awk + " '{ sub(/@custom_vars@/, \"" + custom_vars + "\"); print }'")

    cmd += "> Make.rules"

    command.execute(cmd)

def reconfig(cmode, libs_depend, project_root_path = None):
    cur_dir = os.getcwd()
    makerules = cur_dir + '/Make.rules'

    if (env.os() == 'solaris'):
        this_awk = 'nawk'
    else:
        this_awk = 'gawk'
    print "Reconfig [" + makerules + "]..."

    #Warning if we can not found '@Generated by buildc@' embeded in the Make.rules
    f = open(makerules)
    s = f.read(1024)
    if s.find("@Generated by buildc@") == -1:
        print "Warning: Please make sure the Make.rules file is generated by buildc!"
    f.close()

    c = config.load_config('buildc.cfg')
    project_name, version, author = c.project
    if project_root_path == None:
        topdir = os.path.abspath('./')
    else:
        topdir = project_root_path
    this_os = env.os()
    this_cpu = env.cpu()
    cmode = cmode

    if cmode == '64-bit':
        if this_os == 'solaris' and this_cpu == 'x86':
            cc = '/usr/sfw/bin/gcc -m64'
        else:
            cc = 'gcc -m64'
    else:
        cc = 'gcc -m32'

    libs = ''
    includes = ''
    static_libs = ''
    dynamic_libs = ''

    lib_roots = ''
    lib_roots_count = len(libs_depend)
    if not lib_roots_count == 0:
        last_lib = libs_depend[lib_roots_count - 1]
    for (libname, libversion, archives, libpath) in libs_depend:
        if libname == last_lib[0]:
            lib_roots += (libname + '_ROOT = ' + libpath + "#@lib_roots_end@")
        else:
            lib_roots += (libname + '_ROOT = ' + libpath + "#@lib_roots@\\n")

        includes += ('-I $(' + libname + '_ROOT)' + '/include ')
        libs += (' -L $(' + libname + '_ROOT)' + '/lib')
        for archive in archives:
            libs += (' -l' + __libname2compile_option(archive))
            if __is_static_lib(archive):
                static_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                static_libs += (' -l' + __libname2compile_option(archive))
            else:
                dynamic_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                dynamic_libs += (' -l' + __libname2compile_option(archive))

    custom_defs = ''
    custom_defs_count = len(c.custom_defs)
    for cdef in c.custom_defs:
        custom_defs += (cdef + ' ')

    custom_vars = ''
    custom_vars_count = len(c.custom_vars)
    for var in c.custom_vars:
        custom_vars += (var[0] + ' = ' + str(var[1]))
        if var == c.custom_vars[custom_vars_count - 1]:
            custom_vars += "#@custom_vars_end@"
        else:
            custom_vars += "#@custom_vars@\\n"

    custom_includes = ''
    custom_includes_count = len(c.custom_includes)
    for inc in c.custom_includes:
        custom_includes += ('-I ' + inc + ' ')

    custom_libs = ''
    custom_libs_count = len(c.custom_libs)
    for (libpath, archives) in c.custom_libs:
        if not len(libpath) == 0:
            custom_libs += (' -L' + libpath)

        for archive in archives:
            custom_libs += (' -l' + __libname2compile_option(archive))
            if __is_static_lib(archive):
                if not len(libpath) == 0:
                    static_libs += (' -L ' + libpath)
                static_libs += (' -l' + __libname2compile_option(archive))
            else:
                if not len(libpath) == 0:
                    dynamic_libs += (' -L ' + libpath)
                dynamic_libs += (' -l' + __libname2compile_option(archive))

    system_libs = ''
    system_libs_count = len(c.system_libs)
    for (libpath, archives) in c.system_libs:
        if not len(libpath) == 0:
            system_libs += (' -L ' + libpath)

        for archive in archives:
            system_libs += (' -l' + __libname2compile_option(archive))
        
    cmd =   "sed -e '1,$ s/=.*@topdir@/= "+ __add_backlash(topdir) + "#@topdir@/g' "+ 'Make.rules' + '|'\
          + "sed -e '1,$ s/=.*@os@/= " + this_os +"#@os@/g'" + '|'\
          + "sed -e '1,$ s/=.*@cpu@/= " + this_cpu +"#@cpu@/g'" + '|'\
          + "sed -e '1,$ s/=.*@cmode@/= " + cmode +"#@cmode@/g'" + '|'\
          + "sed -e '1,$ s/=.*@version@/= " + version +"#@version@/g'" + '|'\
          + "sed -e '1,$ s/=.*@cc@/= " + __add_backlash(cc) +"#@cc@/g'" + '|'\
          + "sed -e '1,$ s/=.*@default_includes@/= "+ __add_backlash(default.default_includes) + "#@default_includes@/g'"+ '|'\
          + "sed -e '1,$ s/=.*@default_libs@/= "+ __add_backlash(default.default_libs) + "#@default_libs@/g'"+ '|'\
          + "sed -e '1,$ s/=.*@custom_includes@/= "+ __add_backlash(custom_includes) + "#@custom_includes@/g'"+ '|'\
          + "sed -e '1,$ s/=.*@custom_libs@/= "+ __add_backlash(custom_libs) + "#@custom_libs@/g'"+ '|'\
          + "sed -e '1,$ s/=.*@system_libs@/= "+ __add_backlash(system_libs) + "#@system_libs@/g'"+ '|'\
          + "sed -e '1,$ s/=.*@static_libs@/= "+ __add_backlash(static_libs) + "#@static_libs@/g'"+ '|'\
          + "sed -e '1,$ s/=.*@dynamic_libs@/= "+ __add_backlash(dynamic_libs) + "#@dynamic_libs@/g'"+ '|'\
          + "sed -e '1,$ s/=.*@custom_defs@/= " + custom_defs +"#@custom_defs@/g'" + '|'\
          + "sed -e '1,$ s/=.*@lib_includes@/= " + __add_backlash(includes) +"#@lib_includes@/g'" + '|'\
          + "sed -e '1,$ s/=.*@libs_depend@/= " + __add_backlash(libs) +"#@libs_depend@/g'" + '|'\
          + "sed -e '/^.*@lib_roots@/d'" + '|'\
          + "sed -e '1,$ s/^.*@lib_roots_end@/@lib_roots@/g'" + '|'\
          + "sed -e '/^.*@custom_vars@/d'" + '|'\
          + "sed -e '1,$ s/^.*@custom_vars_end@/@custom_vars@/g'" + '|'

    if lib_roots_count == 0:
        cmd += ("sed -e '1,$ s/@lib_roots@/#@lib_roots_end@/g'" + '|')
    else:
        cmd += (this_awk + " '{ sub(/@lib_roots@/, \"" + lib_roots + "\"); print }'" + '|')

    if custom_vars_count == 0:
        cmd += ("sed -e '1,$ s/@custom_vars@/#@custom_vars_end@/g'")
    else:
        cmd += (this_awk + " '{ sub(/@custom_vars@/, \"" + custom_vars + "\"); print }'")

    cmd += "> .Make.rules"

    command.execute(cmd)
    command.execute('mv .Make.rules Make.rules')

    print "Reconfig [" + makerules + "] OK!"

def generate(buildc_home, cmode, libs_depend, project_root_path = None):
    cur_dir = os.getcwd()
    makerules = cur_dir + '/Make.rules'
    makerules_tpl = buildc_home + '/templates/' + 'Make.rules.in'
    if not os.path.exists(makerules_tpl):
        print 'Can not found ['+ makerules_tpl + ']'
        sys.exit (errnos.errors['tpl_file_not_found'])
    else:
        print "Generate [" + makerules + "] ..."
        print "Config [" +  makerules  + "]... "
        do_config(buildc_home, cmode, libs_depend, project_root_path)
        print "Config [" +  makerules  + "] OK!"
        print "Generate [" + makerules + "] OK!"

if __name__ == '__main__':
    print ''
