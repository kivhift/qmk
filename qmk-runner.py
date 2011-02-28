#!/usr/bin/python

import os
import sys
import imp
import optparse

from PyQt4 import QtCore, QtGui, QtXml, QtSvg

import qmk
import utils

class QuitCommand(qmk.Command):
    '''Use this command to quit.'''
    def __init__(self):
        self._name = 'quit'
        self._help = self.__doc__

    def action(self, arg):
        # XXX Perhaps add some fancier shutdown stuff here.
        QtGui.qApp.quit()

modloadtuple = ('.py', 'rb', imp.PY_SOURCE)
def load_qmkconfig(filename):
    with open(filename, 'rb') as f:
        cfg = imp.load_module('qmkconfig', f, filename, modloadtuple)

    return cfg

def register_commands(cmds):
    for t in cmds:
        basedir = t[0]
        if not basedir:
            basedir = os.path.join(
                utils.get_user_info()['HOME'], '.qmk', 'commands')
        for fn in t[1]:
            filename = os.path.join(basedir, fn)
            modname = os.path.splitext(os.path.basename(fn))[0]
            with open(filename, 'rb') as f:
                c = imp.load_module(modname, f, filename, modloadtuple)
            qmk.CommandManager().registerCommands(c.commands())

optpar = optparse.OptionParser()
optpar.add_option('-f', '--filename', dest = 'filename', default = None,
    help = 'name of config file to use instead of ~/.qmk/qmkconfig.py')

app = QtGui.QApplication(sys.argv)
opts, args = optpar.parse_args()

qmkconfig = load_qmkconfig(opts.filename if opts.filename is not None
    else os.path.join(utils.get_user_info()['HOME'], '.qmk', 'qmkconfig.py'))
register_commands(qmkconfig.commands)

app.setQuitOnLastWindowClosed(False)
app.setWindowIcon(QtGui.QIcon(':images/qmk-icon.svg'))
# {{{
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
# }}}

qmk.CommandManager().registerCommands([QuitCommand()])
qmk.CommandInput().updateCompletions()

qmk.InputFilter().setQMKKeyboardCallback(qmk.Engine.QMKCallback)
qmk.InputFilter().enableQMKKeyboardCallback()
qmk.InputFilter().setKeyboardCallback(qmk.Engine.hideMessageCallback)
qmk.InputFilter().setMouseCallback(qmk.Engine.hideMessageCallback)
qmk.InputFilter().setKeyboardWindowId(int(qmk.CommandInput().winId()))

qmk.Message()('QMK has started...')

sys.exit(app.exec_())
