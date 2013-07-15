#! /usr/bin/env python
from utils.util import Util
from utils.datastruct.treebybintree import TreeByBinTree

class SvnTree(TreeByBinTree):
    def export_node_function(self, tree_str, node_data):
        if node_data == None:
            TreeByBinTree.str_msg += tree_str
        else:
            TreeByBinTree.str_msg += tree_str + "    " + node_data

    @staticmethod
    def import_node_function(item_str):
        item_name = None
        item_data = None
        delimiter = '    '
        delimiter_l = len(delimiter)
        loc = str(item_str).find(delimiter)
        if loc != -1:
            item_name = item_str[:loc]
            item_data = item_str[loc+delimiter_l:]
        else:
            item_name = item_str

        return (item_name, item_data)

    @staticmethod
    def set_empty_node(item, parameter):
        item.data = "none"

    @staticmethod
    def default_empty_node(item, parameter):
        if item.data == None:
            item.data = "none"

    def export_format_tree_to_file(self, file_path):
        TreeByBinTree.export_format_tree_to_file(self, file_path, "  ", self.export_node_function)

    def import_format_tree_from_file(self, file_path):
        TreeByBinTree.import_format_tree_from_file(self, file_path, "  ", self.import_node_function)

    def is_new_tree(self, item):
        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_child_item = self.get_child_item(item)

        while(h_child_item != None):
            if (self.get_child_item(h_child_item) == None):
                if h_child_item.data != "none":
                    return False

            result = self.is_new_tree(h_child_item)
            if result == False:
                return False
            h_child_item = self.get_next_sibling_item(h_child_item)

        return True

    def build_tree(self, search_path, cur_level, level_max = -1):
        if cur_level > level_max:
            return

        svn_path = search_path.replace("|", "/")
        cmd_output = Util.execute_and_output("svn ls " + svn_path)
        if cmd_output == "":
            return
        item_nodes = str(cmd_output).split("\n")

        is_dir = True
        for item_node in item_nodes:
            if item_node[-1] == "/":
                item_node = item_node[:-1]
                is_dir = True
            else:
                is_dir = False

            node_path = search_path + '|' + item_node
            self.add_item(node_path, '|', True, False, False)

            if is_dir == True:
                cur_level = cur_level + 1
                SvnTree.build_tree(self, node_path, cur_level, level_max)
                cur_level = cur_level - 1
