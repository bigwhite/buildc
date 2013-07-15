#!/usr/bin/env python

import os
import sys
from utils.errnos import Errors
from utils.str_oper import StrOper
from utils.file_oper import FileOper
from utils.datastruct.bintree import BinTree

class TreeByBinTree(BinTree):
    BT_ROOT  = 0x10000
    BT_FIRST = 0x0FFFF
    BT_LAST  = 0x0FFFE

    def __init__(self):
        self.layer_count = 0
        self.layer_num   = 0
        return super(TreeByBinTree, self).__init__()

    @staticmethod
    def get_child_item(item):
        return item.lchild

    @staticmethod
    def get_next_sibling_item(item):
        return item.rchild

    @staticmethod
    def get_layer_count(item):
        count = 0
        while(item):
            count = count + 1
            item = TreeByBinTree.get_parent_item(item)

        return count

    def insert_item(self, item_name, parent, insert_after):
        if (self.get_root_item() == None):
            self.root = self.new_child(None, item_name)
            return self.root

        newitem = None
        if (parent == None):
            root = self.get_root_item()
            newitem = self.new_child(None, item_name)
            if (insert_after == TreeByBinTree.BT_FIRST):
                newitem.rchild = root
                root           = newitem
                return newitem
            elif (insert_after == TreeByBinTree.BT_LAST):
                while (root.rchild):
                    root = root.rchild
                root.rchild = newitem
                return newitem
            else:
                while (root.rchild and root != insert_after):
                    root = root.rchild

                if (root != insert_after):
                    print "Not find the root corresponding sibling node."
                    assert(False)
                    return None
                else:
                    newitem.rchild = root.rchild
                    root.rchild = newitem
                    return newitem

        if (insert_after == TreeByBinTree.BT_FIRST):
            newitem = self.new_child(parent, item_name)
            if (parent.lchild):
                newitem.rchild = parent.lchild
                parent.lchild  = newitem
            else:
                parent.lchild = newitem

            return newitem
        elif (insert_after == TreeByBinTree.BT_LAST):
            newitem = self.new_child(parent, item_name)
            if (parent.lchild):
                tailitem = parent.lchild;
                while (tailitem.rchild):
                    tailitem = tailitem.rchild
                tailitem.rchild = newitem
            else:
                parent.lchild = newitem

            return newitem;
        else:
            newitem = self.new_child(parent, item_name)
            if (parent.lchild):
                p_item = parent.lchild
                while(p_item.rchild and p_item != insert_after):
                    p_item = p_item.rchild

                if (p_item != insert_after):
                    print "Not find the corresponding sibling in the parent node."
                    assert(False)
                    return None
                else:
                    newitem.rchild = p_item.rchild
                    p_item.rchild = newitem
                    return newitem
            else:
                print "Not find the corresponding sibling in the parent node."
                assert(False)
                return None

    def search_sibling_node(self, item, sibling_name):
        if (self.root == None):
            return None

        p_item = None
        while(item.parent != None):
            p_item = item
            item = item.parent
            if (item.rchild == p_item):
                continue
            else:
                break

        while(p_item):
            if (p_item.name == sibling_name):
                return p_item

            p_item = p_item.rchild

    def add_item(self, full_path, delimiter = "\\", add_path_item = True, can_repeat = False, prompt = True):
        if full_path.endswith(delimiter):
            full_path = full_path[:-len(delimiter)]
        if (len(full_path) == 0):
            return None
        full_path_list = str(full_path).split(delimiter)

        location = 1
        h_item     = self.get_root_item()
        h_pre_item = h_item
        h_child_item = None
        item_str     = full_path_list[location-1]

        if (h_item == None):
            if (add_path_item == True or len(full_path_list) == 1):
                item_str = full_path_list[location-1]
                h_child_item = self.insert_item(item_str, h_pre_item, TreeByBinTree.BT_FIRST)
                assert(h_child_item != None)
                if (location == len(full_path_list)):
                    return h_child_item
                h_pre_item = h_item = h_child_item
            else:
                print "The middle path does not exist, can not be established leaf nodes: " + full_path_list[len(full_path_list)-1]
                return None

        while(True):
            if (self.get_item_text(h_item) == item_str):
                while(True):
                    h_pre_item = h_item
                    h_item = self.get_next_sibling_item(h_item)
                    if (h_item and self.get_item_text(h_item) == item_str):
                        pass
                    else:
                        h_item = h_pre_item
                        break

                if (location == len(full_path_list)):
                    if (can_repeat == True):
                        h_child_item = self.insert_item(item_str, self.get_parent_item(h_item), TreeByBinTree.BT_LAST)
                        assert(h_child_item != None)
                        return h_child_item
                    else:
                        if (prompt == True):
                            print "Node data items: " + full_path + " already exists, you do not need to add."
                        return h_item
                else:
                    h_child_item = self.get_child_item(h_item)
                    if (h_child_item):
                        location = location + 1
                        item_str = full_path_list[location-1]
                        h_pre_item = h_item = h_child_item
                    else:
                        if (add_path_item == True or location+1 == len(full_path_list)):
                            location = location + 1
                            item_str = full_path_list[location-1]
                            h_child_item = self.insert_item(item_str, h_item, TreeByBinTree.BT_FIRST);
                            assert(h_child_item != None)
                            if (location == len(full_path_list)):
                                return h_child_item
                            h_pre_item = h_item = h_child_item
                        else:
                            print "The middle path does not exist, can not be established leaf nodes: " + full_path_list[len(full_path_list)-1]
                            return None
            else:
                h_pre_item = h_item
                h_item = self.get_next_sibling_item(h_item)
                if (h_item == None):
                    if (add_path_item == True or location == len(full_path_list)):
                        item_str = full_path_list[location-1]
                        h_child_item = self.insert_item(item_str, self.get_parent_item(h_pre_item), h_pre_item)
                        assert(h_child_item != None)
                        if (location == len(full_path_list)):
                            return h_child_item
                        h_item = h_child_item
                    else:
                        print "The middle path does not exist, can not be established leaf nodes: " + full_path_list[len(full_path_list)-1]
                        return None
                else:
                    pass

        return

    def delete_leaf_node(self, item, prompt = True):
        if (self.get_child_item(item) == None):
            h_parent_item = self.get_parent_item(item)
            h_pre_item = None
            if h_parent_item == None:
                if (self.root == item):
                    self.root = item.rchild
                else:
                    h_pre_item = self.root
                    while (h_pre_item.rchild != item):
                        h_pre_item = h_pre_item.rchild
                    h_pre_item.rchild = item.rchild
                return True
            else:
                if (h_parent_item.lchild == item):
                    h_parent_item.lchild = item.rchild
                else:
                    h_pre_item = h_parent_item.lchild
                    while (h_pre_item.rchild != item):
                        h_pre_item = h_pre_item.rchild
                    h_pre_item.rchild = item.rchild
                return True
        else:
            if (prompt == True):
                print "Can not delete non-leaf node."
            return False

    def delete_leaf_item(self, full_path, delimiter = "\\", prompt = True):
        found_item_list = list()
        self.find_full_strict_item(None, found_item_list, full_path, delimiter, 1)
        if len(found_item_list) == 0:
            if (prompt == True):
                print "full_path corresponding node does not exist."
            return True

        return self.delete_leaf_node(found_item_list[0], prompt)

    def find_item(self, full_path, delimiter = "\\", prompt = True, operation = 1):
        assert(operation==1 or operation==2 or operation==3)

        full_path_list = str(full_path).split(delimiter)
        if (len(full_path_list) == 0):
            return self.get_root_item()

        location = 1
        h_item = self.get_root_item()
        item_str = full_path_list[location-1]

        while(True):
            while(h_item != None):
                if (operation == 1 and self.get_item_text(h_item) == item_str):
                    break
                elif (operation == 2 and str(self.get_item_text(h_item)).startswith(item_str) == True):
                    break
                elif (operation == 3 and str(self.get_item_text(h_item)).endswith(item_str) == True):
                    break

                h_item = self.get_next_sibling_item(h_item)

            if (h_item == None):
                if (location == len(full_path_list)):
                    if (prompt):
                        print "The data item: " + full_path + "\nnot found."
                    return None
                else:
                    pass_str = ""
                    i = location
                    for i in xrange(location):
                        pass_str = pass_str + full_path_list[i] + delimiter
                    if (prompt):
                        print "The data item: " + pass_str + "\nnot found."
                    return None
            else:
                if (location == len(full_path_list)):
                    return h_item
                else:
                    h_item = self.get_child_item(h_item)
                    location = location + 1
                    item_str = full_path_list[location-1]

    def find_full_item(self, item, found_item_list, full_path, delimiter = "\\", operation = 1):
        assert(operation==1 or operation==2 or operation==3)

        if full_path.endswith(delimiter):
            full_path = full_path[:-len(delimiter)]
        if (len(full_path) == 0):
            found_item_list.append(item)
            return

        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_child_item = self.get_child_item(item)

        is_found = False
        item_str = None
        child_path = None
        while(h_child_item != None):
            if full_path.find(delimiter) == -1:
                item_str = full_path
            else:
                item_str = full_path[:full_path.find(delimiter)]

            if (operation == 1 and self.get_item_text(h_child_item) == item_str):
                is_found = True
            elif (operation == 2 and str(self.get_item_text(h_child_item)).startswith(item_str) == True):
                is_found = True
            elif (operation == 3 and str(self.get_item_text(h_child_item)).endswith(item_str) == True):
                is_found = True
            else:
                is_found = False

            if is_found == True:
                if full_path.find(delimiter) == -1:
                    child_path = ""
                else:
                    child_path = full_path[full_path.find(delimiter)+1:]
                self.find_full_item(h_child_item, found_item_list, child_path, delimiter, operation)
            h_child_item = self.get_next_sibling_item(h_child_item)

    def find_full_strict_item(self, item, found_item_list, full_path, delimiter = "\\", operation = 1):
        assert(operation==1 or operation==2 or operation==3)

        if full_path.endswith(delimiter):
            full_path = full_path[:-len(delimiter)]
        if (len(full_path) == 0):
            found_item_list.append(item)
            return

        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_child_item = self.get_child_item(item)

        is_found = False
        item_str = None
        loc_num  = None
        cur_num  = 0
        child_path = None
        while(h_child_item != None):
            if full_path.find(delimiter) == -1:
                item_str = full_path
            else:
                item_str = full_path[:full_path.find(delimiter)]

            if item_str.find('.') != -1:
                loc_num = int(item_str[item_str.find('.')+1:])
                item_str = item_str[:item_str.find('.')]

            if (operation == 1 and self.get_item_text(h_child_item) == item_str):
                is_found = True
            elif (operation == 2 and str(self.get_item_text(h_child_item)).startswith(item_str) == True):
                is_found = True
            elif (operation == 3 and str(self.get_item_text(h_child_item)).endswith(item_str) == True):
                is_found = True
            else:
                is_found = False

            if is_found == True:
                cur_num = cur_num + 1

            if is_found == True:
                if loc_num == None or loc_num <= cur_num:
                    if full_path.find(delimiter) == -1:
                        child_path = ""
                    else:
                        child_path = full_path[full_path.find(delimiter)+1:]
                    self.find_full_strict_item(h_child_item, found_item_list, child_path, delimiter, operation)
            if loc_num == None or loc_num > cur_num:
                h_child_item = self.get_next_sibling_item(h_child_item)
            else:
                break

    def get_full_path(self, h_item, delimiter="\\"):
        full_path = ""
        count = 0
        if (h_item):
            full_path = self.get_item_text(h_item)
            count += 1
        else:
            full_path = ""
            return (full_path, count)

        h_item = self.get_parent_item(h_item)
        while(h_item != None):
            full_path = self.get_item_text(h_item) + delimiter + full_path
            count += 1
            h_item = self.get_parent_item(h_item)

        return (full_path, count)

    str_msg = ""
    export_node_handler = None
    def recursive_write_items_to_text(self, item, level, indent = "  "):
        if (item == None):
            item = self.get_root_item()

        while (item != None):
            tree_str = None
            temp_str = None

            tree_str = StrOper.get_indent_str(temp_str, indent, level) + item.name

            if self.export_node_handler == None:
                TreeByBinTree.str_msg += tree_str
            else:
                self.export_node_handler(tree_str, item.data)
            TreeByBinTree.str_msg += '\n'

            item_child = self.get_child_item(item)
            if (item_child != None):
                level += 1
                self.recursive_write_items_to_text(item_child, level, indent)
                level -= 1

            item = self.get_next_sibling_item(item)

    def export_format_tree_to_file(self, file_path, indent = "  ", export_node_function = None):
        level = 0
        TreeByBinTree.str_msg = ""

        self.export_node_handler = export_node_function
        self.recursive_write_items_to_text(None, level, indent)
        self.export_node_handler = None
        content_str = TreeByBinTree.str_msg
        TreeByBinTree.str_msg = ""

        FileOper.write_data(file_path, content_str)
        return

    def show_format_tree(self, indent = "  ", export_node_function = None):
        level = 0
        TreeByBinTree.str_msg = ""

        self.export_node_handler = export_node_function
        self.recursive_write_items_to_text(None, level, indent)
        self.export_node_handler = None
        content_str = TreeByBinTree.str_msg
        TreeByBinTree.str_msg = ""

        print "tree structure:"
        print content_str
        return

    def import_format_tree_from_file(self, file_path, indent = "  ", import_node_handler = None):
        if not os.path.exists(file_path):
            return

        items = list()
        index = 0
        items.append((None))
        h_after = self.BT_FIRST

        line_str = None
        pre_indent_count = 0
        cur_indent_count = 0

        indent_l = len(indent)

        f = open(file_path, 'r')
        for line_str in f.readlines():
            if line_str[-1] == '\n':
                line_str = line_str[:-1]

            cur_indent_count = 0
            i = 0
            while(True):
                if (str(line_str)[i:i+indent_l] == indent):
                    cur_indent_count += 1
                else:
                    break

                i += indent_l

            item_name = None
            item_data = None
            item_str = str(line_str)[i:]
            if import_node_handler != None:
                (item_name, item_data) = import_node_handler(item_str)
            else:
                item_name = item_str

            if (pre_indent_count == cur_indent_count):
                h_after = self.insert_item(item_name, items[index], h_after)
            elif (pre_indent_count < cur_indent_count):
                items.append((h_after))
                index += 1
                h_after = self.BT_FIRST
                h_after = self.insert_item(item_name, items[index], h_after)
            else:
                for i in range(pre_indent_count - cur_indent_count):
                    items.pop()
                index -= (pre_indent_count - cur_indent_count)
                h_after = self.BT_LAST
                h_after = self.insert_item(item_name, items[index], h_after)
            h_after.data = item_data

            pre_indent_count = cur_indent_count

        f.close()

    def take_item_data_by_browse(self, item, deal_process, deal_way = 3):
        h_child_item = None
        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_child_item = self.get_child_item(item)

        while(h_child_item != None):
            if (deal_way == 1):
                if (self.get_child_item(h_child_item) == None):
                    deal_process(h_child_item, self.parameter_point)
            elif (deal_way == 2):
                if (self.get_child_item(h_child_item) != None):
                    deal_process(h_child_item, self.parameter_point)
            elif (deal_way == 3):
                deal_process(h_child_item, self.parameter_point)
            else:
                print "Error: Processing method parameters deal_way error, deal_way=" + deal_way
                sys.exit(Errors.args_invalid)

            self.take_item_data_by_browse(h_child_item, deal_process, deal_way)
            h_child_item = self.get_next_sibling_item(h_child_item)

    def take_item_data_by_browse_only_deal_sibling(self, item, deal_process, deal_way = 3):
        h_child_item = None
        if (item == None):
            h_child_item = self.get_root_item()
        else:
            h_parent_item = self.get_parent_item(item)
            if (h_parent_item == None):
                h_child_item = self.get_root_item()
            else:
                h_child_item = self.get_child_item(h_parent_item)

        while(h_child_item != None):
            if (deal_way == 1):
                if (self.get_child_item(h_child_item) == None):
                    deal_process(h_child_item, self.parameter_point)
            elif (deal_way == 2):
                if (self.get_child_item(h_child_item) != None):
                    deal_process(h_child_item, self.parameter_point)
            elif (deal_way == 3):
                deal_process(h_child_item, self.parameter_point)
            else:
                print "Error: Processing method parameters deal_way error, deal_way=" + deal_way
                sys.exit(Errors.args_invalid)

            h_child_item = self.get_next_sibling_item(h_child_item)

    @staticmethod
    def set_browse_layer_num(self, num):
        self.layer_num = num
    @staticmethod
    def get_browse_layer_num(self):
        return self.layer_num

    def take_item_data_by_browse_limit_layer_num(self, item, deal_process, deal_way = 3):
        self.layer_count = 0
        self.__in_take_item_data_by_browse_limit_layer_num(item, deal_process, deal_way)

    def __in_take_item_data_by_browse_limit_layer_num(self, item, deal_process, deal_way = 3):
        h_child_item = None
        if (item == None):
            h_child_item = self.get_root_item()
            self.layer_count += 1
        else:
            h_child_item = self.get_child_item(item)
            self.layer_count += 1

        if (self.layer_count > self.layer_num):
            self.layer_count -= 1
            return

        while(h_child_item != None):
            if (deal_way == 1):
                if (self.get_child_item(h_child_item) == None):
                    deal_process(h_child_item, self.parameter_point)
            elif (deal_way == 2):
                if (self.get_child_item(h_child_item) != None):
                    deal_process(h_child_item, self.parameter_point)
            elif (deal_way == 3):
                deal_process(h_child_item, self.parameter_point)
            else:
                print "Error: Processing method parameters deal_way error, deal_way=" + deal_way
                sys.exit(Errors.args_invalid)

            self.take_item_data_by_browse(h_child_item, deal_process, deal_way)
            h_child_item = self.get_next_sibling_item(h_child_item)

        self.layer_count -= 1

    def browse_control(self, h_cur_item, deal_process, browse_way = 1, deal_node_way = 3, layer_num = 0):
        if (self.layer_num <= 0):
            if (browse_way == 1):
                self.take_item_data_by_browse(None, deal_process, deal_node_way)
            elif (browse_way == 2):
                self.take_item_data_by_browse(h_cur_item, deal_process, deal_node_way)
            elif (browse_way == 3):
                self.take_item_data_by_browse_only_deal_sibling(h_cur_item, deal_process, deal_node_way)
            else:
                print "Error: Processing method parameters browse_way error, browse_way = %d" % browse_way
                sys.exit(Errors.args_invalid)
        else:
            self.set_browse_layer_num(layer_num)
            if (browse_way == 1):
                self.take_item_data_by_browse_limit_layer_num(None, deal_process, deal_node_way)
            elif(browse_way == 2):
                self.take_item_data_by_browse_limit_layer_num(h_cur_item, deal_process, deal_node_way)
            elif(browse_way == 3):
                self.take_item_data_by_browse_only_deal_sibling(h_cur_item, deal_process, deal_node_way)
            else:
                print "Error: Processing method parameters browse_way error, browse_way = %d" % browse_way
                sys.exit(Errors.args_invalid)

    __in_take_items_address_list = None
    @staticmethod
    def __in_take_items(h_item, parameter):
        TreeByBinTree.__in_take_items_address_list.append(h_item)

    def take_items(self, h_item, items_address_list, browse_way = 2, deal_node_way = 3, layer_num = 0):
        TreeByBinTree.__in_take_items_address_list = list()

        self.browse_control(h_item, TreeByBinTree.__in_take_items, browse_way, deal_node_way, layer_num)
        for item in TreeByBinTree.__in_take_items_address_list:
            items_address_list.append(item)

        length = len(TreeByBinTree.__in_take_items_address_list)
        TreeByBinTree.__in_take_items_address_list = None
        return length

    __in_take_item_titles_list = None
    @staticmethod
    def __in_take_item_titles(h_item, parameter):
        _this = parameter
        TreeByBinTree.__in_take_item_titles_list.append(_this.get_item_text(h_item))

    def take_item_titles(self, h_item, item_titles_list, browse_way = 2, deal_node_way = 3, layer_num = 0):
        TreeByBinTree.__in_take_item_titles_list = list()

        self.parameter_point = self
        self.browse_control(h_item, TreeByBinTree.__in_take_item_titles, browse_way, deal_node_way, layer_num)
        self.parameter_point = None
        for item in TreeByBinTree.__in_take_item_titles_list:
            item_titles_list.append(item)

        length = len(TreeByBinTree.__in_take_item_titles_list)
        TreeByBinTree.__in_take_item_titles_list = None
        return length

    __in_take_item_paths_list = None
    @staticmethod
    def __in_take_item_paths(h_item, parameter):
        _this = parameter
        TreeByBinTree.__in_take_item_paths_list.append(_this.get_full_path(h_item)[0])

    def take_item_paths(self, h_item, item_paths_list, browse_way = 2, deal_node_way = 3, layer_num = 0):
        TreeByBinTree.__in_take_item_paths_list = list()

        self.parameter_point = self
        self.browse_control(h_item, TreeByBinTree.__in_take_item_paths, browse_way, deal_node_way, layer_num)
        self.parameter_point = None
        for item in TreeByBinTree.__in_take_item_paths_list:
            item_paths_list.append(item)

        length = len(TreeByBinTree.__in_take_item_paths_list)
        TreeByBinTree.__in_take_item_paths_list = None
        return length

if __name__ == '__main__':
    pass
