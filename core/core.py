#! /usr/bin/env python
import os
import shutil
from glo import Glo
from cache import Cache
from makerules import Makerules
from pack import Pack

class Core(object):
    @staticmethod
    def init():
        dotrc = Glo.dot_buildc_rc_path()
        if os.path.exists(dotrc):
            print dotrc + ' has been already existed! Just config it!'
        else:
            buildc_rc_in = Glo.buildc_rc_tpl_path()
            if os.path.exists(buildc_rc_in):
                shutil.copyfile(buildc_rc_in, dotrc)
                print "Copy " + buildc_rc_in + " to " + dotrc + " OK!"
                print "Please config " +  dotrc  + " before you use other buildc commands!"

        return True

    @staticmethod
    def cache_init():
        return Cache.cache_init()

    @staticmethod
    def cache_upgrade():
        return Cache.cache_upgrade()

    @staticmethod
    def cache_update(cmode, ignore_error):
        if cmode == None:
            result = Cache.cache_update(Glo.BIT32, ignore_error)
            if result == False:
                return False
            result = Cache.cache_update(Glo.BIT64, ignore_error)
            if result == False:
                return False
        else:
            result = Cache.cache_update(cmode, ignore_error)
            if result == False:
                return False

        return True

    @staticmethod
    def cache_remove(cmode):
        if cmode == None:
            Cache.cache_remove()
        else:
            Cache.cache_remove_by_cmode(cmode)

        return True

    @staticmethod
    def config_init():
        buildc_cfg_in = Glo.buildc_cfg_tpl_path()

        buildc_cfg_path = Glo.buildc_cfg_path()
        if not os.path.exists(buildc_cfg_path):
            shutil.copyfile(buildc_cfg_in, buildc_cfg_path)
            print "Copy " + buildc_cfg_in + " to " + buildc_cfg_path + " OK!"
            print "Please config buildc.cfg before you use [buildc config make] command!"
        else:
            print 'buildc.cfg has been already existed! Just config it!'

        return True

    @staticmethod
    def config_make(cmode, force_update, lib_root_path = None, project_root_path = None):
        result = Cache.check_consistency()
        if result == False:
            return result

        return Makerules.config_make(cmode, force_update, lib_root_path, project_root_path)

    @staticmethod
    def pack_create(project_path):
        return Pack.pack_create(project_path)

    @staticmethod
    def pack_build(cmode, tag, force_update):
        result = Cache.check_consistency()
        if result == False:
            return result

        return Pack.pack_build(cmode, tag, force_update)

    @staticmethod
    def pack_clean():
        return Pack.pack_clean()

    @staticmethod
    def pack_upload(opts):
        return Pack.pack_upload(opts)

    @staticmethod
    def pack_source(cmode, tag, force_update, component):
        result = Cache.check_consistency()
        if result == False:
            return result

        return Pack.pack_source(cmode, tag, force_update, component)
