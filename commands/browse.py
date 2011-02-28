import webbrowser

import qmk

class BrowseCommand(qmk.Command):
    '''Open the supplied URL in the default web browser.'''
    def __init__(self):
        self._name = 'browse'
        self._help = self.__doc__

    def action(self, arg):
        if arg is None: return
        webbrowser.open_new_tab(arg)

def commands(): return [ BrowseCommand() ]
