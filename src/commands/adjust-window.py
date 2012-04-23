#
# Copyright (c) 2011-2012 Joshua Hughes <kivhift@gmail.com>
#
import ctypes
import ctypes.wintypes

import win32api

import qmk
import pu.utils

def adjust(coord, arg):
    tmp = coord

    if arg.startswith('-') or arg.startswith('+'):
        tmp += int(arg)
    elif arg.startswith('='):
        tmp = int(arg[1:])
    else:
        tmp = int(arg)

    return tmp

def check(p):
    msgs = []
    if p[2] < 1: msgs.append('invalid width: %d' % p[2])
    if p[3] < 1: msgs.append('invalid height: %d' % p[3])
    if msgs: raise ValueError('Error: ' + ', '.join(msgs))

class AdjustWindowCommand(qmk.Command):
    '''
    Adjust current window to new position and dimensions.

    The position and dimensions can be given as integer arguments in order of
    x, y, w and h (i.e., left, top, width and height) to adjust the window
    absolutely.  To relatively adjust the window, give the arguments as
    adjustments to the current value; e.g., to adjust to the left by ten
    pixels, give x-10: to the right by ten, give x+10.  To mix in absolute
    arguments with relative ones, just use =; e.g., w=200.  Any missing
    parameters use their current values.

    The single argument "info" can be given to get the corners of the
    current window along with its width and height.

    The single argument "desktop-info" can be given to get information about
    the desktop geometry.
    '''
    def __init__(self):
        self._name = 'adjust-window'
        self._help = self.__doc__

        self._gwr = ctypes.windll.user32.GetWindowRect
        self._mw = ctypes.windll.user32.MoveWindow
        self._gle = ctypes.windll.kernel32.GetLastError

    def indicateError(self, ecode):
        raise RuntimeError(
            'Error: %s' % (win32api.FormatMessage(ecode).strip()))

    def action(self, arg):
        if arg is None:
            args = []
        else:
            args = arg.split()

        rect = ctypes.wintypes.RECT()
        hwnd = qmk.InputFilter().foregroundWindowId()

        if not self._gwr(hwnd, ctypes.byref(rect)):
            self.indicateError(self._gle())

        if 0 == len(args):
            p = [ 0, 0, rect.right - rect.left, rect.bottom - rect.top, 1 ]
        elif 1 == len(args) and args[0] in ('info', 'desktop-info'):
            a0 = args[0]
            if 'info' == a0:
                qmk.Message()(
                    '     Left-top: (%d, %d)\n'
                    ' Right-bottom: (%d, %d)\n'
                    'Width, height: %d, %d' % (
                    rect.left, rect.top, rect.right, rect.bottom,
                    rect.right - rect.left, rect.bottom - rect.top))
                return
            elif 'desktop-info' == a0:
                qad = qmk.QtGui.QApplication.desktop()
                sc = qad.screenCount()
                shift = ' ' * 8
                msg = '  %sScreen count: %d\n%sPrimary screen: %d' % (
                        shift, sc, shift, qad.primaryScreen())

                for i in xrange(sc):
                    sg = qad.screenGeometry(i)
                    msg += '\n%2d:    Screen Geometry: %d, %d' % (
                        i, sg.width(), sg.height())
                    ag = qad.availableGeometry(i)
                    msg += '\n    Available geometry: %d, %d' % (
                        ag.width(), ag.height())

                qmk.Message()(msg)
                return
        elif pu.utils.contains_any(arg, 'xywh'):
            p = [ rect.left, rect.top,
                rect.right - rect.left, rect.bottom - rect.top, 1 ]
            n = dict(x = 0, y = 1, w = 2, h = 3)
            for a in args:
                for c in 'xywh':
                    if a.startswith(c):
                        p[n[c]] = adjust(p[n[c]], a[1:])
                        break
        else:
            p = [ rect.left, rect.top,
                rect.right - rect.left, rect.bottom - rect.top, 1 ]
            for i in xrange(len(args)):
                p[i] = int(args[i])

        check(p)

        if not self._mw(hwnd, *p):
            self.indicateError(self._gle())

def commands(): return [ AdjustWindowCommand() ]
