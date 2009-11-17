#!/usr/bin/python

import os
import sys
import glob

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtSvg

import qmk

class QuitCommand(qmk.Command):
	'''Use this command to quit.'''
	def __init__(self):
		self._name = 'quit'
		self._help = self.__doc__

	def action(self, arg):
		# XXX Perhaps add some fancier shutdown stuff here.
		QtGui.qApp.quit()

app = QtGui.QApplication([])
app.setQuitOnLastWindowClosed(False)
app.setWindowIcon(QtGui.QIcon(':images/qmk-icon.svg'))
app.setStyleSheet('''\
QLineEdit {
	background-color: #4b4b4b;
	color: #ffffff;
	border-width: 2px;
	border-style: solid;
	border-color: #ffffff;
	border-radius: 5px;
	font-size: 20px;
	font-family: "Dejavu Sans Mono";
	padding: 3px;
	margin: 0px;
}
/* Give some visual feedback if we've got keyboard focus. */
QLineEdit:focus {
	background-color: #004b00;
	color: #00ff00;
	border-color: #00ff00;
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

filt = qmk.InputFilter.get()
ci = qmk.CommandInput.get()
cm = qmk.CommandManager.get()

filt.setCallback(qmk.Engine.callback)

cm.registerCommands([QuitCommand()])

cm.registerCommands(__import__('commands').commands())

m = qmk.Message('QMK Message', 'QMK has started...', 5000)
m.show()

sys.exit(app.exec_())
