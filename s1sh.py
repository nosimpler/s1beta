#!/usr/bin/env python

# s1sh.py - run simulations and create interactive env
#
# v 1.6.23
# rev 2013-01-21 (SL: minor order change)
# last major: (SL: local history file)

import os, readline, shutil, sys
from fn.cli import Console

# Main Fn starts here
if __name__ == '__main__':
    try:
        file_input = sys.argv[1]

    except:
        print "Usage:", sys.argv[0], 'file_input'
        sys.exit(1)

    # Force Readline stuff
    readline.parse_and_bind('set editing-mode vi')
    readline.parse_and_bind('\C-l: clear-screen')
    readline.parse_and_bind('tab: complete')

    # local and default
    fhist_default = '.s1sh_history'
    fhist_local = '.s1sh_hist_local'

    # check if the local file exists
    # and if not, copy the default over
    if not os.path.isfile(fhist_local):
        shutil.copyfile(fhist_default, fhist_local)

    # set the readline history file to fhist_local
    readline.read_history_file(fhist_local)

    if sys.platform.startswith('darwin'):
        readline.parse_and_bind('"^[[A": history-search-backward')
        readline.parse_and_bind('"^[[B": history-search-backward')

    elif sys.platform.startswith('linux'):
        readline.parse_and_bind('"\e[A": history-search-backward')
        readline.parse_and_bind('"\e[B": history-search-forward')

    # Run the console
    console = Console(file_input)
    console.cmdloop()
