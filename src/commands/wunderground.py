#
# Copyright (c) 2010-2012 Joshua Hughes <kivhift@gmail.com>
#
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

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(
            self.__baseURL % urllib.quote_plus(arg.encode('utf-8')))

def commands(): return [ WundergroundCommand() ]
