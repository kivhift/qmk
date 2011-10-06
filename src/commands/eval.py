from math import *

import qmk

class EvalCommand(qmk.Command):
    '''Pass arguments to Python's eval() builtin.'''
    def __init__(self):
        self._name = 'eval'
        self._help = self.__doc__

    def action(self, arg):
        if arg is None:
            arg = qmk.Clipboard.text()

        result = str(eval(arg))
        qmk.Clipboard.setText(result)
        qmk.Message()(arg + ' --> ' + result)

def commands(): return [ EvalCommand() ]
