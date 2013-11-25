#
# Copyright (c) 2013 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class DuckDuckGoCommand(qmk.Command):
    '''Duckduckgo the given arguments.  A new tab will be opened in the
    default web browser with the search results.'''
    def __init__(self):
        self._name = 'duckduckgo'
        self._help = self.__doc__
        self.__baseURL = 'https://duckduckgo.com/?q=%s'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(self.__baseURL % urllib.quote_plus(
            ' '.join(arg.split()).encode('utf-8')))

def commands(): return [ DuckDuckGoCommand() ]
