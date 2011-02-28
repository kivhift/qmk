import urllib
import webbrowser

import qmk

class WundergroundCommand(qmk.Command):
    '''Look up the current weather conditions for a given ZIP code (or
    airport code) using Weather Underground.  A new tab will be opened
    in the default web browser that contains the search results.'''
    def __init__(self):
        self._name = 'wunderground'
        self._help = self.__doc__
        self.__baseURL = 'http://www.wunderground.com/cgi-bin' \
        '/findweather/getForecast?query=%s&wuSelect=WEATHER'

    def action(self, arg):
        if arg is None: return
        text = arg.strip()
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(text.encode('utf-8'))
        webbrowser.open_new_tab(query)

def commands(): return [ WundergroundCommand() ]
