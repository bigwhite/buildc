#!/usr/bin/env python

# Copyright (c) 2011 - 2012 Tony Bai <bigwhite.cn@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

errors = {
    'args_invalid' : 10,
    'os_not_supported' : 11,
    'cpu_not_supported' : 12,
    'lib_not_found' : 13,
    'shell_cmd_exec_failed' : 14,
    'bin_file_not_found' : 15,
    'conf_file_not_found' : 16,
    'tpl_file_not_found' : 17,
    'file_or_dir_exists' : 18
}

if __name__ == '__main__':
    print errors
