#
# Copyright (c) 2010-2012 Joshua Hughes <kivhift@gmail.com>
#
import qmk

from conversion.pressure import Pressure
from conversion.temperature import Temperature
from conversion.volume import Volume

class DummyConversion(object): pass

class ConvertCommand(qmk.Command):
    '''Convert values with given units to other units.'''
    def __init__(self):
        self._name = 'convert'
        self._help = self.__doc__

        self.__P = Pressure()
        self.__T = Temperature()
        self.__V = Volume()

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        args = arg.split()
        if len(args) != 3: raise ValueError('Three arguments required.')

        val, fu, tu = float(args[0]), args[1], args[2]
        co = DummyConversion()
        if fu in self.__P.available_units():
            co = self.__P
        elif fu in self.__T.available_units():
            co = self.__T
        elif fu in self.__V.available_units():
            co = self.__V

        setattr(co, fu, val)

        qmk.Message()('%s %s --> %f %s' % (
            args[0], fu, getattr(co, tu), tu))

def commands(): return [ ConvertCommand() ]
