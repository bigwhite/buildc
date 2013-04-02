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
import sys
import errnos

def execute(cmd, ignore_error=None):
    o = commands.getstatusoutput(cmd)
    if o[0] != 0:
        print "Failed to execute cmd [%s], errno = [%d]" % (cmd, o[0])

        # the max errno which unix/linux shell support may be 256, so
        # here when error occurs, we do not use the real errno return
        # by executing command, instead, we use a fixed
        # errno: errnos.errors['shell_cmd_exec_failed']
        if (ignore_error == None):
            sys.exit(errnos.errors['shell_cmd_exec_failed'])

    return o

if __name__ == '__main__':
    print execute('ls -l')
    print execute('ls 1.zip')
