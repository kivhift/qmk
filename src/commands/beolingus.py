#
# Copyright (c) 2009-2012 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class BeolingusCommand(qmk.Command):
    '''Look up a German word using Beolingus.  A new tab will be opened
    in the default web browser with the search results.'''
    def __init__(self):
        self._name = 'beolingus'
        self._help = self.__doc__
        self.__baseURL = 'http://dict.tu-chemnitz.de/?query=%s' \
            '&service=deen&mini=1'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(
            self.__baseURL % urllib.quote_plus(arg.encode('latin_1')))

def commands(): return [ BeolingusCommand() ]
