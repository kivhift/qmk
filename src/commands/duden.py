# coding=utf-8
#
# Copyright (c) 2014 Joshua Hughes <kivhift@gmail.com>
#
import urllib
import webbrowser

import qmk

class DudenCommand(qmk.Command):
    '''Look up the given argument using Duden's dictionary search.  A new tab
    will be opened with the results.'''
    def __init__(self):
        self._name = 'duden'
        self._help = self.__doc__
        self.__baseURL = 'http://www.duden.de/rechtschreibung/{}'

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        webbrowser.open_new_tab(self.__baseURL.format(
            urllib.quote_plus('_'.join(arg.split()).encode('utf-8')
            .replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue')
            .replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
            .replace('ß', 'ss'))))

def commands(): return [ DudenCommand() ]
