#
# Copyright (c) 2009-2012 Joshua Hughes <kivhift@gmail.com>
#
import datetime

import qmk

class DateCommand(qmk.Command):
    '''View the current date.'''
    def __init__(self):
        self._name = 'date'
        self._help = self.__doc__

    def action(self, arg):
        now = str(datetime.datetime.now())
        qmk.Message()(now)

def commands(): return [ DateCommand() ]
