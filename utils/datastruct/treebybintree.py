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

    def add_item(self, full_path, delimiter="\\", add_path_item = True, can_repeat = False, prompt = True):
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

if __name__ == '__main__':
    def export_node_function(tree_str, node_data):
        if node_data == None:
            TreeByBinTree.str_msg += tree_str
        else:
            TreeByBinTree.str_msg += tree_str + "    " + node_data

    def deal_leaf_node(item, parameter):
        item.data = "leaf_node"

    tree = TreeByBinTree()
    tree.add_item("aaa1\\bbb1\\ccc1")
    tree.add_item("aaa1\\bbb1\\ccc2")
    tree.add_item("aaa1\\bbb1\\ccc3")
    tree.add_item("aaa1\\bbb2\\ccc1")
    tree.add_item("aaa1\\bbb2\\ccc2")
    tree.add_item("aaa1\\bbb2\\ccc3")
    tree.add_item("aaa2\\bbb1\\ccc1")
    tree.add_item("aaa2\\bbb1\\ccc2")
    tree.add_item("aaa2\\bbb1\\ccc3")
    tree.add_item("aaa2\\bbb2\\ccc1")
    tree.add_item("aaa2\\bbb2\\ccc2")
    tree.add_item("aaa2\\bbb2\\ccc3")
    tree.export_format_tree_to_file("X:\\ttt1.txt")

    import_tree = TreeByBinTree()
    import_tree.import_format_tree_from_file("X:\\ttt1.txt")
    import_tree.export_format_tree_to_file("X:\\import_tree.txt")

    tree.take_item_data_by_browse(None, deal_leaf_node, 1)
    tree.export_format_tree_to_file("X:\\ttt2.txt", "  ", export_node_function)

    print "output X:\\ttt.txt"
