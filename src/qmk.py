#!/usr/bin/python

import ctypes
import optparse
import os
import time

from PyQt4 import QtCore, QtGui

import qrc_qmk_resources

import utils

class InputFilterError(Exception): pass

class InputFilter(utils.Singleton):
    def __init__(self, filter_lib = 'qmk-hook.dll'):
        # void F(int arg);
        self.__cbp = ctypes.CFUNCTYPE(None, ctypes.c_int)
        self.__hook = ctypes.CDLL(filter_lib)
        self.__qmkkbcb = None
        self.__kbcb = None
        self.__mcb = None
        if self.__hook.install_keyboard_hook():
            raise InputFilterError(
                'Had trouble installing keyboard hook.')
        if self.__hook.install_mouse_hook():
            raise InputFilterError(
                'Had trouble installing mouse hook.')
        InputFilter.__init__ = utils.Singleton._init_me_not

    def setQMKKeyboardCallback(self, cb):
        self.__qmkkbcb = self.__cbp(cb)

    def enableQMKKeyboardCallback(self):
        self.__hook.set_qmk_keyboard_hook_callback(self.__qmkkbcb)

    def disableQMKKeyboardCallback(self):
        self.__hook.set_qmk_keyboard_hook_callback(None)

    def setKeyboardCallback(self, cb):
        self.__kbcb = self.__cbp(cb)

    def enableKeyboardCallback(self):
        self.__hook.set_keyboard_hook_callback(self.__kbcb)

    def disableKeyboardCallback(self):
        self.__hook.set_keyboard_hook_callback(None)

    def setKeyboardWindowId(self, wid):
        self.__hook.set_keyboard_window_id(wid)

    def setMouseCallback(self, cb):
        self.__mcb = self.__cbp(cb)

    def enableMouseCallback(self):
        self.__hook.set_mouse_hook_callback(self.__mcb)

    def disableMouseCallback(self):
        self.__hook.set_mouse_hook_callback(None)

    def injectFullKeystroke(self):
        self.__hook.inject_press_and_release()

    def foregroundWindowId(self):
        return self.__hook.get_foreground_window_id()

#formatted help with .format_help()
class CommandOptionParser(optparse.OptionParser):
    def __init__(self, *a, **kwa):
        name = kwa.pop('name', None)
        if name is not None and not kwa.has_key('usage'):
            kwa['usage'] = '%s [options]' % name
        if not kwa.has_key('add_help_option'):
            kwa['add_help_option'] = False

        optparse.OptionParser.__init__(self, *a, **kwa)

    def error(self, msg):
        raise RuntimeError(msg)

class Command(object):
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._name = None
        obj._help = 'No help for this command.'
        obj._optpar = None
        return obj

    def __name(self):
        return self._name
    name = property(fget = __name)

    def __help(self):
        wh = '\n\n'.join(utils.wrapped_paragraphs(self._help, 75))
        if self._optpar is None:
            return wh
        else:
            return '%s\n\n%s' % (wh, self._optpar.format_help())
    help = property(fget = __help)

    def action(self, arg):
        pass

    def shutdown(self):
        pass

    @staticmethod
    def actionRequiresArgument(fn):
        def ar(self, arg):
            if arg is None:
                arg = str(Clipboard.text())
                if '' == arg:
                    raise ValueError('Argument required.')
            return fn(self, arg)
        ar.__name__ = fn.__name__
        ar.__doc__ = fn.__doc__
        ar.__dict__.update(fn.__dict__)
        return ar

class Message(utils.Singleton, QtGui.QWidget):
    def __call__(self, text):
        self.setText(text)
        self.show()

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setStyleSheet('''\
QTextEdit {
    background-color: #000000;
    color: #00ff00;
    border: 2px dotted #00ff00;
    border-radius: 4px;
    font-family: "Dejavu Sans Mono";
}
''')
        self.setWindowFlags(QtCore.Qt.ToolTip |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)

        self.__lo = QtGui.QVBoxLayout()
        self.__lo.setContentsMargins(0, 0, 0, 0)
        self.__te = QtGui.QTextEdit()
        self.__te.setReadOnly(True)
        self.__lo.addWidget(self.__te)
        self.setLayout(self.__lo)

        self.resize(324, 200)

        dt = QtGui.qApp.desktop()
        ag = dt.availableGeometry(dt.primaryScreen())
        fg = self.frameGeometry()
        self.move(((ag.width() / 2) - ag.x()) - (fg.width() / 2),
            ((ag.height() / 2) - ag.y()) - (fg.height() / 2))
        Message.__init__ = utils.Singleton._init_me_not

    def setText(self, text):
        self.__te.setText(text)

    def show(self):
        filt = InputFilter()
        filt.enableKeyboardCallback()
        filt.enableMouseCallback()
        QtGui.QWidget.show(self)

class ErrorMessage(utils.Singleton, QtGui.QDialog):
    def __call__(self, text):
        self.append(text)
        self.show()

    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.setStyleSheet('''\
QTextEdit {
    background-color: #000000;
    color: #ffff00;
    border: 2px dotted #00ff00;
    border-radius: 4px;
    font-family: "Dejavu Sans Mono";
}
''')
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)
        self.setWindowTitle('QMK Errors')

        self.__lo = QtGui.QVBoxLayout()
        self.__lo.setContentsMargins(0, 0, 0, 0)
        self.__te = QtGui.QTextEdit()
        self.__te.setReadOnly(True)
        self.__lo.addWidget(self.__te)
        self.setLayout(self.__lo)

        dt = QtGui.qApp.desktop()
        ag = dt.availableGeometry(dt.primaryScreen())

        self.resize(ag.width() / 2, int(ag.width() / (1.0 + 5.0**0.5)))
        fg = self.frameGeometry()
        self.move(ag.width() - fg.width(), ag.height() - fg.height())

        ErrorMessage.__init__ = utils.Singleton._init_me_not

    def append(self, text):
        self.__te.append('%s: %s' % (
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), text))

def capture_and_show_exceptions(name):
    def deco(fn):
        def nfn(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception, e:
                ErrorMessage()('%s: %s' % (name, str(e)))
        return nfn
    return deco

class Completer(QtGui.QCompleter):
    def setCurrentIndex(self, index):
        pu = self.popup()
        sm = pu.selectionModel()
        if not index.isValid():
            sm.clear()
        else:
            sm.setCurrentIndex(index, QtGui.QItemSelectionModel.Select
                | QtGui.QItemSelectionModel.Rows)
        ci = sm.currentIndex()
        if not ci.isValid():
            pu.scrollToTop()
        else:
            pu.scrollTo(ci, QtGui.QAbstractItemView.PositionAtTop)

    def eventFilter(self, obj, ev):
        if QtCore.QEvent.KeyPress == ev.type():
            pu = self.popup()
            if pu and pu.isVisible():
                ci = pu.currentIndex()
                cm = self.completionModel()
                ek = ev.key()
                if ek == QtCore.Qt.Key_Tab:
                    if not ci.isValid():
                        fi = cm.index(0, self.completionColumn())
                        self.setCurrentIndex(fi)
                        return True
                    elif ci.row() == cm.rowCount() - 1:
                        if self.wrapAround():
                            self.setCurrentIndex(QtCore.QModelIndex())
                        return True
                    return False
                elif ek == QtCore.Qt.Key_Backtab:
                    if not ci.isValid():
                        rc = cm.rowCount()
                        li = cm.index(rc - 1, self.completionColumn())
                        self.setCurrentIndex(li)
                        return True
                    elif 0 == ci.row():
                        if self.wrapAround():
                            self.setCurrentIndex(QtCore.QModelIndex())
                        return True
                    return False
        return QtGui.QCompleter.eventFilter(self, obj, ev)

class CommandInputLineEdit(QtGui.QLineEdit):
    def __init__(self, *a, **kw):
        QtGui.QLineEdit.__init__(self)

        self.postKeyPressEventCallbacks = {}

    def keyPressEvent(self, event):
        k = event.key()
        QtGui.QLineEdit.keyPressEvent(self, event)
        if self.postKeyPressEventCallbacks.has_key(k):
            self.postKeyPressEventCallbacks[k]()

class CommandInput(utils.Singleton, QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.connect(self, QtCore.SIGNAL('rejected()'),
            self.setRejected)

        self.__completer = None
        self.input = CommandInputLineEdit()
        self.input.setCursor(QtCore.Qt.BlankCursor)
        self.input.postKeyPressEventCallbacks[
            QtCore.Qt.Key_Up] = self.historyBackward
        self.input.postKeyPressEventCallbacks[
            QtCore.Qt.Key_Down] = self.historyForward

        self.__history = []
        self.__history_idx = 0

        self.__lo = QtGui.QVBoxLayout()
        self.__lo.setContentsMargins(0, 0, 0, 0)
        self.__lo.setSpacing(0)
        self.__lo.addWidget(self.input)
        self.setLayout(self.__lo)

        self.__qa = QtGui.QAction('&Quit', self)
        self.connect(self.__qa, QtCore.SIGNAL('triggered()'),
            QtGui.qApp, QtCore.SLOT('quit()'))

        self.__tim = QtGui.QMenu(self)
        self.__tim.addAction(self.__qa)
        self.__ti = QtGui.QSystemTrayIcon(self)
        self.__ti.setToolTip(self.tr('QMK'))
        self.__ti.setIcon(QtGui.QIcon(':images/qmk-icon.png'))
        self.__ti.setContextMenu(self.__tim)
        self.__ti.show()

        self.setWindowTitle(self.tr('QMK Input'))

        flags = QtCore.Qt.CustomizeWindowHint \
            | QtCore.Qt.FramelessWindowHint \
            | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.85)

        self.__cursor_pos = QtCore.QPoint(0, 0)

        self.move(0, 0)

        dt = QtGui.qApp.desktop()
        ag = dt.availableGeometry(dt.primaryScreen())
        self.resize(ag.width() / 2, 0)

        CommandInput.__init__ = utils.Singleton._init_me_not

    def historyForward(self):
        hl = len(self.__history)
        if 0 == hl: return

        self.__history_idx += 1
        if self.__history_idx >= hl:
            self.__history_idx = 0
        self.input.setText(self.__history[self.__history_idx])

    def historyBackward(self):
        hl = len(self.__history)
        if 0 == hl: return

        self.__history_idx -= 1
        if self.__history_idx < 0:
            self.__history_idx = hl - 1
        self.input.setText(self.__history[self.__history_idx])

    def show(self):
        self.wasRejected = False
###     self.__cursor_pos = QtGui.QCursor.pos()
        QtGui.QDialog.show(self)
        # This is a kludge.  The window should be unmovable.
        #QtGui.QCursor.setPos(10, 10)

    def hide(self):
        QtGui.QDialog.hide(self)
###     QtGui.QCursor.setPos(self.__cursor_pos)
        if self.__completer is not None:
            self.__completer.popup().hide()

    def setRejected(self):
        self.wasRejected = True

    def runCommand(self):
        cmd = unicode(self.input.text()).strip()
        if '' == cmd: return

        part = cmd.split(None, 1)

        # Check arg count here, etc.
        if CommandManager().runCommand(part[0],
                part[1] if len(part) > 1 else None):
            if 0 == len(self.__history) or cmd != self.__history[-1]:
                self.__history.append(cmd)
            self.__history_idx = len(self.__history)

    def updateCompletions(self):
        cn = CommandManager().commandNames()
        if 0 == len(cn):
            self.__completer = None
        else:
            self.__completer = Completer(cn)
            self.__completer.popup().setTabKeyNavigation(True)
        self.input.setCompleter(self.__completer)

class CommandManager(utils.Singleton):
    def __init__(self):
        self.__cmd = {}
        CommandManager.__init__ = utils.Singleton._init_me_not

    def registerCommands(self, cmds):
        for cmd in cmds:
            self.__cmd[cmd.name] = cmd

    def runCommand(self, name, arg):
        '''Return True if successful, False otherwise.'''
        try:
            if self.__cmd.has_key(name):
                self.__cmd[name].action(arg)
            elif self.__cmd.has_key('eval'):
                self.__cmd['eval'].action(
                    '%s%s' % (name, '' if arg is None else ' ' + arg))
            else:
                ErrorMessage()('Not found: "%s" <-- "%s"' % (name, arg))
                return False
        except Exception, e:
            ErrorMessage()('%s: %s' % (name, str(e)))
            return False

        return True

    def commandNames(self):
        N = self.__cmd.keys()
        N.sort()
        return N

    def command(self, name):
        return self.__cmd[name]

    def shutdownCommands(self):
        for k in self.__cmd.keys():
            self.__cmd[k].shutdown()
            del self.__cmd[k]

class Engine(object):
    @staticmethod
    def QMKCallback(qmk_down):
        ci = CommandInput()

        if qmk_down:
            ci.input.clear()
            ci.show()
            return

        ci.hide()

        if ci.wasRejected:
            return

        if ci.input.text().isEmpty():
            #InputFilter.get().injectFullKeystroke()
            return

        ci.runCommand()

    @staticmethod
    def hideMessageCallback(qmk_down):
        if qmk_down: return

        msg = Message()
        if msg.isVisible():
            filt = InputFilter()
            filt.disableKeyboardCallback()
            filt.disableMouseCallback()
            msg.hide()

class Clipboard(object):
    @staticmethod
    def setText(text):
        QtGui.qApp.clipboard().setText(text)

    @staticmethod
    def text():
        return QtGui.qApp.clipboard().text()

def base_dir():
    return os.path.join(utils.get_user_info()['HOME'], '.qmk')
