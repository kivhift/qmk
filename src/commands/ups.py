#
# Copyright (c) 2012 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class UPSCommand(qmk.Command):
    '''Use the UPS website to view the tracking info for the given tracking
    number.'''
    def __init__(self):
        self._name = 'ups'
        self._help = self.__doc__
        self.__baseURL = 'http://wwwapps.ups.com/WebTracking/' \
            'track?HTMLVersion=5.0&loc=en_US&Requester=UPSHome&' \
            'WBPM_lid=homepage%%2Fct1.html_pnl_trk&trackNums=%s&track.x=Track'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        query = self.__baseURL % urllib.quote_plus(
            arg.split()[0].encode('utf-8'))
        webbrowser.open_new_tab(query)

def commands(): return [ UPSCommand() ]
