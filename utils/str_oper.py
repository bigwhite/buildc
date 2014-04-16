#!/usr/bin/env python
import re

class StrOper(object):
    @staticmethod
    def show_hex_from_str(str, len):
        i = 1
        while (i < len + 1):
            if isinstance(str[i-1], int):
                print "%02x" % str[i-1],
            else:
                print "%02x" % ord(str[i-1]),
            if ( (i % 16) == 0):
                print ""
            i = i + 1

    @staticmethod
    def parse_host_str(host_str):
        host_string = host_str[str(host_str).rfind('@')+1 : ]
        username    = host_str[0 : str(host_str).find('/')]
        password    = host_str[str(host_str).find('/')+1 : str(host_str).find('@')]
        return (host_string, username, password)

    @staticmethod
    def get_spaces_str(string, num):
        string = ""
        for i in xrange(num):
            string += " "
        return string

    @staticmethod
    def get_indent_str(string, indent, num):
        string = ""
        for i in xrange(num):
            string += indent
        return string

    @staticmethod
    def get_env_var_values(var_name, user_env_str):
        var_values = list()
        user_env_str = '\n' + user_env_str + '\n'

        value_list = list()
        num = StrOper.take_tag_text(user_env_str, '\n' + var_name + "=", '\n', var_values, -1)
        if num == 0:
            info_str = "Warning: " + var_name + " does not exist."
            print info_str
            return None
        else:
            value_list = re.split("[:;]", str(var_values[0]))
            return value_list

    @staticmethod
    def env_var_to_value(file_path, user_env_str):
        path_str = file_path
        var_name_list = list()
        num = StrOper.take_tag_text(path_str + '/', '$', '/', var_name_list, -1)

        var_name = None
        var_values = list()
        for index in xrange(num):
            var_name = var_name_list[index]
            var_values = StrOper.get_env_var_values(var_name, user_env_str)
            if var_values != None:
                path_str = str(path_str).replace('$' + var_name, var_values[0], 1)
            else:
                return None

        return path_str

    @staticmethod
    def take_cell_text(text_str, delimiter, text_list, max_num = -1, append_delimiter = False):
        balance = 0

        context = ""
        element = ""
        delimiter_l = len(delimiter)
        i = 0
        index = 0
        text_l = len(text_str)
        while (index < text_l):
            element = text_str[index]
            index += 1
            if (element[0] == delimiter[i]):
                may_be_del = ""
                may_be_del += element
                i = 1
                while (i < delimiter_l):
                    element = text_str[index]
                    index += 1
                    if (element[0] == delimiter[i]):
                        may_be_del += element
                    else:
                        may_be_del += element
                        context += may_be_del
                        break
                    i += 1

                if (i == delimiter_l):
                    if (append_delimiter == True):
                        context += may_be_del
                    text_list.append(context)

                    balance += 1
                    if (balance == max_num):
                        return balance
                    context = ""

                i = 0
            else:
                context += element

        if (context != ""):
            text_list.append(context)

            balance += 1
            if (balance == max_num):
                return balance
            return balance
        else:
            return balance

    @staticmethod
    def take_cell_text_by_list(text_str, delimiter_list, text_list, max_num = -1, append_delimiter = False):
        balance = 0
        if (delimiter_list == None):
            text_list.append(text_str)
            balance += 1
            return balance

        context = ""
        element = ""
        delimiter = ""
        delimiter_l = 0

        i = 0
        index = 0
        text_l = len(text_str)
        delimiter_loc = -1
        delimiter_list_i = 0
        delimiter_list_l = len(delimiter_list)
        while (index < text_l):
            element = text_str[index]
            index += 1
            delimiter_list_i = 0
            for delimiter_list_i in range(delimiter_list_l):
                delimiter_l = len(delimiter_list[delimiter_list_i])
                if (delimiter_l != 0):
                    delimiter = delimiter_list[delimiter_list_i]
                else:
                    continue

                if (element[0] == delimiter[i]):
                    delimiter_loc = 1
                    may_be_del = ""
                    may_be_del += element
                    i = 1
                    while (i < delimiter_l):
                        element = text_str[index]
                        index += 1
                        delimiter_loc += 1
                        if (element[0] == delimiter[i]):
                            may_be_del += element
                        else:
                            index -= delimiter_loc
                            delimiter_loc = -1
                            break
                        i += 1

                    if (i == delimiter_l):
                        if (append_delimiter == True):
                            context += may_be_del;
                        text_list.append(context)
                        balance += 1
                        if (balance == max_num):
                            return balance
                        context = ""
                        i = -1
                    else:
                        i = 0
                        element = text_str[index]
                        index += 1

                if (i == -1):
                    break

            if (i == -1):
                i = 0
                continue
            context += element

        if (context != ""):
            text_list.append(context)
            balance += 1
            if (balance == max_num):
                return balance
            return balance
        else:
            return balance

    @staticmethod
    def take_tag_text(text_str, before_tag, after_tag, text_list, max_num = -1):
        balance = 0
        text_l = len(text_str)

        context = ""
        btag_l = len(before_tag)
        bi = 0
        atag_l = len(after_tag)
        ai = 0
        deal_str = ""

        j = 0
        k = -1
        while(True):
            if (j == k):
                break
            else:
                k = j
            while(j < text_l):
                deal_str = text_str[j]
                j = j + 1
                if (before_tag[bi] == deal_str[0]):
                    bi = bi + 1
                    if (bi == btag_l):
                        bi = 0
                        break
                else:
                    bi = 0

            while(j < text_l):

                deal_str = text_str[j]
                j = j + 1
                if (after_tag[ai] == deal_str[0]):
                    if (atag_l == 1):
                        ai = -1
                        break
                    ai = ai + 1
                    while(j < text_l):
                        deal_str = text_str[j]
                        j = j + 1
                        if (after_tag[ai] == deal_str[0]):
                            ai = ai + 1
                            if (ai == atag_l):
                                ai = -1
                                break
                        else:
                            j -= ai
                            context += after_tag[0];
                            ai = 0;
                            break;

                    if (ai == -1):
                        break
                else:
                    context += deal_str[0];

            if (ai == -1):
                text_list.append(context)

                balance = balance + 1;
                if (balance == max_num):
                    break

                context = ""
                ai = 0

        return balance

    @staticmethod
    def take_inner_tag_text(text_str, before_tag, after_tag, text_list, \
        max_num = -1, offset_tag = None, append_tag = False):
        balance=0
        text_l = len(text_str)

        context = ""
        element = ""
        offset_tag_l = 0
        if (offset_tag != None and offset_tag != ""):
            offset_tag_l = len(offset_tag)
        btag_l = len(before_tag)
        atag_l = len(after_tag)

        i = 0
        index = 0

        delimiter_loc = -1
        while (offset_tag_l != 0 and index < text_l):
            element = text_str[index]
            index += 1
            if (element[0] == offset_tag[index]):
                delimiter_loc = 1
                may_be_del = ""
                may_be_del += element
                i = 1
                for i in range(1, offset_tag_l):
                    element[0] = text_str[index]
                    index += 1
                    delimiter_loc += 1
                    if (element[0] == offset_tag[i]):
                        may_be_del += element
                    else:
                        index -= delimiter_loc
                        delimiter_loc = -1
                        break

                if (i == offset_tag_l):
                    if (append_tag == True):
                        context += may_be_del
                    i = 0
                    break

                i = 0
                if (index == text_l):
                    print "exception: index == text_l"
                    assert(False)
                    break
                element = text_str[index]
                index += 1

        while (index < text_l):
            level = -1
            while (index < text_l):
                element = text_str[index]
                index += 1
                if (before_tag[i] == element[0]):
                    delimiter_loc = 1
                    may_be_del = ""
                    may_be_del += element
                    i = 1
                    while (i < btag_l):
                        element = text_str[index]
                        index += 1
                        delimiter_loc += 1
                        if (before_tag[i] == element[0]):
                            may_be_del += element
                        else:
                            index -= delimiter_loc
                            delimiter_loc = -1
                            break
                        i += 1

                    if (i == btag_l):
                        level = 1
                        if (append_tag == True):
                            context = may_be_del
                        else:
                            context = ""
                        i = 0
                        continue

                    i = 0
                    if (index == text_l):
                        print "exception: index == text_l"
                        assert(False)
                        break
                    element = text_str[index]
                    index += 1

                if (after_tag[i] == element[0]):
                    delimiter_loc = 1
                    may_be_del = ""
                    may_be_del += element
                    i = 1
                    while (i < atag_l):
                        element = text_str[index]
                        index += 1
                        delimiter_loc += 1
                        if (after_tag[i] == element[0]):
                            may_be_del += element
                        else:
                            index -= delimiter_loc
                            delimiter_loc = -1
                            break
                        i += 1

                    if (i == atag_l):
                        if (level == 1):
                            if (append_tag == True):
                                context += may_be_del
                            text_list.append(context)
                            balance += 1
                            i = 0
                            break
                        else:
                            print "exist tag2, level=" + str(level)
                            i = 0
                            continue

                    i = 0
                    if (index == text_l):
                        print "exception: index == text_l"
                        assert(False)
                        break
                    element = text_str[index]
                    index += 1

                if (level == 1):
                    context += element
            if (balance == max_num):
                return balance
            context = ""

        return balance

if __name__ == '__main__':
    inner_text_str = "<div><div>Intel E8</div><div>"
    text_list = list()
    StrOper.take_inner_tag_text(inner_text_str, "<div>", "</div>", text_list, -1, None, False)
    for item in text_list:
        print "value=" + item

    StrOper.show_hex_from_str("hello_world", len("hello_world"))

    user_env_str = \
"""MPIAG_HOME=mpiag_temp/ffff/aaaa
JAVA_HOME=java1_temp/ffff/aaaa:jara2_temp/ffff/aaaa
JRE_HOME=jre_temp/ffff/aaaa
"""
    var_values = list()
    var_values = StrOper.get_env_var_values("JAVA_HOME", user_env_str)
    for value in var_values:
        print "value=" + value

    file_path = StrOper.env_var_to_value("$JAVA_HOME/end_temp/6666", user_env_str)
    print "file_path=" + file_path

    text_list = list()
    text_str = "1.2.3.4.5"
    print "test: take_cell_text()"
    StrOper.take_cell_text(text_str, ".", text_list, -1, False)
    for i in range(len(text_list)):
        print str(i) + "-->" + text_list[i]

    text_list = list()
    text_str = "1___2___3___4___5"
    StrOper.take_cell_text(text_str, "___", text_list, -1, False)
    for i in range(len(text_list)):
        print str(i) + "-->" + text_list[i]

    text_list = list()
    text_str = "1.2_3.4_5"
    print "test: take_cell_text_by_list()"
    StrOper.take_cell_text_by_list(text_str, (".", "_"), text_list, -1, False)
    for i in range(len(text_list)):
        print str(i) + "-->" + text_list[i]

    text_list = list()
    text_str = "1___2___3___4___5"
    StrOper.take_cell_text_by_list(text_str, ("___", ), text_list, -1, False)
    for i in range(len(text_list)):
        print str(i) + "-->" + text_list[i]

    text_list = list()
    text_str = "<b>aaa</b><b>bbb</b>"
    print "test: take_tag_text()"
    StrOper.take_tag_text(text_str, "<b>", "</b>", text_list, -1)
    for i in range(len(text_list)):
        print str(i) + "-->" + text_list[i]
