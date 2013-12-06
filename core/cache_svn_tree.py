#! /usr/bin/env python
import os
import sys
from utils.errnos import Errors
from utils.util import Util
from utils.svn_local_oper import SvnLocalOper
from utils.datastruct.treebybintree import TreeByBinTree
from glo import Glo
from svn_tree import SvnTree

class CacheSvnTree(SvnTree):
    def __init__(self, repositories):
        SvnTree.__init__(self)
        self.__repositories = repositories

    def get_cache_libs(self, item, cmode, cache_libs):
        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_child_item = self.get_child_item(item)

        while(h_child_item != None):
            if (self.get_child_item(h_child_item) == None):
                item_text = self.get_item_text(h_child_item)
                if item_text == Glo.CPU + '_' + cmode[0:2] + '_' + Glo.SYSTEM:
                    full_svn_path = self.get_full_path(h_child_item, '|')[0]

                    svn_root_path = full_svn_path[:str(full_svn_path).find('|')]
                    cache_root_path = Glo.get_local_cache_path(svn_root_path, self.__repositories)
                    if cache_root_path == None:
                        print svn_root_path + ' does not exist in .buildc.rc'
                        sys.exit(Errors.conf_item_not_found)

                    full_cache_path = cache_root_path + '|' + full_svn_path[str(full_svn_path).find('|')+1:]
                    real_cache_path = str(full_cache_path).replace('|', '/')
                    real_cache_version_path = real_cache_path[:str(real_cache_path).rfind('/')]
                    real_cache_name_path    = real_cache_version_path[:str(real_cache_version_path).rfind('/')]
                    cache_libversion = real_cache_version_path[str(real_cache_version_path).rfind('/')+1:]
                    cache_libname    = real_cache_name_path[str(real_cache_name_path).rfind('/')+1:]
                    cache_libs.append((cache_libname, cache_libversion, os.path.expanduser(cache_root_path)))

            self.get_cache_libs(h_child_item, cmode, cache_libs)
            h_child_item = self.get_next_sibling_item(h_child_item)

    def check_local_cache_conflict(self):
        url        = None
        cache_path = None

        tree = TreeByBinTree()
        for repository in self.__repositories:
            if len(repository) == Glo.ONE_TUPLE:
                url = repository[0]

                cache_path = '~/buildc_libs/'
                cache_path += url[str(url).rfind('/')+1:]
                cache_path = os.path.abspath(os.path.expanduser(cache_path))
            elif len(repository) == Glo.TWO_TUPLE or len(repository) == Glo.THREE_TUPLE:
                (url, cache_path) = (repository[0], repository[1])
                cache_path = os.path.abspath(os.path.expanduser(cache_path))
            else:
                print 'tuple number invalid in .buildc.rc'
                sys.exit(Errors.tuple_number_invalid)

            pre_item = tree.find_item(cache_path, '/', False, 1)
            if pre_item == None:
                cur_item = tree.add_item(cache_path, '/', True, False, False)
                cur_item.data = url
            else:
                print 'Warning:'
                print '    current path mapping ' + url + ' to ' + cache_path
                print '    previous path mapping ' + pre_item.data + ' to ' + cache_path
                print '    map the same path.'

    def check_tree_consistency(self):
        url = None
        presence_consistency_flag = True
        is_only                   = True
        is_equal                  = True
        order_consistency_flag    = True

        url_list = list()
        for repository in self.__repositories:
            url = repository[0]
            root_item = self.find_item(url, '|', False, 1)
            if root_item == None:
                print "Error: svn path " + url + " does not exist in .buildc.repository."
                presence_consistency_flag = False
            else:
                if url not in url_list:
                    url_list.append(url)
                else:
                    is_only = False
                    print "Error: svn path " + url + " is repeated in .buildc.rc."

        index = 0
        h_child_item = self.get_root_item()
        if len(url_list) == 0:
            if h_child_item == None:
                pass
            else:
                is_equal = False
        else:
            count = 0
            while(h_child_item != None):
                count += 1
                item_text = self.get_item_text(h_child_item)
                if index < len(url_list) and url_list[index] == item_text:
                    index += 1
                else:
                    pass

                h_child_item = self.get_next_sibling_item(h_child_item)

            if len(url_list) != count:
                is_equal = False
            if index != len(url_list):
                order_consistency_flag = False

        if is_equal == False:
            print "Error: svn paths had to be removed in .buildc.rc."
        if order_consistency_flag == False:
            print "Error: svn paths had to be reordered in .buildc.rc."

        if False in (presence_consistency_flag, is_only, is_equal, order_consistency_flag):
            print "Please use [buildc cache upgrade] to update the libraries map."
            return False
        else:
            return True

    def is_new_tree(self, item):
        return SvnTree.is_new_tree(self, item)

    def __adjust_tree(self):
        layer_count  = None
        item_text    = None
        element_list = None
        parent_item  = None
        items_address_list = list()
        self.take_items(None, items_address_list, 2, 1, 0)
        for item_address in items_address_list:
            layer_count = self.get_layer_count(item_address)
            if layer_count >= 4:
                item_text = self.get_item_text(item_address)
                element_list = str(item_text).split("_")
                if (len(element_list) == 3 and \
                    (element_list[0] == "sparc" or element_list[0] == "x86") and \
                    (element_list[1] == "32" or element_list[1] == "64") and \
                    (element_list[2] == "linux" or element_list[2] == "solaris")):
                    continue

            result = True
            item = item_address
            while (result == True):
                parent_item = self.get_parent_item(item)
                result = self.delete_leaf_node(item, False)
                item = parent_item
                if item == None:
                    break

    def build_tree(self, search_path, cur_level, level_max = -1):
        SvnTree.build_tree(self, search_path, cur_level, level_max)
        self.__adjust_tree()

    def update_tree(self, item, cmode, ignore_error):
        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_child_item = self.get_child_item(item)

        while(h_child_item != None):
            if (self.get_child_item(h_child_item) == None):
                item_text = self.get_item_text(h_child_item)
                if str(item_text).find("_" + cmode[0:2] + "_") != -1:
                    full_svn_path = self.get_full_path(h_child_item, '|')[0]
                    real_svn_path = str(full_svn_path).replace('|', '/')

                    svn_root_path = full_svn_path[:str(full_svn_path).find('|')]
                    cache_root_path = Glo.get_local_cache_path(svn_root_path, self.__repositories)
                    if cache_root_path == None:
                        print svn_root_path + ' does not exist in .buildc.rc'
                        sys.exit(Errors.conf_item_not_found)

                    full_cache_path = cache_root_path + '|' + full_svn_path[str(full_svn_path).find('|')+1:]
                    real_cache_path = str(full_cache_path).replace('|', '/')
                    real_cache_version_path = real_cache_path[:str(real_cache_path).rfind('/')]
                    real_cache_name_path    = real_cache_version_path[:str(real_cache_version_path).rfind('/')]
                    dep_libname    = real_cache_name_path[str(real_cache_name_path).rfind('/')+1:]
                    dep_libversion = real_cache_version_path[str(real_cache_version_path).rfind('/')+1:]
                    svn_revision_code = SvnLocalOper.get_svn_info_revision_code(real_svn_path, True)
                    if h_child_item.data == 'none':
                        if os.path.exists(real_cache_path):
                            Util.execute_and_return("rm -rf " + real_cache_path)

                    else:
                        if not os.path.exists(real_cache_path):
                            print 'library [' + dep_libname + ' ' + dep_libversion + '] does not exist!'
                            print 'Checkout [' + real_svn_path + ']...'
                            SvnLocalOper.checkout(real_svn_path, real_cache_path, ignore_error)
                            print 'Checkout [' + real_svn_path + '] OK!'
                        else:
                            cache_revision_code = SvnLocalOper.get_svn_info_revision_code(real_cache_path, None)
                            if svn_revision_code != cache_revision_code:
                                print 'Update [' + dep_libname + ' ' + dep_libversion + ']...'
                                SvnLocalOper.update(real_cache_path, ignore_error)
                                print 'Update [' + dep_libname + ' ' + dep_libversion + '] OK!'

                        h_child_item.data = svn_revision_code

            self.update_tree(h_child_item, cmode, ignore_error)
            h_child_item = self.get_next_sibling_item(h_child_item)

    def build_dependent(self, dep_libname, dep_libversion, cmode, force_update = True):
        lib_flag = False

        h_child_item = self.get_root_item()
        while(h_child_item != None):
            svn_root_path = self.get_item_text(h_child_item)
            full_svn_path = svn_root_path + '|' + dep_libname + '|' + dep_libversion + '|' + Glo.CPU + '_' + cmode[0:2] + '_' + Glo.SYSTEM
            real_svn_path = str(full_svn_path).replace('|', '/')
            leaf_node = self.find_item(full_svn_path, '|', False, 1)
            if leaf_node != None:
                lib_flag = True

                cache_root_path = Glo.get_local_cache_path(svn_root_path, self.__repositories)
                if cache_root_path == None:
                    print svn_root_path + ' does not exist in .buildc.rc'
                    sys.exit(Errors.conf_item_not_found)

                full_cache_path = cache_root_path + '|' + dep_libname + '|' + dep_libversion + '|' + Glo.CPU + '_' + cmode[0:2] + '_' + Glo.SYSTEM
                real_cache_path = str(full_cache_path).replace('|', '/')
                svn_revision_code = SvnLocalOper.get_svn_info_revision_code(real_svn_path, True)
                if svn_revision_code == "":
                    return False
                if leaf_node.data == 'none':
                    if os.path.exists(real_cache_path):
                        Util.execute_and_return("rm -rf " + real_cache_path)

                    print 'library [' + dep_libname + ' ' + dep_libversion + '] does not exist!'
                    print 'Checkout [' + real_svn_path + ']...'
                    result = SvnLocalOper.checkout(real_svn_path, real_cache_path, True)
                    if result == False:
                        return False
                    print 'Checkout [' + real_svn_path + '] OK!'
                    leaf_node.data = svn_revision_code
                else:
                    if not os.path.exists(real_cache_path):
                        print 'library [' + dep_libname + ' ' + dep_libversion + '] does not exist!'
                        print 'Checkout [' + real_svn_path + ']...'
                        result = SvnLocalOper.checkout(real_svn_path, real_cache_path, True)
                        if result == False:
                            return False
                        print 'Checkout [' + real_svn_path + '] OK!'
                        leaf_node.data = svn_revision_code
                    else:
                        if force_update:
                            cache_revision_code = SvnLocalOper.get_svn_info_revision_code(real_cache_path, True)
                            if cache_revision_code == "":
                                return False
                            if svn_revision_code != cache_revision_code:
                                print 'Update [' + dep_libname + ' ' + dep_libversion + ']...'
                                result = SvnLocalOper.update(real_cache_path, True)
                                if result == False:
                                    return False
                                print 'Update [' + dep_libname + ' ' + dep_libversion + '] OK!'
                            leaf_node.data = svn_revision_code
                        else:
                            print "Do not use force_update, skip the update check!"
                            pass

                break

            h_child_item = self.get_next_sibling_item(h_child_item)

        if lib_flag == True:
            return True
        else:
            return False

    def remove_tree(self, item, cmode):
        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_child_item = self.get_child_item(item)

        while(h_child_item != None):
            if (self.get_child_item(h_child_item) == None):
                item_text = self.get_item_text(h_child_item)
                if str(item_text).find("_" + cmode[0:2] + "_") != -1:
                    full_svn_path = self.get_full_path(h_child_item, '|')[0]

                    svn_root_path = full_svn_path[:str(full_svn_path).find('|')]
                    cache_root_path = Glo.get_local_cache_path(svn_root_path, self.__repositories)
                    if cache_root_path == None:
                        print svn_root_path + ' does not exist in .buildc.rc'
                        sys.exit(Errors.conf_item_not_found)

                    full_cache_path = cache_root_path + '|' + full_svn_path[str(full_svn_path).find('|')+1:]
                    real_cache_path = str(full_cache_path).replace('|', '/')
                    real_cache_version_path = real_cache_path[:str(real_cache_path).rfind('/')]
                    real_cache_name_path    = real_cache_version_path[:str(real_cache_version_path).rfind('/')]
                    if h_child_item.data == 'none':
                        if os.path.exists(real_cache_path):
                            ret = Util.execute_and_return("rm -rf " + real_cache_path + "/.svn " + real_cache_path)
                            if (ret != 0):
                                print 'Remove [' + real_cache_path + '] Failed!'
                                sys.exit(ret)
                            else:
                                print 'Remove [' + real_cache_path + '] OK!'
                    else:
                        if not os.path.exists(real_cache_path):
                            pass
                        else:
                            ret = Util.execute_and_return("rm -rf " + real_cache_path + "/.svn " + real_cache_path)
                            if (ret != 0):
                                print 'Remove [' + real_cache_path + '] Failed!'
                                sys.exit(ret)
                            else:
                                print 'Remove [' + real_cache_path + '] OK!'

                    if os.path.exists(real_cache_version_path):
                        if len(os.listdir(real_cache_version_path)) == 0:
                            os.rmdir(real_cache_version_path)
                    if os.path.exists(real_cache_name_path):
                        if len(os.listdir(real_cache_name_path)) == 0:
                            os.rmdir(real_cache_name_path)
                    if os.path.exists(cache_root_path):
                        if len(os.listdir(cache_root_path)) == 0:
                            os.rmdir(cache_root_path)

                    h_child_item.data = 'none'

            self.remove_tree(h_child_item, cmode)
            h_child_item = self.get_next_sibling_item(h_child_item)
