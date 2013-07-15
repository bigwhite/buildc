#! /usr/bin/env python
import os
import imp
from utils.config import Config

class Load(object):

    @staticmethod
    def load_setup_cfg(file_path):
        c = Config.load_config(file_path)
        return c

    @staticmethod
    def load_dot_buildc_rc(file_path):
        c = Config.load_config(file_path)
        return c

    @staticmethod
    def load_buildc_cfg(file_path, glo_var):
        cfg_file_path = file_path
        var_str       = glo_var
        if var_str == None or var_str == "":
            c = Config.load_config(cfg_file_path)
            return c
        else:
            var_name  = var_str[:var_str.find("=")]
            var_value = var_str[var_str.find("=")+1:]
            var_str = var_name + "=\"" + var_value + "\""

            c = imp.new_module('')
            code_obj = compile(var_str, "", 'exec')
            exec code_obj in c.__dict__

            f = open(cfg_file_path, 'rU')
            code_obj = compile(f.read(), "", 'exec')
            exec code_obj in c.__dict__
            f.close()

            return c
