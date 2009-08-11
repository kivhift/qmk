#!/usr/bin/python

# Could perhaps get tab-completion by reimplementing keyPressEvent() for
# the QLineEdit (and possibly keyPressEvent() for the QCompleter as well).
# See the Tools > Custom Completer example for ideas.

import ctypes
#import subprocess

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
		self.__cb = None
		if self.__hook.install_keyboard_hook():
			raise InputFilterError('Had trouble installing hook.')
	
	def setCallback(self, cb):
		self.__cb = self.__cbp(cb)
		self.__hook.set_keyboard_hook_callback(self.__cb)
	
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

class Message(QtGui.QDialog):
	def __init__(self, title = '', text = ''):
		QtGui.QDialog.__init__(self)

		self.setStyleSheet('''\
QGroupBox {
	background-color: #000000;
	border: 2px solid #00ff00;
	border-radius: 4px;
	margin-top: 1em;
	font-size: 14px;
	font-family: "Dejavu Sans Mono";
}
QGroupBox::title {
	background-color: #000000;
	border: 2px solid #00ff00;
	border-radius: 4px;
	color: #00ff00;
	subcontrol-origin: margin;
	subcontrol-position: top left;
	padding 3px 3px 3px 3px;
}
QTextEdit {
	background-color: #000000;
	color: #00ff00;
	border: 2px dotted #00ff00;
	border-radius: 4px;
	font-family: "Dejavu Sans Mono";
}
''')
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | \
			QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		#self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		self.__gb = QtGui.QGroupBox()
		self.__lo = QtGui.QVBoxLayout()
		self.__lo.setContentsMargins(0, 0, 0, 0)
		self.__lo.addWidget(self.__gb)
		self.setLayout(self.__lo)

		self.__gblo = QtGui.QVBoxLayout()
		self.__te = QtGui.QTextEdit()
		self.__te.setReadOnly(True)
		self.__gblo.addWidget(self.__te)
		self.__gb.setLayout(self.__gblo)

		self.resize(300, 200)

		dt = QtGui.qApp.desktop()
		ag = dt.availableGeometry(dt.primaryScreen())
		fg = self.frameGeometry()
		self.move((ag.width() - ag.x()) - fg.width(),
			(ag.height() - ag.y()) - fg.height())
		self.setWindowTitle(title)
		self.__gb.setTitle(title)
		self.__te.setText(text)

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
#		self.__comp = QtGui.QCompleter(
#			['effort', 'cook', 'cat', 'dog', 'quit', 'quack'],
#			self)
#		self.__comp.popup().setTabKeyNavigation(True)
#		self.input.setCompleter(self.__comp)

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

		self.__cursor_pos = QtCore.QPoint(0, 0)

		self.move(0, 0)

	def show(self):
		self.wasRejected = False
		self.__cursor_pos = QtGui.QCursor.pos()
		QtGui.QDialog.show(self)
		# This is a kludge.  The window should be unmovable.
		#QtGui.QCursor.setPos(10, 10)

	def hide(self):
		QtGui.QDialog.hide(self)
		QtGui.QCursor.setPos(self.__cursor_pos)

	def setRejected(self):
		self.wasRejected = True

	def runCommand(self):
		cmd = unicode(self.input.text()).strip()
		if '' == cmd: return

		part = cmd.split(None, 1)

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
		if self.__cmd.has_key(name):
			self.__cmd[name].action(arg)
		else:
			print 'Not found: "%s" <-- "%s"' % (name, arg)
#			args = [name]
#			if arg is not None: args += arg
#			subprocess.Popen(args)

	def commandNames(self):
		N = self.__cmd.keys()
		N.sort()
		return N

	def command(self, name):
		return self.__cmd[name]

class Engine(object):
	@staticmethod
	def callback(qmk_down):
		ci = CommandInput.get()

		if qmk_down:
			ci.input.clear()
			ci.show()
			return

		ci.hide()

		if ci.wasRejected:
			return

		if ci.input.text().isEmpty():
			InputFilter.get().injectFullKeystroke()
			return

		ci.runCommand()
