#! /usr/bin/env python
import os
import sys
import time
import shutil
import glob
import itertools
from ftplib import FTP
from utils import options
from utils.errnos import Errors
from utils.util import Util
from utils.data_oper import DataOper
from utils.svn_local_oper import SvnLocalOper
from glo import Glo
from load import Load
from makerules import Makerules
from cache import Cache
from svn_tree import SvnTree

class Pack(object):
    SETUP_CFG_PATH = "./setup.cfg"

    @staticmethod
    def __pack_init():
        c = Load.load_setup_cfg(Pack.SETUP_CFG_PATH)
        return c

    @staticmethod
    def __build_component_deps(build_home, url, cmode, force_update):
        if not os.path.exists(build_home + os.sep + '.build'):
            Util.execute_and_output('mkdir -p ' + build_home + os.sep + '.build')
        os.chdir(build_home + os.sep + '.build')
        print "Create dir [.build] OK!"

        Util.execute_and_output('rm -rf ' + url[url.rindex("/")+1:])
        SvnLocalOper.export(url, None, None, Glo.source_svn_user(), Glo.source_svn_passwd(), False)
        print "Export [" + url + "] OK!"

        source_home = build_home + '/.build/' + url[url.rindex("/")+1:]
        os.chdir(source_home)
        print "Cd " + source_home

        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print('Can not found ' + dotrc)
            print('Please run buildc init and then config .buildc.rc!')
            sys.exit(Errors.conf_file_not_found)
        buildc_rc = Load.load_dot_buildc_rc(dotrc)

        buildc_cfg = Load.load_buildc_cfg(Glo.buildc_cfg_path(), Glo.var_str())

        is_valid = Cache.cache_build_by_external_libs(buildc_cfg.external_libs, cmode, force_update)
        if is_valid == False:
            os.chdir(build_home)
            print "Cd " + build_home
            return False

        dotrepository  = Glo.dot_buildc_repository_path()
        svn_tree = SvnTree()
        svn_tree.import_format_tree_from_file(dotrepository)
        for dependence in buildc_cfg.external_libs:
            Pack.__copy_dependent_all(dependence, svn_tree, buildc_rc, build_home, cmode)

        os.chdir(build_home)
        print "Cd " + build_home

        print 'Build deps [' + url + '] OK!'
        return True

    @staticmethod
    def __build_component_src(build_home, url, cmode, force_update):
        if not os.path.exists(build_home + os.sep + '.build'):
            Util.execute_and_output('mkdir -p ' + build_home + os.sep + '.build')
        os.chdir(build_home + os.sep + '.build')
        print "Create dir [.build] OK!"

        Util.execute_and_output('rm -rf ' + url[url.rindex("/")+1:])
        SvnLocalOper.export(url, None, None, Glo.source_svn_user(), Glo.source_svn_passwd(), False)
        print "Export [" + url + "] OK!"

        source_home = build_home + '/.build/' + url[url.rindex("/")+1:]
        os.chdir(source_home)
        print "Cd " + source_home

        is_valid = Makerules.config_make(cmode, force_update, "$(shell cd ../.; pwd)/deps", "$(shell cd .; pwd)")
        if is_valid == False:
            os.chdir(build_home)
            print "Cd " + build_home
            return False

        print "Config Make.rules OK!"
        Util.execute_and_output('rm -f buildc.cfg')
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
        f = open("configure", "w")
        f.write(cmd_str)
        f.close()
        Util.execute_and_output('chmod +x configure')
        print "Create configure OK!"

        os.chdir(build_home)
        print "Cd " + build_home

        print 'Build src [' + url + '] OK!'
        return True

    @staticmethod
    def __make(cmode):
        cmd_str = 'make CMODE=' + cmode + ' > make.log 2>&1'
        err = Util.execute_and_return(cmd_str)
        f = open('make.log', 'r')
        print f.read()
        f.close()
        if err != 0:
            print "Failed to execute cmd [%s], errno = [%d]" % (cmd_str, err)
            sys.exit(err)

    @staticmethod
    def __build_source(build_home, url, cmode, force_update, binary_prefix, pack_path):
        Util.execute_and_output('mkdir -p ' + build_home + os.sep + '.build')
        os.chdir(build_home + os.sep + '.build')
        print "Create dir [.build] OK!"

        SvnLocalOper.export(url, None, None, Glo.source_svn_user(), Glo.source_svn_passwd(), False)
        print "Export [" + url + "] OK!"

        source_home = build_home + os.sep + '.build' + os.sep + url[url.rindex("/")+1:]
        os.chdir(source_home)
        print "Cd " + source_home

        result = Makerules.config_make(cmode, force_update)
        if result == False:
            print "Config Make.rules Error!"
            os.chdir(build_home)
            print "Cd " + build_home
            return False

        print "Config Make.rules OK!"

        Pack.__make(cmode)
        print "Make OK!"

        if pack_path != "":
            des_path = build_home + os.sep + 'src' + os.sep + pack_path
            if not os.path.exists(des_path):
                os.mkdir(des_path)
            Util.execute_and_output('cp ' + binary_prefix + '* ' + des_path)
            print "Copy binary file to [" + build_home + os.sep + 'src' + os.sep + pack_path + ']' + " OK!"

        os.chdir(build_home)
        print "Cd " + build_home

        print 'Build source [' + url + '] OK!'
        return True

    @staticmethod
    def __build_version(build_home, source, cmode, tag):
        information_str = Glo.CPU + '-' + Glo.SYSTEM + '-' + cmode[:2] + 'bit';
        cur_time_str    = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        project_reversion_list = list()

        if tag != None:
            url = tag
            project_name   = url[url.rindex("/")+1:]
            revision_code = Pack.__get_svn_info_revision_code(url)
            project_reversion_list.append("project name: %s, revision: %s" % (project_name, revision_code))
        else:
            for index in range(len(source)):
                url = source[index]["trunk"]
                project_name   = url[url.rindex("/")+1:]
                revision_code = SvnLocalOper.get_svn_info_revision_code(url, None)
                project_reversion_list.append("project name: %s, revision: %s" % (project_name, revision_code))

        info_str  = ""
        info_str += "buildc version: " + options.VERSION + os.linesep
        info_str += "information: " + information_str + os.linesep
        info_str += "build time: "  + cur_time_str + os.linesep
        for index in range(len(project_reversion_list)):
            info_str += project_reversion_list[index] + os.linesep

        version_file = open(build_home + os.sep + 'src' + os.sep + 'VERSION', 'w')
        version_file.write(info_str)
        version_file.close()

        print('Build VERSION OK!')

    @staticmethod
    def __make_component_deps_package(build_home, distribution, cmode):
        os.chdir(build_home)

        Util.execute_and_output('mkdir -p ' + build_home + os.sep + '.package')
        print "Create dir [.package] OK!"

        target_prefix = distribution["packname"] + \
               '-' + distribution["version"] + \
               '-' + Glo.CPU + \
               '-' + Glo.SYSTEM + \
               '-' + cmode[:2] + 'bit' + '-deps' + Glo.PACK_SUFFIX

        src_path = build_home + os.sep + 'src' + os.sep + 'deps'
        dst_path = build_home + os.sep + '.package' + os.sep + target_prefix + os.sep + 'deps'
        DataOper.copy_tree_ex(src_path, dst_path, [".svn"], ["*"], True)
        print "copy %s to %s" % (src_path, dst_path)

        shutil.copy2(build_home + '/src/VERSION', build_home + '/.package/' + target_prefix)

        os.chdir(build_home + os.sep + '.package')
        print "Cd " + build_home + os.sep + '.package'

        Util.execute_and_output('tar cvf ' + target_prefix + '.tar ' + target_prefix)
        print 'Generate ' + target_prefix + '.tar' + ' OK!'

        Util.execute_and_output('gzip ' + target_prefix + '.tar')
        print('Zip ' + target_prefix + '.tar' + ' OK!')

        os.chdir(build_home)
        print('Cd ' + build_home)

        Util.execute_and_output('mv .package/' + target_prefix + '.tar.gz ' + 'distributions')
        Util.execute_and_output('rm -fr ' + build_home + '/.package')
        print 'Del [.package] OK!'

        print 'Make target [' + target_prefix + '.tar.gz] OK!'

    @staticmethod
    def __make_component_src_package(build_home, distribution, cmode):
        os.chdir(build_home)

        Util.execute_and_output('mkdir -p ' + build_home + os.sep + '.package')
        print "Create dir [.package] OK!"

        target_prefix = distribution["packname"] + \
               '-' + distribution["version"] + \
               '-' + Glo.CPU + \
               '-' + Glo.SYSTEM + \
               '-' + cmode[:2] + 'bit' + '-src' + Glo.PACK_SUFFIX

        src_path = build_home + '/.build'
        dst_path = build_home + '/.package/' + target_prefix
        DataOper.copy_tree_ex(src_path, dst_path, [".svn"], ["*"], True)
        print "copy %s to %s" % (src_path, dst_path)

        shutil.copy2(build_home + '/src/VERSION', build_home + '/.package/' + target_prefix)

        os.chdir(build_home + os.sep + '.package')
        print "Cd " + build_home + os.sep + '.package'

        Util.execute_and_output('tar cvf ' + target_prefix + '.tar ' + target_prefix)
        print 'Generate ' + target_prefix + '.tar' + ' OK!'

        Util.execute_and_output('gzip ' + target_prefix + '.tar')
        print('Zip ' + target_prefix + '.tar' + ' OK!')

        os.chdir(build_home)
        print('Cd ' + build_home)

        Util.execute_and_output('mv .package/' + target_prefix + '.tar.gz ' + 'distributions')
        Util.execute_and_output('rm -fr ' + build_home + '/.package')
        print 'Del [.package] OK!'

        print 'Make target [' + target_prefix + '.tar.gz] OK!'

    @staticmethod
    def __make_component_all_package(build_home, distribution, cmode):
        os.chdir(build_home)

        Util.execute_and_output('mkdir -p ' + build_home + os.sep + '.package')
        print "Create dir [.package] OK!"

        target_prefix = distribution["packname"] + \
               '-' + distribution["version"] + \
               '-' + Glo.CPU + \
               '-' + Glo.SYSTEM + \
               '-' + cmode[:2] + 'bit' + '-full' + Glo.PACK_SUFFIX

        src_path = build_home + os.sep + 'src' + os.sep + 'deps'
        dst_path = build_home + os.sep + '.package' + os.sep + target_prefix + os.sep + 'deps'
        DataOper.copy_tree_ex(src_path, dst_path, [".svn"], ["*"], True)
        print "copy %s to %s" % (src_path, dst_path)

        src_path = build_home + '/.build'
        dst_path = build_home + '/.package/' + target_prefix
        DataOper.copy_tree_ex(src_path, dst_path, [".svn"], ["*"], True)
        print "copy %s to %s" % (src_path, dst_path)
        shutil.copy2(build_home + '/src/VERSION', build_home + '/.package/' + target_prefix)

        os.chdir(build_home + os.sep + '.package')
        print "Cd " + build_home + os.sep + '.package'

        Util.execute_and_output('tar cvf ' + target_prefix + '.tar ' + target_prefix)
        print 'Generate ' + target_prefix + '.tar' + ' OK!'

        Util.execute_and_output('gzip ' + target_prefix + '.tar')
        print('Zip ' + target_prefix + '.tar' + ' OK!')

        os.chdir(build_home)
        print('Cd ' + build_home)

        Util.execute_and_output('mv .package/' + target_prefix + '.tar.gz ' + 'distributions')
        Util.execute_and_output('rm -fr ' + build_home + '/.package')
        print 'Del [.package] OK!'

        print 'Make target [' + target_prefix + '.tar.gz] OK!'

    @staticmethod
    def __make_package(build_home, distribution, cmode):
        os.chdir(build_home)

        Util.execute_and_output('mkdir -p ' + build_home + os.sep + '.package')
        print "Create dir [.package] OK!"

        target_prefix = distribution["packname"] + \
                '-' + distribution["version"] + \
                '-' + Glo.CPU + \
                '-' + Glo.SYSTEM + \
                '-' + cmode[:2] + 'bit' + Glo.PACK_SUFFIX

        src_path = build_home + os.sep + 'src'
        dst_path = build_home + os.sep + '.package' + os.sep + target_prefix
        DataOper.copy_tree_ex(src_path, dst_path, [".svn"], ["*"], True)
        print "copy %s to %s" % (src_path, dst_path)

        os.chdir(build_home + os.sep + '.package')
        print "Cd " + build_home + os.sep + '.package'

        Util.execute_and_output('tar cvf ' + target_prefix + '.tar ' + target_prefix)
        print 'Generate ' + target_prefix + '.tar' + ' OK!'

        Util.execute_and_output('gzip ' + target_prefix + '.tar')
        print('Zip ' + target_prefix + '.tar' + ' OK!')

        os.chdir(build_home)
        print('Cd ' + build_home)
        des_path = 'distributions'
        if not os.path.exists(des_path):
            os.mkdir(des_path)
        Util.execute_and_output('mv .package/' + target_prefix + '.tar.gz ' + des_path)
        Util.execute_and_output('rm -fr ' + build_home + '/.package')
        print 'Del [.package] OK!'

        print('Make target [' + target_prefix + '.tar.gz] OK!')

    @staticmethod
    def __do_clean(build_home):
        Util.execute_and_output('rm -fr ' + build_home + '/.build')
        print 'Clean [.build] OK!'

        Util.execute_and_output('rm -fr ' + build_home + '/.package')
        print 'Clean [.package] OK!'

        Util.execute_and_output('rm -f ' + build_home + '/src/app/*')
        print 'Clean [./src/app] OK!'

        Util.execute_and_output('rm -f ' + build_home + '/src/lib/*')
        print 'Clean [./src/lib] OK!'

        Util.execute_and_output('rm -fr ' + build_home + '/src/deps/*')
        print 'Clean [./src/deps] OK!'

        Util.execute_and_output('rm -f ' + build_home + '/distributions/*.tar.gz')
        print 'Clean [./distributions] OK!'

        return True

    @staticmethod
    def __do_component_deps_pack(build_home, source, distribution, cmode, tag, force_update):
        url = ''
        if tag != None:
            url = tag
            is_valid = Pack.__build_component_deps(build_home, url, cmode, force_update)
            if is_valid == False:
                return False
        else:
            for index in range(len(source)):
                url = source[index]["trunk"]
                is_valid = Pack.__build_component_deps(build_home, url, cmode, force_update)
                if is_valid == False:
                    return False

        Pack.__build_version(build_home, source, cmode, tag)

        Util.execute_and_output('rm -fr ' + build_home + '/.build')
        print 'Del [.build] OK!'

        Pack.__make_component_deps_package(build_home, distribution, cmode)
        return True

    @staticmethod
    def __do_component_src_pack(build_home, source, distribution, cmode, tag, force_update):
        url = ''
        if tag != None:
            url = tag
            is_valid = Pack.__build_component_src(build_home, url, cmode, force_update)
            if is_valid == False:
                return False
        else:
            for index in range(len(source)):
                url = source[index]["trunk"]
                is_valid = Pack.__build_component_src(build_home, url, cmode, force_update)
                if is_valid == False:
                    return False

        Pack.__build_version(build_home, source, cmode, tag)

        Pack.__make_component_src_package(build_home, distribution, cmode)

        Util.execute_and_output('rm -fr ' + build_home + '/.build')
        print 'Del [.build] OK!'
        return True

    @staticmethod
    def __do_component_all_pack(build_home, source, distribution, cmode, tag, force_update):
        url = ''
        if tag != None:
            url = tag
            is_valid = Pack.__build_component_deps(build_home, url, cmode, force_update)
            if is_valid == False:
                return False
            Pack.__build_component_src(build_home, url, cmode, force_update)
        else:
            for index in range(len(source)):
                url = source[index]["trunk"]
                is_valid = Pack.__build_component_deps(build_home, url, cmode, force_update)
                if is_valid == False:
                    return False
                Pack.__build_component_src(build_home, url, cmode, force_update)

        Pack.__build_version(build_home, source, cmode, tag)

        Pack.__make_component_all_package(build_home, distribution, cmode)

        Util.execute_and_output('rm -fr ' + build_home + '/.build')
        print 'Del [.build] OK!'
        return True

    @staticmethod
    def __do_pack(build_home, source, distribution, cmode, tag, force_update):
        url = ''

        pack_path = ""
        if tag != None:
            url       = tag
            pack_path = 'app'
            result = Pack.__build_source(build_home, url, cmode, force_update, source[0]["binary_prefix"], pack_path)
            if result == False:
                return False
        else:
            for index in range(len(source)):
                url = source[index]["trunk"]
                if dict(source[index]).get("pack_path") == None:
                    pack_path = 'app'
                else:
                    pack_path = source[index]["pack_path"]
                result = Pack.__build_source(build_home, url, cmode, force_update, source[index]["binary_prefix"], pack_path)
                if result == False:
                    return False

        Pack.__build_version(build_home, source, cmode, tag)

        Util.execute_and_output('rm -fr ' + build_home + '/.build')
        print('Del [.build] OK!')

        Pack.__make_package(build_home, distribution, cmode)
        return True

    @staticmethod
    def __do_upload(build_home, distribution, opts):
        target_prefix = distribution["packname"] + \
                '-' + distribution["version"] + \
                '-' + Glo.CPU + \
                '-' + Glo.SYSTEM + \
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
            sys.exit(Errors.args_invalid)

        ftp.cwd(opts.dir)
        f = file(target_prefix + '.tar.gz', 'r')
        ftp.storbinary("STOR " + target_prefix + '.tar.gz', f)
        f.close()
        ftp.quit()
        ftp.close()

        os.chdir(build_home)
        print 'Upload [' + target_prefix + '.tar.gz] OK!'

    @staticmethod
    def pack_create(project_path):
        if project_path == None:
            print "Error: no project name is given!"
            sys.exit(Errors.args_invalid)

        if os.path.exists(project_path):
            print "Error: [" + project_path + "] has already existed!"
            sys.exit(Errors.file_or_dir_exists)

        Util.execute_and_output('mkdir -p ' + project_path)
        Util.execute_and_output('cp ' + Glo.setup_cfg_tpl_path()  + ' ' + project_path + os.sep + 'setup.cfg')
        Util.execute_and_output('mkdir -p ' + project_path + os.sep + 'distributions')
        Util.execute_and_output('mkdir -p ' + project_path + os.sep + 'src' + os.sep + 'app')
        Util.execute_and_output('cp ' + Glo.setup_py_tpl_path()   + ' ' + project_path + os.sep + 'src' + os.sep + 'setup.py')
        Util.execute_and_output('cp ' + Glo.layout_cfg_tpl_path() + ' ' + project_path + os.sep + 'src' + os.sep + 'layout.cfg')
        Util.execute_and_output('touch '    + project_path + os.sep + 'src' + os.sep + 'README')
        Util.execute_and_output('mkdir -p ' + project_path + os.sep + 'src' + os.sep + 'deps')
        Util.execute_and_output('mkdir -p ' + project_path + os.sep + 'src' + os.sep + 'conf')
        Util.execute_and_output('mkdir -p ' + project_path + os.sep + 'src' + os.sep + 'others')
        Util.execute_and_output('mkdir -p ' + project_path + os.sep + 'src' + os.sep + 'scripts')
        Util.execute_and_output('cp ' + Glo.checkc_cfg_tpl_path() + ' ' + project_path + os.sep + 'src' + os.sep + 'scripts' + os.sep + 'deps_check.py')
        Util.execute_and_output('cp ' + Glo.env_gen_py_tpl_path() + ' ' + project_path + os.sep + 'src' + os.sep + 'scripts' + os.sep + 'env_gen.py')
        Util.execute_and_output('touch '    + project_path + os.sep + 'src' + os.sep + 'scripts' + os.sep + '__init__.py')

        return True

    @staticmethod
    def __copy_dependent_file(src_path, dst_path, tagfiles):
        if tagfiles == None or len(tagfiles) == 0:
            DataOper.copy_tree_ex(src_path, dst_path, [".svn"], ["*"], True)
            print "copy %s to %s" % (src_path, dst_path)
            return

        if not os.path.isdir(dst_path):
            os.makedirs(dst_path)

        for tagfile in tagfiles:
            if not os.path.exists(src_path + '/' + tagfile):
                print 'Can not found ' + src_path + '/' + tagfile
                sys.exit(Errors.file_or_dir_exists)

            shutil.copyfile(src_path + '/' + tagfile, dst_path + '/' + tagfile)
            print "copy %s to %s" % (src_path + '/' + tagfile, dst_path + '/' + tagfile)

        return

    @staticmethod
    def __copy_dependent(dependence, svn_tree, buildc_rc, build_home, cmode, dirname):
        if dirname != "include" and dirname != "lib" and dirname != "":
            print 'dirname args invalid'
            sys.exit(Errors.args_invalid)

        (dep_libname, dep_libversion, dep_tagfile) = Glo.get_dependent_name_and_version(dependence)

        h_child_item = svn_tree.get_root_item()
        while(h_child_item != None):
            svn_root_path = svn_tree.get_item_text(h_child_item)
            full_svn_path = svn_root_path + '|' + dep_libname + '|' + dep_libversion + '|' + Glo.CPU + '_' + cmode[0:2] + '_' + Glo.SYSTEM
            leaf_node = svn_tree.find_item(full_svn_path, '|', False, 1)
            if leaf_node != None:

                cache_root_path = Glo.get_local_cache_path(svn_root_path, buildc_rc.external_repositories)
                if cache_root_path == None:
                    print svn_root_path + ' does not exist in .buildc.rc'
                    sys.exit(Errors.conf_item_not_found)

                lib_path      = cache_root_path + '/'     + dep_libname + '/' + dep_libversion + '/' + Glo.CPU + '_' + cmode[0:2] + '_' + Glo.SYSTEM + '/' + dirname
                deps_lib_path = build_home + '/src/deps/' + dep_libname + '/' + dep_libversion + '/' + Glo.CPU + '_' + cmode[0:2] + '_' + Glo.SYSTEM + '/' + dirname

                if dirname == "lib":
                    Pack.__copy_dependent_file(lib_path, deps_lib_path, dep_tagfile)
                else:
                    Pack.__copy_dependent_file(lib_path, deps_lib_path, None)

                return

            h_child_item = svn_tree.get_next_sibling_item(h_child_item)

        print('Can not found ' + dep_libname + '/' + dep_libversion + '/' + Glo.CPU + '_' + cmode[0:2] + '_' + Glo.SYSTEM + \
            ' in external repositories.')
        sys.exit(Errors.file_or_dir_exists)

    @staticmethod
    def __copy_dependent_include(dependence, svn_tree, buildc_rc, build_home, cmode):
        Pack.__copy_dependent(dependence, svn_tree, buildc_rc, build_home, cmode, "include")

    @staticmethod
    def __copy_dependent_library(dependence, svn_tree, buildc_rc, build_home, cmode):
        Pack.__copy_dependent(dependence, svn_tree, buildc_rc, build_home, cmode, "lib")

    @staticmethod
    def __copy_dependent_all(dependence, svn_tree, buildc_rc, build_home, cmode):
        Pack.__copy_dependent(dependence, svn_tree, buildc_rc, build_home, cmode, "")

    @staticmethod
    def pack_component_deps(cmode, tag, force_update):
        build_home = os.getcwd()

        attribute_lists = Pack.__pack_init()
        distribution = attribute_lists.distribution
        source       = attribute_lists.source

        Pack.__do_clean(build_home)
        is_valid = Pack.__do_component_deps_pack(build_home, source, distribution, cmode, tag, force_update)
        return is_valid

    @staticmethod
    def pack_component_src(cmode, tag, force_update):
        build_home = os.getcwd()

        attribute_lists = Pack.__pack_init()
        distribution = attribute_lists.distribution
        source       = attribute_lists.source

        Pack.__do_clean(build_home)
        is_valid = Pack.__do_component_src_pack(build_home, source, distribution, cmode, tag, force_update)
        return is_valid

    @staticmethod
    def pack_component_all(cmode, tag, force_update):
        build_home = os.getcwd()

        attribute_lists = Pack.__pack_init()
        distribution = attribute_lists.distribution
        source       = attribute_lists.source

        Pack.__do_clean(build_home)
        is_valid = Pack.__do_component_all_pack(build_home, source, distribution, cmode, tag, force_update)
        return is_valid

    @staticmethod
    def pack_build(cmode, tag, force_update):
        build_home = os.getcwd()

        attribute_lists = Pack.__pack_init()
        distribution = attribute_lists.distribution
        source       = attribute_lists.source

        Pack.__do_clean(build_home)

        if "dependences" in list(dir(attribute_lists)):
            dependences = attribute_lists.dependences

            result = Cache.cache_build_by_external_libs(dependences, cmode, force_update)
            if result == False:
                return False

            dotrc = Glo.dot_buildc_rc_path()
            if not os.path.exists(dotrc):
                print('Can not found ' + dotrc)
                print('Please run buildc init and then config .buildc.rc!')
                sys.exit(Errors.conf_file_not_found)
            buildc_rc = Load.load_dot_buildc_rc(dotrc)

            dotrepository  = Glo.dot_buildc_repository_path()
            svn_tree = SvnTree()
            svn_tree.import_format_tree_from_file(dotrepository)
            for dependence in dependences:
                Pack.__copy_dependent_library(dependence, svn_tree, buildc_rc, build_home, cmode)

        result = Pack.__do_pack(build_home, source, distribution, cmode, tag, force_update)
        if result == False:
            return False
        return True

    @staticmethod
    def pack_clean():
        build_home = os.getcwd()
        Pack.__do_clean(build_home)
        return True

    @staticmethod
    def pack_upload(opts):
        build_home = os.getcwd()
        c = Pack.__pack_init()
        Pack.__do_upload(build_home, c.distribution, opts)
        return True

    @staticmethod
    def pack_source(cmode, tag, force_update, component):
        if component == "src":
            is_valid = Pack.pack_component_src(cmode, tag, force_update)
        elif component == "deps":
            is_valid = Pack.pack_component_deps(cmode, tag, force_update)
        else:
            is_valid = Pack.pack_component_all(cmode, tag, force_update)

        return is_valid
