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

    def action(self, arg):
        if arg is None: return
        text = arg.strip().split()[0]
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(
            text.encode('latin_1'))
        webbrowser.open_new_tab(query)

def commands(): return [ BeolingusCommand() ]
