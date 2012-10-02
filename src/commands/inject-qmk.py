#
# Copyright (c) 2012 Joshua Hughes <kivhift@gmail.com>
#
import qmk

class InjectQMKCommand(qmk.Command):
    '''Inject the QMK.'''
    def __init__(self):
        super(InjectQMKCommand, self).__init__(self)
        self._name = 'INJECT-QMK'
        self._help = self.__doc__

    def action(self, arg):
        qmk.InputFilter().injectFullKeystroke()

def commands(): return [ InjectQMKCommand() ]
