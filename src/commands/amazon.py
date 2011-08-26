import urllib
import webbrowser

import qmk

class AmazonCommand(qmk.Command):
    '''Search www.amazon.com using the given arguments.  A new tab will be
    opened in the default web browser with the search results.'''
    def __init__(self):
        self._name = 'amazon'
        self._help = self.__doc__
        self.__baseURL = 'http://www.amazon.com/' \
            's?ie=UTF8&index=blended&field-keywords=%s'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        query = self.__baseURL % urllib.quote_plus(
            ' '.join(arg.split()).encode('utf-8'))
        webbrowser.open_new_tab(query)

def commands(): return [ AmazonCommand() ]
