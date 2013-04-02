#!/usr/bin/env python -v

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

import imp
import command
import os 

DOT_BUILDC_RC = '.buildc.rc'
BUILDC_CFG = 'buildc.cfg'

def usr_home():
    return os.path.expanduser('~')

def dot_buildc_rc_path():
    return usr_home() + '/' + DOT_BUILDC_RC;

def load_config(filename):
    f = file(filename, 'rU')
    try:
        m = imp.load_source('', filename, f)
    except SyntaxError, error:
        print error
    f.close()
    command.execute('rm -f ' + filename + 'c')

    return m

if __name__ == '__main__':
    print usr_home()
    print dot_buildc_rc_path()
    exit
