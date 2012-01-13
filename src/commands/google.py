#
# Copyright (c) 2009-2012 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class GoogleCommand(qmk.Command):
    '''Google the given arguments.  A new tab will be opened in the
    default web browser with the Google search results.'''
    def __init__(self):
        self._name = 'google'
        self._help = self.__doc__
        self.__baseURL = 'http://www.google.com/search?q=%s'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(self.__baseURL % urllib.quote_plus(
            ' '.join(arg.split()).encode('utf-8')))

def commands(): return [ GoogleCommand() ]
