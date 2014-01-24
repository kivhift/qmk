#
# Copyright (c) 2014 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class OEDCommand(qmk.Command):
    '''Look up the given argument using Oxford's dictionary search.  A new tab
    will be opened with the results.'''
    def __init__(self):
        self._name = 'oed'
        self._help = self.__doc__
        self.__baseURL = (
            'http://www.oxforddictionaries.com/search/english/?q=%s')

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(self.__baseURL % urllib.quote_plus(
            '-'.join(arg.split()).encode('utf-8')))

def commands(): return [ OEDCommand() ]
