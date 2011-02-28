import qmk

from conversion.pressure import Pressure
from conversion.temperature import Temperature
from conversion.volume import Volume

class ConvertCommand(qmk.Command):
    '''Convert values with given units to other units.'''
    def __init__(self):
        self._name = 'convert'
        self._help = self.__doc__

        self.__P = Pressure()
        self.__T = Temperature()
        self.__V = Volume()

    def action(self, arg):
        if arg is None: return
        arg = arg.split()
        if len(arg) != 3: return
        try:
            val = float(arg[0])
        except:
            return
        fu, tu = arg[1], arg[2]
        if fu in self.__P.available_units():
            co = self.__P
        elif fu in self.__T.available_units():
            co = self.__T
        elif fu in self.__V.available_units():
            co = self.__V
        else:
            return

        if not tu in co.available_units():
            return

        setattr(co, fu, val)

        qmk.Message()('%s %s --> %f %s' % (
            arg[0], fu, getattr(co, tu), tu))

def commands(): return [ ConvertCommand() ]
