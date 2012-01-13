#
# Copyright (c) 2011-2012 Joshua Hughes <kivhift@gmail.com>
#
import qmk
import pu.utils

class RotateNCommand(qmk.Command):
    '''Perform a Caesar cipher and return the result.'''
    def __init__(self):
        self._name = 'rotate-n'
        self._help = self.__doc__

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        qmk.Message()(pu.utils.rotn(arg))

def commands(): return [ RotateNCommand() ]
