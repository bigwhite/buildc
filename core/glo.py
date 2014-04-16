#! /usr/bin/env python
import os
import sys
from utils.errnos import Errors
from utils.util import Util
from utils.system_local_info import SystemLocalInfo

class Glo(object):
    default_includes = ''
    default_libs     = ''

    DOT_BUILDC_RC = Util.usr_home() + os.sep + '.buildc.rc'
    DOT_BUILDC_REPOSITORY = Util.usr_home() + os.sep + '.buildc.repository'
    BUILDC_CFG_PATH = './buildc.cfg'
    MAKE_RULES_PATH = './Make.rules'
    MAKE_RULES_TEMP_PATH = './.Make.rules'

    core_home   = os.path.dirname(os.path.realpath(__file__))
    buildc_home = core_home[:str(core_home).rfind(os.sep)]
    MAKERULES_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'Make.rules.in'
    SETUP_CFG_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'setup.cfg.in'
    SETUP_PY_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'setup.py.in'
    LAYOUT_CFG_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'layout.cfg.in'
    CHECKC_CFG_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'checkc.cfg.in'
    ENV_GEN_PY_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'env_gen.py.in'
    BUILDC_CFG_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'buildc.cfg.in'
    BUILDC_RC_TPL_PATH = buildc_home + os.sep + 'templates' + os.sep + 'buildc.rc.in'

    ONE_TUPLE   = 1
    TWO_TUPLE   = 2
    THREE_TUPLE = 3

    BIT32 = '32-bit'
    BIT64 = '64-bit'
    CPU    = SystemLocalInfo.cpu()
    SYSTEM = SystemLocalInfo.system()
    PACK_SUFFIX = ""

    VAR_STR = ""
    SOURCE_SVN_USER   = None
    SOURCE_SVN_PASSWD = None

    @staticmethod
    def var_str():
        return Glo.VAR_STR

    @staticmethod
    def source_svn_user():
        return Glo.SOURCE_SVN_USER

    @staticmethod
    def source_svn_passwd():
        return Glo.SOURCE_SVN_PASSWD

    @staticmethod
    def dot_buildc_rc_path():
        return Glo.DOT_BUILDC_RC

    @staticmethod
    def dot_buildc_repository_path():
        return Glo.DOT_BUILDC_REPOSITORY

    @staticmethod
    def buildc_cfg_path():
        return Glo.BUILDC_CFG_PATH

    @staticmethod
    def make_rules_path():
        return Glo.MAKE_RULES_PATH

    @staticmethod
    def make_rules_temp_path():
        return Glo.MAKE_RULES_TEMP_PATH

    @staticmethod
    def make_rules_tpl_path():
        return Glo.MAKERULES_TPL_PATH

    @staticmethod
    def setup_cfg_tpl_path():
        return Glo.SETUP_CFG_TPL_PATH

    @staticmethod
    def setup_py_tpl_path():
        return Glo.SETUP_PY_TPL_PATH

    @staticmethod
    def layout_cfg_tpl_path():
        return Glo.LAYOUT_CFG_TPL_PATH

    @staticmethod
    def checkc_cfg_tpl_path():
        return Glo.CHECKC_CFG_TPL_PATH

    @staticmethod
    def env_gen_py_tpl_path():
        return Glo.ENV_GEN_PY_TPL_PATH

    @staticmethod
    def buildc_cfg_tpl_path():
        return Glo.BUILDC_CFG_TPL_PATH

    @staticmethod
    def buildc_rc_tpl_path():
        return Glo.BUILDC_RC_TPL_PATH

    @staticmethod
    def add_backlash(string):
        return string.replace("/", "\/")

    @staticmethod
    def libname2compile_option(libname):
        return ((libname.replace("lib", "", 1)).replace(".a", "")).replace(".so", "")

    @staticmethod
    def is_static_lib(libfilename):
        return libfilename.endswith(".a")

    @staticmethod
    def get_dependent_name_and_version(dependence):
        dep_libname    = None
        dep_libversion = None
        dep_tagfile    = None

        if len(dependence) == Glo.THREE_TUPLE:
            (dep_libname, dep_libversion, dep_tagfile) = dependence
        elif len(dependence) == Glo.TWO_TUPLE:
            (dep_libname, dep_libversion) = dependence
        else:
            print 'dependence args invalid'
            sys.exit(Errors.args_invalid)

        return (dep_libname, dep_libversion, dep_tagfile)

    @staticmethod
    def get_repository(item):
        repository = None
        if len(item) == Glo.ONE_TUPLE:
            if isinstance(item[0], tuple):
                repository = item[0]
            else:
                repository = item
        elif len(item) == Glo.TWO_TUPLE:
            if isinstance(item[0], tuple):
                repository = item[0]
            else:
                repository = item
        else:
            print 'tuple number invalid in .buildc.rc'
            sys.exit(Errors.tuple_number_invalid)

        return repository

    @staticmethod
    def get_local_cache_path(svn_path, repositories):
        url        = None
        cache_path = None

        for item in repositories:
            repository = Glo.get_repository(item)

            if len(repository) == Glo.ONE_TUPLE:
                url = repository[0]
                if svn_path == url:
                    cache_path = '~/buildc_libs/'
                    cache_path += url[str(url).rfind('/')+1:]
                    return os.path.abspath(os.path.expanduser(cache_path))
            elif len(repository) == Glo.TWO_TUPLE or len(repository) == Glo.THREE_TUPLE:
                (url, cache_path) = (repository[0], repository[1])
                if svn_path == url:
                    return os.path.abspath(os.path.expanduser(cache_path))
            else:
                print 'tuple number invalid in .buildc.rc'
                sys.exit(Errors.tuple_number_invalid)

        return None
