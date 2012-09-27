#!/usr/bin/env python

# s1sh.py - run simulations and create interactive env
#
# v 1.2.0
# rev 2012-09-27 (SL: imported from aush)
# last major:

import readline, sys
from fn.cli import Console

# Main Fn starts here
if __name__ == '__main__':
    try:
        file_input = sys.argv[1]

    except:
        print "Usage:", sys.argv[0], 'file_input'
        sys.exit(1)

    # Force Readline stuff
    readline.parse_and_bind('\C-l: clear-screen')
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')
    readline.read_history_file('.s1sh_history')

    if sys.platform.startswith('darwin'):
        readline.parse_and_bind('"^[[A": history-search-backward')
        readline.parse_and_bind('"^[[B": history-search-backward')

    elif sys.platform.startswith('linux'):
        readline.parse_and_bind('"\e[A": history-search-backward')
        readline.parse_and_bind('"\e[B": history-search-forward')

    # Run the console
    console = Console(file_input)
    # try:
    #     console.cmdloop()
    # except (KeyboardInterrupt):
    #     print "Figure this out!"
    console.cmdloop()
