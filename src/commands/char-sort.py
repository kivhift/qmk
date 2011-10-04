import qmk

class CharSortCommand(qmk.Command):
    '''
    Sort the characters of the given argument.  The result is shown and placed
    on the clipboard.
    '''
    def __init__(self):
        self._name = 'char-sort'
        self._help = self.__doc__

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        la = list(arg)
        la.sort()
        res = ''.join(la)
        qmk.Clipboard.setText(res)
        qmk.Message()('"%s" ==> "%s"' % (arg, res))

def commands(): return [ CharSortCommand() ]
