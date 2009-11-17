import atexit
import os
import tempfile
import urllib
import webbrowser
import datetime
import calendar
import subprocess

import qmk

class RunCommand(qmk.Command):
	'''Use this command to run arbitrary processes.'''
	def __init__(self):
		self._name = '$'
		self._help = self.__doc__

	def action(self, arg):
		pid = subprocess.Popen(arg).pid

class CalendarCommand(qmk.Command):
	'''Use this command to display a calendar for the current month.'''
	def __init__(self):
		self._name = 'cal'
		self._help = self.__doc__
		self.__m = None

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
		cm = cal.formatmonth(year, month)
		self.__m = qmk.Message('Calendar', cm)
		self.__m.show()

class DateCommand(qmk.Command):
	'''Use this command to quickly view the current date.'''
	def __init__(self):
		self._name = 'date'
		self._help = self.__doc__

	def action(self, arg):
		now = str(datetime.datetime.now())
		self.__m = qmk.Message('Date', str(now), 10000)
		self.__m.show()

class GoogleCommand(qmk.Command):
	'''Use this command to google the given arguments.  A new tab will
	be opened in the default web browser with the Google search results.'''
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

class BeolingusCommand(qmk.Command):
	'''Use this command to look up a German word using Beolingus.  A
	new tab will be opened in the default web browser with the search
	results.'''
	def __init__(self):
		self._name = 'beolingus'
		self._help = self.__doc__
		self.__baseURL = 'http://dict.tu-chemnitz.de/dings.cgi' \
			'?lang=en&service=deen&opterrors=0&optpro=0&query=%s'

	def action(self, arg):
		if arg is None: return
		text = arg.strip().split()[0]
		if '' == text: return
		query = self.__baseURL % urllib.quote_plus(
			text.encode('latin_1'))
		webbrowser.open_new_tab(query)

class BrowseCommand(qmk.Command):
	'''Use this command to open the supplied URL in the default web
	browser.'''
	def __init__(self):
		self._name = 'browse'
		self._help = self.__doc__

	def action(self, arg):
		if arg is None: return
		webbrowser.open_new_tab(arg)

class HelpCommand(qmk.Command):
	'''Use this command to view help for all available commands.  A new
	tab will be opened in the default web browser that contains the
	help for all of the commands that are registered.'''
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
		cm = qmk.CommandManager.get()
		for name in cm.commandNames():
			cmd = cm.command(name)
			ht = cmd.help
			f.write('<b>%s</b><p>%s</p>' % (name, ht.encode(
				'ascii', 'xmlcharrefreplace')))
		f.write('</body></html>\n')
		f.close()
		webbrowser.open_new_tab('file:%s' % urllib.pathname2url(
			f.name))

class OctopartCommand(qmk.Command):
	'''Use this command to look up a part on Octopart.  A new tab will
	be opened in the default web browser that contains the search
	results.'''
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
	return cmds
