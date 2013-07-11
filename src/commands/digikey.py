#
# Copyright (c) 2013 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class DigikeyCommand(qmk.Command):
    """Look up a part on Digi-Key.

    A new tab will be opened in the default web browser that contains the
    search results.
    """
    def __init__(self):
        self._name = 'digikey'
        self._help = self.__doc__
        self.__baseURL = 'http://www.digikey.com/product-search/en?KeyWords={}'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(self.__baseURL.format(urllib.quote_plus(
            ' '.join(arg.split()).encode('utf-8'))))

def commands(): return [ DigikeyCommand() ]
