#! /usr/bin/env python

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

import commands

def os():
    s = commands.getoutput('uname -s')    
    if (s == 'Linux'):
        return 'linux'
    if (s == 'SunOS'):
        return 'solaris'
    else:
        return 'unknown'

def cpu():
    s = commands.getoutput('uname -p')    
    if (s == 'sparc'):
        return 'sparc'
    if (s == 'i386'):
        return 'x86'
    if (s == 'x86_64'):
        return 'x86'
    else:
        return 'unknown'
    
if __name__ == '__main__':
    print os()
    print cpu()
