import atexit
import os
import tempfile
import urllib
import webbrowser

import qmk

class HelpCommand(qmk.Command):
    '''View help for all available commands.  A new tab will be opened
    in the default web browser that contains the help for all of the
    commands that are registered.'''
    def __init__(self):
        self._name = 'help'
        self._help = self.__doc__
        h, self.__filename = tempfile.mkstemp(suffix = '.html',
            prefix = 'qmkhelp')
        os.close(h)
        atexit.register(os.remove, self.__filename)

    def action(self, arg):
        # For now, ignore help requests for specific commands.
        # if arg is not None: pass
        f = file(self.__filename, 'wb')
        f.write('<html><head><title>QMK Help</title></head><body>')
        f.write('<h1>QMK Command Help</h1>')
        cm = qmk.CommandManager()
        f.write('<table border="1"><tr><th>Name</th><th>Help</th></tr>')
        for name in cm.commandNames():
            cmd = cm.command(name)
            ht = cmd.help
            f.write('<tr><td>%s</td><td>%s</td></tr>' % (name,
                ht.encode('ascii', 'xmlcharrefreplace')))
        f.write('</table></body></html>\n')
        f.close()
        webbrowser.open_new_tab('file:%s' % urllib.pathname2url(
            f.name))

def commands(): return [ HelpCommand() ]
