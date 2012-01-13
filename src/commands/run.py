#
# Copyright (c) 2009-2012 Joshua Hughes <kivhift@gmail.com>
#
import subprocess

import qmk

class RunCommand(qmk.Command):
    '''Run arbitrary processes.'''
    def __init__(self):
        self._name = '!'
        self._help = self.__doc__

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        pid = subprocess.Popen(arg).pid

def commands(): return [ RunCommand() ]
