#
# Copyright (c) 2014 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class WikipediaCommand(qmk.Command):
    """Look up the given argument in Wikipedia."""
    def __init__(self):
        self._name = 'wikipedia'
        self._help = self.__doc__
        self.__baseURL = 'https://en.wikipedia.org/wiki/{}'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(self.__baseURL.format(
            urllib.quote_plus('_'.join(arg.split())).encode('utf-8')))

def commands(): return [ WikipediaCommand() ]
