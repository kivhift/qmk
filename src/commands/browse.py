#
# Copyright (c) 2009-2012 Joshua Hughes <kivhift@gmail.com>
#
import webbrowser

import qmk

class BrowseCommand(qmk.Command):
    '''Open the supplied URL in the default web browser.'''
    def __init__(self):
        self._name = 'browse'
        self._help = self.__doc__

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(arg)

def commands(): return [ BrowseCommand() ]
