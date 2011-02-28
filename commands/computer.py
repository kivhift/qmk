import ctypes

import qmk

class ComputerCommand(qmk.Command):
    '''Hibernate, suspend, shutdown or reboot the computer or log off.'''
    # These are from winuser.h.
    EWX_LOGOFF = 0
    EWX_POWEROFF = 8
    EWX_REBOOT = 2
    EWX_FORCEIFHUNG = 16
    def __init__(self):
        self._name = 'computer'
        self._help = self.__doc__

    def hibernate(self):
        ctypes.windll.powrprof.SetSuspendState(1, 0, 0)

    def suspend(self):
        ctypes.windll.powrprof.SetSuspendState(0, 0, 0)

    def shutdown(self):
        ctypes.windll.user32.ExitWindowsEx(ComputerCommand.EWX_POWEROFF, 0)

    def reboot(self):
        ctypes.windll.user32.ExitWindowsEx(ComputerCommand.EWX_REBOOT, 0)

    def logoff(self):
        ctypes.windll.user32.ExitWindowsEx(ComputerCommand.EWX_LOGOFF, 0)

    def action(self, arg):
        if arg is None: return

        for a in 'hibernate suspend shutdown reboot logoff'.split():
            if a.startswith(arg): return getattr(self, a)()

        qmk.ErrorMessage()('Invalid request: %s' % arg)

def commands(): return [ ComputerCommand() ]
