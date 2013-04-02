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

import sys
import optparse
import errnos

def options_parse():
    usage = "usage: %prog [options] COMMAND args"
    description = "buildc is an assistant tool for project building and packing.\n"\
             + "\n  The most commonly used buildc commands are:\n"\
             + "  init                  init your own buildc configuration and .buildc.rc will be \n"\
             + "                        created in your home directory.\n"\
             + "\n"\
             + "  cache   init          checkout or clone repositories into local cache.\n"\
             + "          update        update the local repository cache when the some libraray changes. \n"\
             + "          upgrade       upgrade the local repository cache when repository \n"\
             + "                        config in .buildc.rc changes. \n"\
             + "          remove        remove the repositories in the local cache. \n"\
             + "\n"\
             + "  config  init          create buildc.cfg for your specific project. \n"\
             + "  config  make          generate or re-config Make.rules of your project \n"\
             + "                        according to the buildc.cfg.\n"\
             + "\n"\
             + "  pack    create        create an empty setup project.\n"\
             + "  pack    build         build the setup project.\n"\
             + "  pack    source        pack the project source.\n"\
             + "  pack    clean         clean the setup project.\n"\
             + "  pack    upload        upload the distribution package \n"\
             + "                        to a remote server through ftp.\n"

    #optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog
    optparse.OptionParser.format_description = lambda self, formatter: self.description
    p = optparse.OptionParser(usage = usage,
                              version="%prog 0.2.2",
                              description = description)

    p.add_option("-c", "--cmode", choices=["64-bit", "32-bit"], dest="cmode",
                                    help="compiling mode: [32-bit|64-bit]")
    p.add_option("-v", "--verbose", action="store_true", dest="verbose", default=True,
                                    help="output lots of details[default]")
    p.add_option("-t", "--tag", help="source tag")
    p.add_option("", "--project", help="setup project name")
    p.add_option("", "--host", help="ftp host")
    p.add_option("", "--user", help="ftp username")
    p.add_option("", "--passwd", help="ftp passwd")
    p.add_option("", "--port", help="ftp port")
    p.add_option("", "--dir", help="remote directory")
    p.add_option("", "--ignore-error", action="store_true",
                                    help="ignore svn does not exist corresponding to the third-party library")
    p.add_option("",  "--component", choices=["src", "deps", "all"],
                                    help="source component")

    (opt, args) = p.parse_args()
    if len(args) < 1:
        p.error("Have you read the Usage? Try [buildc --help]!")
        sys.exit(errnos.errors['args_invalid'])

    if len(args) < 2:
        if args[0] == 'cache':
            print 'Be careful! You lost the second arg!'
            print 'init, update, and remove are available for you, Just choose one of them!'
            sys.exit(errnos.errors['args_invalid'])

        if args[0] == 'pack':
            print 'Be careful! You lost the second arg!'
            print 'create, build, clean, upload are available for you, Just choose one of them!'
            sys.exit(errnos.errors['args_invalid'])

        if args[0] == 'config':
            print 'Be careful! You lost the second arg!'
            print 'init and make are available for you, Just choose one of them!'
            sys.exit(errnos.errors['args_invalid'])

        if args[0] != 'init':
            print "Unsupport command [%s], Try [buildc --help]!" % args[0]
            sys.exit(errnos.errors['args_invalid'])

    return (opt, args)

if __name__ == '__main__':
    opt, args = options_parse()
    print opt, args
    print opt.cmode
    print opt.verbose
