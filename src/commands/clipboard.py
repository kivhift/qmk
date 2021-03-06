#
# Copyright (c) 2010-2012 Joshua Hughes <kivhift@gmail.com>
#
import qmk

class ClipboardCommand(qmk.Command):
    '''Show the contents of the clipboard or set it to the given argument.'''
    def __init__(self):
        self._name = 'clipboard'
        self._help = self.__doc__

    def action(self, arg):
        if arg is None:
            qmk.Message()(qmk.Clipboard.text())
        elif arg in ('-c', '--clear'):
            qmk.Clipboard.setText('')
        else:
            qmk.Clipboard.setText(arg)

def commands(): return [ ClipboardCommand() ]
