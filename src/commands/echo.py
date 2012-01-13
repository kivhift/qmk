#
# Copyright (c) 2011-2012 Joshua Hughes <kivhift@gmail.com>
#
import qmk

class EchoCommand(qmk.Command):
    '''Echo the argument.'''
    def __init__(self):
        self._name = 'echo'
        self._help = self.__doc__

    def action(self, arg):
        qmk.Message()('' if arg is None else arg)

def commands(): return [ EchoCommand() ]
