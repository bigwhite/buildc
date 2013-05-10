#!/usr/bin/env python

class Errors(object):
    args_invalid          = 10
    vm_list_invalid       = 11
    shell_cmd_exec_failed = 14
    conf_file_not_found   = 16
    conf_item_not_found   = 17
    tpl_file_not_found    = 18
    lib_not_found         = 19
    file_or_dir_exists    = 20
    logical_errors        = 21
    environment_errors    = 22
    shell_type_unknown    = 23
    tuple_number_invalid  = 24

if __name__ == '__main__':
    print ""
