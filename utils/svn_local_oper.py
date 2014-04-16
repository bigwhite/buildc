#!/usr/bin/env python
import re
import sys
from utils.util import Util

class SvnLocalOper(object):
    @staticmethod
    def export(svn_path, download_path = None, ignore_error = None, trunk_user = None, trunk_pass = None, ignore_hint = True):
        if download_path != None:
            Util.execute_and_output("rm -rf " + download_path)

        cmd_str  = "svn export " + "\"" + svn_path +"\""
        if download_path != None:
            cmd_str += " " + "\"" + download_path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"

        if not ignore_hint:
            print "command: " + cmd_str
        err = Util.execute_and_return(cmd_str)
        if err != 0:
            print "Failed to execute cmd [%s], errno = [%d]" % (cmd_str, err)
            if (ignore_error == None):
                sys.exit(err)
            return False
        return True

    @staticmethod
    def checkout(svn_path, download_path = None, ignore_error = None, trunk_user = None, trunk_pass = None, ignore_hint = True):
        if download_path != None:
            Util.execute_and_output("rm -rf " + download_path)

        cmd_str  = "svn checkout " + "\"" + svn_path +"\""
        if download_path != None:
            cmd_str += " " + "\"" + download_path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"

        if not ignore_hint:
            print "command: " + cmd_str
        err = Util.execute_and_return(cmd_str)
        if err != 0:
            print "Failed to execute cmd [%s], errno = [%d]" % (cmd_str, err)
            if (ignore_error == None):
                sys.exit(err)
            return False
        return True

    @staticmethod
    def update(download_path, ignore_error = None, trunk_user = None, trunk_pass = None):
        cmd_str  = "svn update " + "\"" + download_path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"

        err = Util.execute_and_return(cmd_str)
        if err != 0:
            print "Failed to execute cmd [%s], errno = [%d]" % (cmd_str, err)
            if (ignore_error == None):
                sys.exit(err)
            return False
        return True

    @staticmethod
    def get_svn_info_revision_code(path, ignore_error = None, trunk_user = None, trunk_pass = None):
        cmd_str  = "svn info " + "\"" + path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"
        svn_info_str = Util.execute_and_output(cmd_str, ignore_error)

        if svn_info_str == None:
            return ""
        if svn_info_str.startswith("svn: warning:"):
            return ""

        revision_code = re.findall(" (\d+)\n", svn_info_str)
        #revision_code: list of two elements, a revision number, a last changed rev

        if len(revision_code) == 0:
            return ""

        return revision_code[0]

    @staticmethod
    def get_svn_ls(svn_path, ignore_error = None, trunk_user = None, trunk_pass = None):
        cmd_str = "svn ls " + "\"" + svn_path +"\""
        if trunk_user != None and trunk_pass != None and \
            trunk_user != "" and trunk_pass != "":
            cmd_str += " " + "--username " + trunk_user
            cmd_str += " " + "--password " + trunk_pass
        cmd_str += " --no-auth-cache"

        svn_ls_str = Util.execute_and_output(cmd_str, ignore_error)
        if svn_ls_str == None:
            return []
        if svn_ls_str == "":
            return []
        item_nodes = str(svn_ls_str).split("\n")
        return item_nodes
