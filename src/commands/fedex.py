import urllib
import webbrowser

import qmk

class FedexCommand(qmk.Command):
    '''Use the Fedex website to view the tracking info for the given
    tracking number.'''
    def __init__(self):
        self._name = 'fedex'
        self._help = self.__doc__
        self.__baseURL = 'http://www.fedex.com/Tracking' \
                '?clienttype=dotcom&ascend_header=1&cntry_code=us' \
                '&language=english&mi=n&tracknumbers=%s'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        query = self.__baseURL % urllib.quote_plus(
            arg.split()[0].encode('utf-8'))
        webbrowser.open_new_tab(query)

def commands(): return [ FedexCommand() ]
