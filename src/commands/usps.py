#
# Copyright (c) 2012 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class USPSCommand(qmk.Command):
    """
    View the tracking information for the given tracking number at usps.com.
    """
    def __init__(self):
        self._name = 'usps'
        self._help = self.__doc__
        self.__baseURL = ('https://tools.usps.com/go/'
            'TrackConfirmAction_input?qtc_tLabels1=%s')

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        query = self.__baseURL % urllib.quote_plus(
            arg.split()[0].encode('utf-8'))
        webbrowser.open_new_tab(query)

def commands(): return [ USPSCommand() ]
