#! /usr/bin/env python
import os
import sys
import time
from utils.util import Util
from utils.config import Config
from utils.system_local_info import SystemLocalInfo
from utils.errnos import Errors
from glo import Glo
from cache import Cache
from cache_svn_tree import CacheSvnTree

class Makerules(object):
    @staticmethod
    def __config(cmode, libs_depend, project_root_path = None):
        makerules_tpl = Glo.make_rules_tpl_path()

        if (SystemLocalInfo.system() == 'solaris'):
            this_awk = 'nawk'
        else:
            this_awk = 'gawk'

        c = Config.load_config(Glo.buildc_cfg_path())
        project_name, version, author = c.project
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        if project_root_path == None:
            topdir = os.path.abspath('./')
        else:
            topdir = project_root_path
        this_os  = SystemLocalInfo.system()
        this_cpu = SystemLocalInfo.cpu()
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
            libs     += (' -L $(' + libname + '_ROOT)' + '/lib')
            for archive in archives:
                libs += (' -l' + Glo.libname2compile_option(archive))
                if Glo.is_static_lib(archive):
                    static_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                    static_libs += (' -l' + Glo.libname2compile_option(archive))
                else:
                    dynamic_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                    dynamic_libs += (' -l' + Glo.libname2compile_option(archive))

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
                custom_libs += (' -l' + Glo.libname2compile_option(archive))
                if Glo.is_static_lib(archive):
                    if not len(libpath) == 0:
                        static_libs += (' -L ' + libpath)
                    static_libs += (' -l' + Glo.libname2compile_option(archive))
                else:
                    if not len(libpath) == 0:
                        dynamic_libs += (' -L ' + libpath)
                    dynamic_libs += (' -l' + Glo.libname2compile_option(archive))

        system_libs = ''
        system_libs_count = len(c.system_libs)
        for (libpath, archives) in c.system_libs:
            if not len(libpath) == 0:
                system_libs += (' -L ' + libpath)

            for archive in archives:
                system_libs += (' -l' + Glo.libname2compile_option(archive))

        cmd  = "sed -e '1,$ s/@project_name@/"     + project_name + "/g' " + makerules_tpl + '|'
        cmd += "sed -e '1,$ s/@author@/"           + author       + "/g'"  + '|'
        cmd += "sed -e '1,$ s/@date@/"             + date         + "/g'"  + '|'
        cmd += "sed -e '1,$ s/@topdir@/"           + Glo.add_backlash(topdir) + "#@topdir@/g'"  + '|'
        cmd += "sed -e '1,$ s/@os@/"               + this_os                          + "#@os@/g'"      + '|'
        cmd += "sed -e '1,$ s/@cpu@/"              + this_cpu                         + "#@cpu@/g'"     + '|'
        cmd += "sed -e '1,$ s/@cmode@/"            + cmode                            + "#@cmode@/g'"   + '|'
        cmd += "sed -e '1,$ s/@version@/"          + version                          + "#@version@/g'" + '|'
        cmd += "sed -e '1,$ s/@cc@/"               + Glo.add_backlash(cc)     + "#@cc@/g'"      + '|'
        cmd += "sed -e '1,$ s/@default_includes@/" + Glo.add_backlash(Glo.default_includes) + "#@default_includes@/g'" + '|'
        cmd += "sed -e '1,$ s/@default_libs@/"     + Glo.add_backlash(Glo.default_libs)     + "#@default_libs@/g'"     + '|'
        cmd += "sed -e '1,$ s/@custom_defs@/"      + custom_defs                                       + "#@custom_defs@/g'"      + '|'
        cmd += "sed -e '1,$ s/@custom_includes@/"  + Glo.add_backlash(custom_includes)         + "#@custom_includes@/g'"  + '|'
        cmd += "sed -e '1,$ s/@custom_libs@/"      + Glo.add_backlash(custom_libs)             + "#@custom_libs@/g'"      + '|'
        cmd += "sed -e '1,$ s/@system_libs@/"      + Glo.add_backlash(system_libs)             + "#@system_libs@/g'"      + '|'
        cmd += "sed -e '1,$ s/@static_libs@/"      + Glo.add_backlash(static_libs)             + "#@static_libs@/g'"      + '|'
        cmd += "sed -e '1,$ s/@dynamic_libs@/"     + Glo.add_backlash(dynamic_libs)            + "#@dynamic_libs@/g'"     + '|'
        cmd += "sed -e '1,$ s/@lib_includes@/"     + Glo.add_backlash(includes)                + "#@lib_includes@/g'"     + '|'
        cmd += "sed -e '1,$ s/@libs_depend@/"      + Glo.add_backlash(libs)                    + "#@libs_depend@/g'"      + '|'

        if lib_roots_count == 0:
            cmd += ("sed -e '1,$ s/@lib_roots@/#@lib_roots_end@/g'" + '|')
        else:
            cmd += (this_awk + " '{ sub(/@lib_roots@/, \"" + lib_roots + "\"); print }'" + '|')

        if custom_vars_count == 0:
            cmd += ("sed -e '1,$ s/@custom_vars@/#@custom_vars_end@/g'")
        else:
            cmd += (this_awk + " '{ sub(/@custom_vars@/, \"" + custom_vars + "\"); print }'")

        cmd += "> " + Glo.make_rules_path()

        Util.execute_and_output(cmd)

    @staticmethod
    def reconfig(cmode, libs_depend, project_root_path = None):
        makerules = Glo.make_rules_path()

        if (SystemLocalInfo.system() == 'solaris'):
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

        c = Config.load_config(Glo.buildc_cfg_path())
        project_name, version, author = c.project
        if project_root_path == None:
            topdir = os.path.abspath('./')
        else:
            topdir = project_root_path
        this_os = SystemLocalInfo.system()
        this_cpu = SystemLocalInfo.cpu()
        cmode = cmode

        if cmode == '64-bit':
            if this_os == 'solaris' and this_cpu == 'x86':
                cc = '/usr/sfw/bin/gcc -m64'
            else:
                cc = 'gcc -m64'
        else:
            cc = 'gcc -m32'

        libs         = ''
        includes     = ''
        static_libs  = ''
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
                libs += (' -l' + Glo.libname2compile_option(archive))
                if Glo.is_static_lib(archive):
                    static_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                    static_libs += (' -l' + Glo.libname2compile_option(archive))
                else:
                    dynamic_libs += (' -L $(' + libname + '_ROOT)' + '/lib')
                    dynamic_libs += (' -l' + Glo.libname2compile_option(archive))

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
                custom_libs += (' -l' + Glo.libname2compile_option(archive))
                if Glo.is_static_lib(archive):
                    if not len(libpath) == 0:
                        static_libs += (' -L ' + libpath)
                    static_libs += (' -l' + Glo.libname2compile_option(archive))
                else:
                    if not len(libpath) == 0:
                        dynamic_libs += (' -L ' + libpath)
                    dynamic_libs += (' -l' + Glo.libname2compile_option(archive))

        system_libs = ''
        system_libs_count = len(c.system_libs)
        for (libpath, archives) in c.system_libs:
            if not len(libpath) == 0:
                system_libs += (' -L ' + libpath)

            for archive in archives:
                system_libs += (' -l' + Glo.libname2compile_option(archive))

        cmd  = "sed -e '1,$ s/=.*@topdir@/= "  + Glo.add_backlash(topdir) + "#@topdir@/g' " + Glo.make_rules_path() + '|'
        cmd += "sed -e '1,$ s/=.*@os@/= "      + this_os                          + "#@os@/g'"      + '|'
        cmd += "sed -e '1,$ s/=.*@cpu@/= "     + this_cpu                         + "#@cpu@/g'"     + '|'
        cmd += "sed -e '1,$ s/=.*@cmode@/= "   + cmode                            + "#@cmode@/g'"   + '|'
        cmd += "sed -e '1,$ s/=.*@version@/= " + version                          + "#@version@/g'" + '|'
        cmd += "sed -e '1,$ s/=.*@cc@/= "               + Glo.add_backlash(cc)                      + "#@cc@/g'"                + '|'
        cmd += "sed -e '1,$ s/=.*@default_includes@/= " + Glo.add_backlash(Glo.default_includes) + "#@default_includes@/g'"  + '|'
        cmd += "sed -e '1,$ s/=.*@default_libs@/= "     + Glo.add_backlash(Glo.default_libs)     + "#@default_libs@/g'"      + '|'
        cmd += "sed -e '1,$ s/=.*@custom_includes@/= "  + Glo.add_backlash(custom_includes)         + "#@custom_includes@/g'"   + '|'
        cmd += "sed -e '1,$ s/=.*@custom_libs@/= "      + Glo.add_backlash(custom_libs)             + "#@custom_libs@/g'"       + '|'
        cmd += "sed -e '1,$ s/=.*@system_libs@/= "      + Glo.add_backlash(system_libs)             + "#@system_libs@/g'"       + '|'
        cmd += "sed -e '1,$ s/=.*@static_libs@/= "      + Glo.add_backlash(static_libs)             + "#@static_libs@/g'"       + '|'
        cmd += "sed -e '1,$ s/=.*@dynamic_libs@/= "     + Glo.add_backlash(dynamic_libs)            + "#@dynamic_libs@/g'"      + '|'
        cmd += "sed -e '1,$ s/=.*@custom_defs@/= "      + custom_defs                                       + "#@custom_defs@/g'"       + '|'
        cmd += "sed -e '1,$ s/=.*@lib_includes@/= "     + Glo.add_backlash(includes)                + "#@lib_includes@/g'"      + '|'
        cmd += "sed -e '1,$ s/=.*@libs_depend@/= "      + Glo.add_backlash(libs)                    + "#@libs_depend@/g'"       + '|'
        cmd += "sed -e '/^.*@lib_roots@/d'"                          + '|'
        cmd += "sed -e '1,$ s/^.*@lib_roots_end@/@lib_roots@/g'"     + '|'
        cmd += "sed -e '/^.*@custom_vars@/d'"                        + '|'
        cmd += "sed -e '1,$ s/^.*@custom_vars_end@/@custom_vars@/g'" + '|'

        if lib_roots_count == 0:
            cmd += ("sed -e '1,$ s/@lib_roots@/#@lib_roots_end@/g'" + '|')
        else:
            cmd += (this_awk + " '{ sub(/@lib_roots@/, \"" + lib_roots + "\"); print }'" + '|')

        if custom_vars_count == 0:
            cmd += ("sed -e '1,$ s/@custom_vars@/#@custom_vars_end@/g'")
        else:
            cmd += (this_awk + " '{ sub(/@custom_vars@/, \"" + custom_vars + "\"); print }'")

        cmd += "> " + Glo.make_rules_temp_path()

        Util.execute_and_output(cmd)
        Util.execute_and_output('mv ' + Glo.make_rules_temp_path() + ' ' + Glo.make_rules_path())

        print "Reconfig [" + makerules + "] OK!"

    @staticmethod
    def generate(cmode, libs_depend, project_root_path = None):
        makerules     = Glo.make_rules_path()
        makerules_tpl = Glo.make_rules_tpl_path()
        if not os.path.exists(makerules_tpl):
            print 'Can not found ['+ makerules_tpl + ']'
            sys.exit(Errors.tpl_file_not_found)

        print "Generate [" + makerules + "] ..."
        print "Config [" +  makerules  + "] ..."
        Makerules.__config(cmode, libs_depend, project_root_path)
        print "Config [" +  makerules  + "] OK!"
        print "Generate [" + makerules + "] OK!"

    @staticmethod
    def __check_buildc_cfg(cmode, lib_root_path = None):
        platform_info = SystemLocalInfo.cpu() + '_' + cmode[0:2] + '_' + SystemLocalInfo.system()

        buildc_cfg_path = Glo.buildc_cfg_path()

        buildc_rc = Config.load_config(Glo.dot_buildc_rc_path())
        buildc_cfg = Config.load_config(buildc_cfg_path)

        cache_libs = []
        dotrepository = Glo.dot_buildc_repository_path()

        cache_svn_tree = CacheSvnTree(buildc_rc.external_repositories)
        cache_svn_tree.import_format_tree_from_file(dotrepository)
        cache_svn_tree.get_cache_libs(None, cmode, cache_libs)

        libs_depend = []
        for (libname, libversion, archives) in buildc_cfg.external_libs:
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
                sys.exit(Errors.lib_not_found)

        return libs_depend

    @staticmethod
    def config_make(cmode, force_update, lib_root_path = None, project_root_path = None):
        buildc_cfg_path = Glo.buildc_cfg_path()
        if not os.path.exists(buildc_cfg_path):
            print 'Can not found buildc.cfg in current directory!'
            print 'Please run buildc config init to generate this file!'
            sys.exit(Errors.conf_file_not_found)

        if not os.path.exists(Glo.dot_buildc_rc_path()):
            print 'Can not found ~/.buildc.rc!'
            print 'Please run buildc init to generate this file!'
            sys.exit(Errors.conf_file_not_found)

        is_valid = Cache.cache_build_by_config(buildc_cfg_path, cmode, force_update)
        if is_valid == False:
            return False
        libs_depend = Makerules.__check_buildc_cfg(cmode, lib_root_path)

        if not os.path.exists(Glo.make_rules_path()):
            print 'Can not found Make.rules in current directory!'
            Makerules.generate(cmode, libs_depend, project_root_path)
        elif os.path.getsize(Glo.make_rules_path()) == 0:
            print 'The Make.rules file is empty in current directory!'
            Makerules.generate(cmode, libs_depend, project_root_path)
        else:
            Makerules.reconfig(cmode, libs_depend, project_root_path)
        return True
