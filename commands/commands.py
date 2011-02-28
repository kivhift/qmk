import atexit
import os
import tempfile
import urllib
import webbrowser
import datetime
import calendar
import subprocess
import ctypes

# For eval command
from math import *

import qmk

class ClipboardCommand(qmk.Command):
    '''Show the contents of the clipboard or set it to the given argument.'''
    def __init__(self):
        self._name = 'clipboard'
        self._help = self.__doc__

    def action(self, arg):
        if arg is None:
            qmk.Message()(qmk.Clipboard.text())
        else:
            qmk.Clipboard.setText(arg)

class EvalCommand(qmk.Command):
    '''Pass arguments to Python's eval() builtin.'''
    def __init__(self):
        self._name = 'eval'
        self._help = self.__doc__

    def action(self, arg):
        if arg is None:
            arg = str(qmk.Clipboard.text())
            if '' == arg: return
        try:
            result = str(eval(arg))
        except Exception, e:
            qmk.ErrorMessage()('Had trouble eval()ing "%s": %s' % (
                arg, str(e)))
            return

        qmk.Clipboard.setText(result)
        qmk.Message()(arg + ' --> ' + result)

class RunCommand(qmk.Command):
    '''Run arbitrary processes.'''
    def __init__(self):
        self._name = '!'
        self._help = self.__doc__

    def action(self, arg):
        pid = subprocess.Popen(arg).pid

class CalendarCommand(qmk.Command):
    '''Display a calendar for a given month.  With no arguments, the
    current year and month are used.  If one argument is given, it is
    used as the month with the current year unless the month is invalid
    in which case the current month is used with the argument as the
    year.  If two arguments are given, they are assumed to be the year
    and month, respectively, unless the month is invalid in which case
    the arguments are used as month and year, respectively.'''
    def __init__(self):
        self._name = 'cal'
        self._help = self.__doc__

    def action(self, arg):
        now = datetime.datetime.now()
        year, month = now.year, now.month

        if arg is not None:
            args = arg.split()
            if len(args) == 2:
                try:
                    y, m = int(args[0]), int(args[1])
                    if m < 1 or m > 12:
                        y, m = m, y
                    year, month = y, m
                except:
                    pass
            elif len(args) == 1:
                try:
                    y = now.year
                    m = int(args[0])
                    if m < 1 or m > 12:
                        y = m
                        m = now.month
                    year, month = y, m
                except:
                    pass

        cal = calendar.TextCalendar(firstweekday=calendar.MONDAY)
        mark = ' '
        if year == now.year and month == now.month:
            mark = ':'
        cm = '%s\n%s\n' % (cal.formatmonthname(year, month, 20, True),
            cal.formatweekheader(2))
        i = 0
        for d in cal.itermonthdays(year, month):
            if 0 == d:
                f = '  '
            else:
                f = '%2d' % d
            if 6 == i % 7:
                f += '\n'
            elif (now.day - 1) == d or now.day == d:
                f += mark
            else:
                f += ' '
            cm += f
            i += 1

        qmk.Message()(cm)

class DateCommand(qmk.Command):
    '''View the current date.'''
    def __init__(self):
        self._name = 'date'
        self._help = self.__doc__

    def action(self, arg):
        now = str(datetime.datetime.now())
        qmk.Message()(now)

class GoogleCommand(qmk.Command):
    '''Google the given arguments.  A new tab will be opened in the
    default web browser with the Google search results.'''
    def __init__(self):
        self._name = 'google'
        self._help = self.__doc__
        self.__baseURL = 'http://www.google.com/search?q=%s'

    def action(self, arg):
        if arg is None: return
        text = arg.strip()
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(
            ' '.join(text.split()).encode('utf-8'))
        webbrowser.open_new_tab(query)

class AmazonCommand(qmk.Command):
    '''Search www.amazon.com using the given arguments.  A new tab will be
    opened in the default web browser with the search results.'''
    def __init__(self):
        self._name = 'amazon'
        self._help = self.__doc__
        self.__baseURL = 'http://www.amazon.com/' \
            's?ie=UTF8&index=blended&field-keywords=%s'

    def action(self, arg):
        if arg is None: return
        text = arg.strip()
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(
            ' '.join(text.split()).encode('utf-8'))
        webbrowser.open_new_tab(query)

class BeolingusCommand(qmk.Command):
    '''Look up a German word using Beolingus.  A new tab will be opened
    in the default web browser with the search results.'''
    def __init__(self):
        self._name = 'beolingus'
        self._help = self.__doc__
        self.__baseURL = 'http://dict.tu-chemnitz.de/?query=%s' \
            '&service=deen&mini=1'

    def action(self, arg):
        if arg is None: return
        text = arg.strip().split()[0]
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(
            text.encode('latin_1'))
        webbrowser.open_new_tab(query)

class BrowseCommand(qmk.Command):
    '''Open the supplied URL in the default web browser.'''
    def __init__(self):
        self._name = 'browse'
        self._help = self.__doc__

    def action(self, arg):
        if arg is None: return
        webbrowser.open_new_tab(arg)

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

class OctopartCommand(qmk.Command):
    '''Look up a part on Octopart.  A new tab will be opened in the
    default web browser that contains the search results.'''
    def __init__(self):
        self._name = 'octopart'
        self._help = self.__doc__
        self.__baseURL = 'http://octopart.com/parts/search?q=%s&js=on'

    def action(self, arg):
        if arg is None: return
        text = arg.strip()
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(
            ' '.join(text.split()).encode('utf-8'))
        webbrowser.open_new_tab(query)

class WundergroundCommand(qmk.Command):
    '''Look up the current weather conditions for a given ZIP code (or
    airport code) using Weather Underground.  A new tab will be opened
    in the default web browser that contains the search results.'''
    def __init__(self):
        self._name = 'wunderground'
        self._help = self.__doc__
        self.__baseURL = 'http://www.wunderground.com/cgi-bin' \
        '/findweather/getForecast?query=%s&wuSelect=WEATHER'

    def action(self, arg):
        if arg is None: return
        text = arg.strip()
        if '' == text: return
        query = self.__baseURL % urllib.quote_plus(text.encode('utf-8'))
        webbrowser.open_new_tab(query)

class ConvertCommand(qmk.Command):
    '''Convert values with given units to other units.'''
    def __init__(self):
        from conversion.pressure import Pressure
        from conversion.temperature import Temperature
        from conversion.volume import Volume

        self._name = 'convert'
        self._help = self.__doc__

        self.__P = Pressure()
        self.__T = Temperature()
        self.__V = Volume()

    def action(self, arg):
        if arg is None: return
        arg = arg.split()
        if len(arg) != 3: return
        try:
            val = float(arg[0])
        except:
            return
        fu, tu = arg[1], arg[2]
        if fu in self.__P.available_units():
            co = self.__P
        elif fu in self.__T.available_units():
            co = self.__T
        elif fu in self.__V.available_units():
            co = self.__V
        else:
            return

        if not tu in co.available_units():
            return

        setattr(co, fu, val)

        qmk.Message()('%s %s --> %f %s' % (
            arg[0], fu, getattr(co, tu), tu))

class ComputerCommand(qmk.Command):
    '''Hibernate, suspend, shutdown or reboot the computer or log off.'''
    # These are from winuser.h.
    EWX_LOGOFF = 0
    EWX_POWEROFF = 8
    EWX_REBOOT = 2
    EWX_FORCEIFHUNG = 16
    def __init__(self):
        self._name = 'computer'
        self._help = self.__doc__

    def hibernate(self):
        ctypes.windll.powrprof.SetSuspendState(1, 0, 0)

    def suspend(self):
        ctypes.windll.powrprof.SetSuspendState(0, 0, 0)

    def shutdown(self):
        ctypes.windll.user32.ExitWindowsEx(ComputerCommand.EWX_POWEROFF, 0)

    def reboot(self):
        ctypes.windll.user32.ExitWindowsEx(ComputerCommand.EWX_REBOOT, 0)

    def logoff(self):
        ctypes.windll.user32.ExitWindowsEx(ComputerCommand.EWX_LOGOFF, 0)

    def action(self, arg):
        if arg is None: return

        for a in 'hibernate suspend shutdown reboot logoff'.split():
            if a.startswith(arg): return getattr(self, a)()

        qmk.ErrorMessage()('Invalid request: %s' % arg)

def commands():
    cmds = []
    cmds.append(GoogleCommand())
    cmds.append(BeolingusCommand())
    cmds.append(BrowseCommand())
    cmds.append(HelpCommand())
    cmds.append(CalendarCommand())
    cmds.append(DateCommand())
    cmds.append(RunCommand())
    cmds.append(OctopartCommand())
    cmds.append(WundergroundCommand())
    cmds.append(EvalCommand())
    cmds.append(ConvertCommand())
    cmds.append(ClipboardCommand())
    cmds.append(AmazonCommand())
    cmds.append(ComputerCommand())
    return cmds