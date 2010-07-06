#!/usr/bin/python

# Could perhaps get tab-completion by reimplementing keyPressEvent() for
# the QLineEdit (and possibly keyPressEvent() for the QCompleter as well).
# See the Tools > Custom Completer example for ideas.

import ctypes
import time

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtSvg

import qmk_resources

class InputFilterError(Exception): pass

class InputFilter(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

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

class Command(object):
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls, *args, **kwargs)
        obj._name = None
        obj._help = 'No help for this command.'
        return obj

    def __init__(self):
        pass

    def __name(self):
        return self._name
    name = property(fget = __name)

    def __help(self):
        return self._help
    help = property(fget = __help)

    def action(self, arg):
        pass

class Message(QtGui.QWidget):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

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

    def setText(self, text):
        self.__te.setText(text)

    def show(self):
        filt = InputFilter.get()
        filt.enableKeyboardCallback()
        filt.enableMouseCallback()
        QtGui.QWidget.show(self)

class ErrorMessage(QtGui.QDialog):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

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

    def append(self, text):
        self.__te.append('%s: %s' % (
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), text))

class CommandInput(QtGui.QDialog):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.connect(self, QtCore.SIGNAL('rejected()'),
            self.setRejected)

        self.input = QtGui.QLineEdit()
        self.input.setCursor(QtCore.Qt.BlankCursor)
#       self.__comp = QtGui.QCompleter(
#           ['effort', 'cook', 'cat', 'dog', 'quit', 'quack'],
#           self)
#       self.__comp.popup().setTabKeyNavigation(True)
#       self.input.setCompleter(self.__comp)

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
        self.__ti.setIcon(QtGui.QIcon(':images/qmk-icon.svg'))
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

    def show(self):
        self.wasRejected = False
###     self.__cursor_pos = QtGui.QCursor.pos()
        QtGui.QDialog.show(self)
        # This is a kludge.  The window should be unmovable.
        #QtGui.QCursor.setPos(10, 10)

    def hide(self):
        QtGui.QDialog.hide(self)
###     QtGui.QCursor.setPos(self.__cursor_pos)

    def setRejected(self):
        self.wasRejected = True

    def runCommand(self):
        cmd = unicode(self.input.text()).strip()
        if '' == cmd: return

        part = cmd.split(None, 1)

        # Check arg count here, etc.
        CommandManager.get().runCommand(part[0],
            part[1] if len(part) > 1 else None)

class CommandManager(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        self.__cmd = {}

    def registerCommands(self, cmds):
        for cmd in cmds:
            self.__cmd[cmd.name] = cmd

    def runCommand(self, name, arg):
        try:
            if self.__cmd.has_key(name):
                self.__cmd[name].action(arg)
            elif self.__cmd.has_key('eval'):
                self.__cmd['eval'].action(
                    '%s%s' % (name, '' if arg is None else ' ' + arg))
            else:
                ErrorMessage.get()('Not found: "%s" <-- "%s"' % (name, arg))
        except Exception, e:
            ErrorMessage.get()('Problem: %s' % str(e))

    def commandNames(self):
        N = self.__cmd.keys()
        N.sort()
        return N

    def command(self, name):
        return self.__cmd[name]

class Engine(object):
    @staticmethod
    def QMKCallback(qmk_down):
        ci = CommandInput.get()

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

        msg = Message.get()
        filt = InputFilter.get()
        if msg.isVisible():
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
