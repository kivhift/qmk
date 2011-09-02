import ctypes
import ctypes.wintypes
import os

import win32api

from PyQt4 import QtCore, QtGui

import qmk
import utils

class ScreenshotCommand(qmk.Command):
    '''
    Take a screenshot of the current window.
    '''
    def __init__(self):
        self._name = 'screenshot'
        self._help = self.__doc__

        self._gfw = ctypes.windll.user32.GetForegroundWindow
        self._gwr = ctypes.windll.user32.GetWindowRect
        self._gle = ctypes.windll.kernel32.GetLastError

        op = qmk.CommandOptionParser(name = self._name)
        op.add_option('-b', '--bare', dest = 'bare', default = False,
            action = 'store_true', help = 'grab window with titlebar, etc.')
        op.add_option('--clobber', dest = 'clobber', default = False,
            action = 'store_true', help = 'clobber file if it exists')
        op.add_option('-d', '--desktop', dest = 'desktop', default = False,
            action = 'store_true', help = 'grab entire desktop')
        op.add_option('-f', '--filename', dest = 'filename', default = '',
            help = 'name of file to write snapshot to')
        op.add_option('-w', '--wait', dest = 'wait', default = 1,
            action = 'store', type = 'int',
            help = 'number of seconds to wait before screenshot')
        self._optpar = op

    def _indicateError(self, ecode):
        raise RuntimeError(
            'Error: %s' % (win32api.FormatMessage(ecode).strip()))

    @qmk.capture_and_show_exceptions('screenshot')
    def _take_snapshot(self):
        o = self._opts

        if '' == o.filename:
            fn = 'screenshot-%s.png' % utils.dt_str(sep = '')
        elif not o.filename.endswith(('.PNG', '.png')):
            fn = '%s.png' % o.filename
        else:
            fn = o.filename

        afn = os.path.abspath(fn)

        if os.path.exists(fn):
            if os.path.isfile(fn):
                if not o.clobber:
                    raise RuntimeError('%s exists and not clobbering.' % fn)
            else:
                raise RuntimeError('%s exists and is not a file.' % fn)

        dn = os.path.dirname(afn)
        if not os.path.exists(dn):
            raise RuntimeError('%s is not a valid directory.' % dn)

        R = ctypes.wintypes.RECT()
        hwnd = self._gfw()

        if not self._gwr(hwnd, ctypes.byref(R)):
            self._indicateError(self._gle())

        if o.desktop:
            pm = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
        elif o.bare:
            pm = QtGui.QPixmap.grabWindow(hwnd)
        else:
            pm = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),
                R.left, R.top, R.right - R.left, R.bottom - R.top)

        if pm is None:
            raise RuntimeError('Had trouble grabbing window.')

        if not pm.save(fn, 'PNG'):
            raise RuntimeError('Had trouble saving to %s.' % afn)

        qmk.Message()('Screenshot saved to %s.' % fn)

    def action(self, arg):
        self._opts, args = self._optpar.parse_args(
            args = [] if arg is None else arg.split())

        QtCore.QTimer.singleShot(1000 * self._opts.wait, self._take_snapshot)

        return

def commands(): return [ ScreenshotCommand() ]
