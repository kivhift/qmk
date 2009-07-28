import urllib
import webbrowser

import qmk

class GoogleCommand(qmk.Command):
	def __init__(self):
		self._name = 'google'
		self.__baseURL = 'http://www.google.com/search?q=%s'
	
	def action(self, arg):
		if arg is None: return
		text = arg.strip()
		if '' == text: return
		Q = text.split()
		query = self.__baseURL % urllib.quote_plus(
			' '.join(text.split()).encode('utf-8'))
		webbrowser.open(query, new = 2)

class BeolingusCommand(qmk.Command):
	def __init__(self):
		self._name = 'beolingus'
		self.__baseURL = 'http://dict.tu-chemnitz.de/dings.cgi' \
			'?lang=en&service=deen&opterrors=0&optpro=0&query=%s'

	def action(self, arg):
		if arg is None: return
		text = arg.strip().split()[0]
		if '' == text: return
		query = self.__baseURL % urllib.quote_plus(
			text.encode('latin_1'))
		webbrowser.open(query, new = 2)

def commands():
	return [GoogleCommand(), BeolingusCommand()]
