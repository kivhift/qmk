import ctypes

import win32api

import qmk
import utils

class ComputerCommand(qmk.Command):
    '''
    Hibernate, suspend, shutdown, reboot or lock the computer or log off.
    '''
    # These are from winuser.h.
    EWX_LOGOFF = 0
    EWX_POWEROFF = 8
    EWX_REBOOT = 2
    EWX_FORCEIFHUNG = 16
    def __init__(self):
        self._name = 'computer'
        self._help = self.__doc__
        self._sss = ctypes.windll.powrprof.SetSuspendState
        self._ewe = ctypes.windll.user32.ExitWindowsEx
        self._gle = ctypes.windll.kernel32.GetLastError
        self._lws = ctypes.windll.user32.LockWorkStation

    def indicateError(self, ecode):
        raise RuntimeError('%s: %s' % (utils.caller_function_name(),
            win32api.FormatMessage(ecode).strip()))

    def _hibernate(self):
        if not self._sss(1, 0, 0):
            self.indicateError(self._gle())

    def _suspend(self):
        if not self._sss(0, 0, 0):
            self.indicateError(self._gle())

    def _shutdown(self):
        if not self._ewe(ComputerCommand.EWX_POWEROFF, 0):
            self.indicateError(self._gle())

    def _reboot(self):
        if not self._ewe(ComputerCommand.EWX_REBOOT, 0):
            self.indicateError(self._gle())

    def _lock(self):
        if not self._lws():
            self.indicateError(self._gle())

    def _logoff(self):
        if not self._ewe(ComputerCommand.EWX_LOGOFF, 0):
            self.indicateError(self._gle())

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        for a in 'hibernate suspend shutdown reboot lock logoff'.split():
            if a.startswith(arg): return getattr(self, '_%s' % a)()

        raise ValueError('Invalid request: %s' % arg)

def commands(): return [ ComputerCommand() ]
