import qmk
import utils

class RotateNCommand(qmk.Command):
    '''Perform a Caesar cipher and return the result.'''
    def __init__(self):
        self._name = 'rotate-n'
        self._help = self.__doc__

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        qmk.Message()(utils.rotn(arg))

def commands(): return [ RotateNCommand() ]
