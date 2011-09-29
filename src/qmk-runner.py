#!/usr/bin/python

import os
import sys
import imp
import optparse
import glob

from PyQt4 import QtCore, QtGui

import qmk
import utils

class QuitCommand(qmk.Command):
    '''Use this command to quit.'''
    def __init__(self):
        self._name = 'quit'
        self._help = self.__doc__

    def action(self, arg):
        qmk.CommandManager().shutdownCommands()
        QtGui.qApp.quit()

modloadtuple = ('.py', 'rb', imp.PY_SOURCE)
def load_qmkconfig(filename):
    with open(filename, 'rb') as f:
        cfg = imp.load_module('qmk-config', f, filename, modloadtuple)

    return cfg

def register_commands(cmds):
    for t in cmds:
        basedir = t[0]
        if not basedir:
            basedir = os.path.join(
                utils.get_user_info()['HOME'], '.qmk', 'commands')

        if not t[1]:
            files = glob.glob(os.path.join(basedir, '*.py'))
        else:
            files = [ os.path.join(basedir, x) for x in t[1] ]

        for fn in files:
            with open(fn, 'rb') as f:
                qmk.CommandManager().registerCommands(imp.load_module(
                    os.path.splitext(os.path.basename(fn))[0], f, fn,
                    modloadtuple).commands())

optpar = optparse.OptionParser()
optpar.add_option('-f', '--filename', dest = 'filename', default = None,
    help = 'name of config file to use instead of ~/.qmk/qmk-config.py')

app = QtGui.QApplication(sys.argv)
opts, args = optpar.parse_args()

qmkconfig = load_qmkconfig(opts.filename if opts.filename is not None
    else os.path.join(utils.get_user_info()['HOME'], '.qmk', 'qmk-config.py'))
register_commands(qmkconfig.commands)

app.setQuitOnLastWindowClosed(False)
app.setWindowIcon(QtGui.QIcon(':images/qmk-icon.png'))
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
