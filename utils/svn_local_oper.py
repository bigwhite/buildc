#!/usr/bin/env python
import re
from utils.util import Util

class SvnLocalOper(object):
    @staticmethod
    def export(svn_path, download_path, ignore_error = None, trunk_user = None, trunk_pass = None):
        Util.execute_and_output("rm -rf " + download_path)

        cmd_str  = "svn export " + "\"" + svn_path +"\""
        cmd_str += " " + "\"" + download_path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"

        Util.execute_and_output(cmd_str, ignore_error)

    @staticmethod
    def checkout(svn_path, download_path, ignore_error = None, trunk_user = None, trunk_pass = None):
        Util.execute_and_output("rm -rf " + download_path)

        cmd_str  = "svn checkout " + "\"" + svn_path +"\""
        cmd_str += " " + "\"" + download_path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"

        Util.execute_and_output(cmd_str, ignore_error)

    @staticmethod
    def update(download_path, ignore_error = None, trunk_user = None, trunk_pass = None):
        cmd_str  = "svn update " + "\"" + download_path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"

        Util.execute_and_output(cmd_str, ignore_error)

    @staticmethod
    def get_svn_info_revision_code(path, ignore_error = None):
        svn_info_str = str(Util.execute_and_output('svn info ' + path, ignore_error))

        revision_code = re.findall(" (\d+)\n", svn_info_str)
        #revision_code: list of two elements, a revision number, a last changed rev

        if len(revision_code) == 0:
            return ""

        return revision_code[0]
