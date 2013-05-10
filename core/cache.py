#! /usr/bin/env python
import os
import sys
from utils.config import Config
from utils.util import Util
from utils.errnos import Errors
from glo import Glo
from svn_tree import SvnTree
from cache_svn_tree import CacheSvnTree

class Cache(object):

    @staticmethod
    def check_consistency():
        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print 'Can not found ~/.buildc.rc!'
            print 'Please run buildc init to generate this file!'
            sys.exit(Errors.conf_file_not_found)

        dotrepository  = Glo.dot_buildc_repository_path()
        buildc_rc      = Config.load_config(dotrc)
        cache_svn_tree = CacheSvnTree(buildc_rc.external_repositories)
        cache_svn_tree.import_format_tree_from_file(dotrepository)

        result = cache_svn_tree.check_tree_consistency()
        if result == False:
            return False

    @staticmethod
    def __create_dot_repository(dotrc, dotrepository):
        buildc_rc = Config.load_config(dotrc)

        cur_level = 1
        cache_svn_tree  = CacheSvnTree(buildc_rc.external_repositories)

        cache_svn_tree.check_local_cache_conflict()

        for repository in buildc_rc.external_repositories:
            svn_path = repository[0]
            print "\n===>Begin init repository [" + svn_path + ']'
            cache_svn_tree.build_tree(svn_path, cur_level, 3)
            print '<=== End init repository [' + svn_path + ']'

        cache_svn_tree.take_item_data_by_browse(None, SvnTree.default_empty_node, 1)
        cache_svn_tree.export_format_tree_to_file(dotrepository)

    @staticmethod
    def cache_init():
        dotrepository = Glo.dot_buildc_repository_path()
        if os.path.exists(dotrepository):
            print dotrepository + ' has been already existed!'
            return False

        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print 'Can not found ' + dotrc
            print 'Please run buildc init and then config .buildc.rc!'
            sys.exit(Errors.conf_file_not_found)

        Cache.__create_dot_repository(dotrc, dotrepository)
        return True

    @staticmethod
    def cache_upgrade():
        dotrepository = Glo.dot_buildc_repository_path()

        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print 'Can not found ' + dotrc
            print 'Please run buildc init and then config .buildc.rc!'
            sys.exit(Errors.conf_file_not_found)

        Cache.__create_dot_repository(dotrc, dotrepository)
        return True

    @staticmethod
    def cache_update(cmode, ignore_error):

        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print 'Can not found ' + dotrc
            print 'Please run buildc init and then config .buildc.rc!'
            sys.exit(Errors.conf_file_not_found)

        dotrepository = Glo.dot_buildc_repository_path()

        buildc_rc  = Config.load_config(dotrc)
        cache_svn_tree = CacheSvnTree(buildc_rc.external_repositories)
        cache_svn_tree.import_format_tree_from_file(dotrepository)

        result = cache_svn_tree.check_tree_consistency()
        if result == False:
            return False

        result = cache_svn_tree.is_new_tree(None)
        if result == True:
            print "Warning: local cache does not need to be updated."
            return False

        cache_svn_tree.update_tree(None, cmode, ignore_error)

        cache_svn_tree.export_format_tree_to_file(dotrepository)

    @staticmethod
    def cache_build_by_external_libs(external_libs, cmode, force_update = True):
        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print 'Can not found ' + dotrc
            print 'Please run buildc init and then config .buildc.rc!'
            sys.exit(Errors.conf_file_not_found)

        buildc_rc  = Config.load_config(dotrc)
        dotrepository  = Glo.dot_buildc_repository_path()
        cache_svn_tree = CacheSvnTree(buildc_rc.external_repositories)
        cache_svn_tree.import_format_tree_from_file(dotrepository)

        is_valid = True

        for dependence in external_libs:
            (dep_libname, dep_libversion) = Glo.get_dependent_name_and_version(dependence)[0:2]
            print '\n===>Begin build library [' + dep_libname + ' ' + dep_libversion + ']'
            result = cache_svn_tree.build_dependent(dep_libname, dep_libversion, cmode, force_update)
            print '<=== End build library [' + dep_libname + ' ' + dep_libversion + ']'
            if result == False:
                is_valid = False

        cache_svn_tree.export_format_tree_to_file(dotrepository)
        return is_valid

    @staticmethod
    def cache_build_by_config(buildc_cfg_path, cmode, force_update = True):
        buildc_cfg = Config.load_config(buildc_cfg_path)

        is_valid = Cache.cache_build_by_external_libs(buildc_cfg.external_libs, cmode, force_update)
        return is_valid

    @staticmethod
    def cache_remove_by_cmode(cmode):
        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print 'Can not found ' + dotrc
            print 'Please run buildc init and then config .buildc.rc!'
            sys.exit(Errors.conf_file_not_found)

        buildc_rc  = Config.load_config(dotrc)
        dotrepository = Glo.dot_buildc_repository_path()
        cache_svn_tree = CacheSvnTree(buildc_rc.external_repositories)
        cache_svn_tree.import_format_tree_from_file(dotrepository)

        cache_svn_tree.remove_tree(None, cmode)

        cache_svn_tree.export_format_tree_to_file(dotrepository)

    @staticmethod
    def cache_remove():
        dotrc = Glo.dot_buildc_rc_path()
        if not os.path.exists(dotrc):
            print 'Can not found ' + dotrc
            print 'Please run buildc init and then config .buildc.rc!'
            sys.exit(Errors.conf_file_not_found)

        buildc_rc = Config.load_config(dotrc)
        for repository in buildc_rc.external_repositories:
            svn_path   = repository[0]
            cache_path = Glo.get_local_cache_path(svn_path, buildc_rc.external_repositories)

            print "\n===>Begin remove local cache of repository [" + svn_path + ']'
            ret = Util.execute_and_return('rm -rf ' + cache_path)
            if (ret != 0):
                print 'Remove [' + cache_path + '] Failed!'
                sys.exit(ret)
            else:
                print 'Remove [' + cache_path + '] OK!'
            print "\n<=== End remove local cache of repository [" + svn_path + ']'

        dotrepository = Glo.dot_buildc_repository_path()
        svn_tree  = SvnTree()
        svn_tree.import_format_tree_from_file(dotrepository)
        svn_tree.take_item_data_by_browse(None, SvnTree.set_empty_node, 1)
        svn_tree.export_format_tree_to_file(dotrepository)
