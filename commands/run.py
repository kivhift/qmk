import subprocess

import qmk

class RunCommand(qmk.Command):
    '''Run arbitrary processes.'''
    def __init__(self):
        self._name = '!'
        self._help = self.__doc__

    def action(self, arg):
        if arg is None: return
        pid = subprocess.Popen(arg).pid

def commands(): return [ RunCommand() ]
