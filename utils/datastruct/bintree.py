#!/usr/bin/env python

class BinNode:
    def __init__(self):
        self.data = None
        self.name = ""
        self.parent = None
        self.lchild, self.rchild = None, None

class BinTree(object):
    def __init__(self):
        self.root = None
        self.parameter_point = None

    def get_root_item(self):
        return self.root

    @staticmethod
    def get_parent_item(item):
        return item.parent

    @staticmethod
    def get_item_text(item):
        return item.name

    def is_created(self):
        return self.get_root_item() != None

    @staticmethod
    def new_child(parent, child_name):
        newitem = BinNode()
        newitem.name   = child_name
        newitem.parent = parent
        return newitem

    @staticmethod
    def new_left_child(item, left_child_name):
        if (item.lchild == None):
            item.lchild = BinNode()
            item.lchild.parent = item
            item.lchild.name   = left_child_name
            return item.lchild
        else:
            print "left child already exists."
            return item.lchild

    @staticmethod
    def new_right_child(item, right_child_name):
        if (item.rchild == None):
            item.rchild = BinNode()
            item.rchild.parent = item
            item.rchild.name   = right_child_name
            return item.rchild
        else:
            print "right child already exists."
            return BinNode(item).rchild

    @staticmethod
    def Creat():
        root = None
        print "Please enter the data of the node to create a binary tree."
        import msvcrt
        ch = msvcrt.getch()
        if (ch == "!"):
            root = None
        else:
            root = BinNode()
            root.data = ch
            root.lchild = BinTree.Creat( )
            root.rchild = BinTree.Creat( )

        return root
