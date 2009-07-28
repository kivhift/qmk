#!/usr/bin/python

import sys
import re
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
	def __init__(self):
		self._name = None

	def __name(self):
		return self._name
	name = property(fget = __name)

	def action(self, arg):
		pass

class CommandInput(QtGui.QDialog):
	__instance = None

	@classmethod
	def get(cls):
		if cls.__instance is None:
			cls.__instance = cls()
		return cls.__instance

	def __init__(self):
		QtGui.QDialog.__init__(self)

		self.input = QtGui.QLineEdit()
		self.input.setCursor(QtCore.Qt.BlankCursor)
#		self.__comp = QtGui.QCompleter(
#			['effort', 'cook', 'cat', 'dog', 'quit', 'quack'],
#			self)
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
		self.__ti.setIcon(QtGui.QIcon(':images/qmk-icon.svg'))
		self.__ti.setContextMenu(self.__tim)
		self.__ti.show()

		self.setWindowTitle(self.tr('QMK Input'))

		flags = QtCore.Qt.CustomizeWindowHint \
			| QtCore.Qt.FramelessWindowHint
		self.setWindowFlags(flags)

		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

		self.cursor_pos = QtCore.QPoint(0, 0)

		self.move(0, 0)

	def show(self):
		self.cursor_pos = QtGui.QCursor.pos()
		QtGui.QDialog.show(self)
		# This is a kludge.  The window should be unmovable.
		QtGui.QCursor.setPos(10, 10)

	def hide(self):
		QtGui.QDialog.hide(self)
		QtGui.QCursor.setPos(self.cursor_pos)

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

class Engine(object):
	@staticmethod
	def callback(qmk_down):
		ci = CommandInput.get()

		if qmk_down:
			ci.input.clear()
			ci.show()
			return

		if not ci.isVisible():
			return

		ci.hide()

		if ci.input.text().isEmpty():
			InputFilter.get().injectFullKeystroke()
			return

		ci.runCommand()

if __name__ == '__main__':
	class QuitCommand(Command):
		def __init__(self):
			self._name = 'quit'

		def action(self, arg):
			# XXX Perhaps add some fancier shutdown stuff here.
			QtGui.qApp.quit()

	app = QtGui.QApplication([])
	app.setQuitOnLastWindowClosed(False)
	app.setWindowIcon(QtGui.QIcon(':images/qmk-icon.svg'))
	app.setStyleSheet('''\
	QLineEdit {
		background-color: #004b00;
		color: #00ff00;
		border-width: 2px;
		border-style: solid;
		border-color: #00ff00;
		border-radius: 5px;
		font-size: 20px;
		font-family: "Dejavu Sans Mono";
		padding: 3px;
		margin: 0px;
	}
	QListView {
		background-color: #004b00;
		color: #00ff00;
		border-width: 2px;
		border-style: solid;
		border-color: #00ff00;
		border-radius: 5px;
		font-size: 14px;
		font-family: "Dejavu Sans Mono";
	}
	''')

	filt = InputFilter.get()
	ci = CommandInput.get()
	cm = CommandManager.get()

	filt.setCallback(Engine.callback)

	cm.registerCommands([QuitCommand()])

	cm.registerCommands(__import__('commands').commands())

	sys.exit(app.exec_())
