import urllib
import webbrowser

import qmk

class OctopartCommand(qmk.Command):
    '''Look up a part on Octopart.  A new tab will be opened in the
    default web browser that contains the search results.'''
    def __init__(self):
        self._name = 'octopart'
        self._help = self.__doc__
        self.__baseURL = 'http://octopart.com/parts/search?q=%s&js=on'

    def action(self, arg):
        if arg is None: return
        text = arg.strip()
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(
            ' '.join(text.split()).encode('utf-8'))
        webbrowser.open_new_tab(query)

def commands(): return [ OctopartCommand() ]
