#
# Copyright (c) 2011-2012 Joshua Hughes <kivhift@gmail.com>
#
import imp
import os

import qmk

class RegisterCommandsCommand(qmk.Command):
    '''Register the commands in the given module.'''
    def __init__(self):
        self._name = 'register-commands'
        self._help = self.__doc__

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        filename = arg
        modname = os.path.splitext(os.path.basename(filename))[0]
        with open(filename, 'rb') as f:
            c = imp.load_module(
                modname, f, filename, ('.py', 'rb', imp.PY_SOURCE))
        qmk.CommandManager().registerCommands(c.commands())
        qmk.CommandInput().updateCompletions()

def commands(): return [ RegisterCommandsCommand() ]
