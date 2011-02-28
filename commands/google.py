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

    def action(self, arg):
        if arg is None: return
        text = arg.strip()
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(
            ' '.join(text.split()).encode('utf-8'))
        webbrowser.open_new_tab(query)

def commands(): return [ GoogleCommand() ]
