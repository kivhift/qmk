#
# Copyright (c) 2009-2012 Joshua Hughes <kivhift@gmail.com>
#
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

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(self.__baseURL % urllib.quote_plus(
                        ' '.join(arg.split()).encode('utf-8')))

def commands(): return [ OctopartCommand() ]
