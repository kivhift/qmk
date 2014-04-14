#
# Copyright (c) 2014 Joshua Hughes <kivhift@gmail.com>
#
import requests

import qmk

class LengthenURLCommand(qmk.Command):
    '''Lengthen the given shortened URL, then display the result and copy it to
    the clipboard.'''
    def __init__(self):
        self._name = 'lengthen-url'
        self._help = self.__doc__

    @qmk.Command.actionRequiresArgument
    def action(self, arg):
        # The assumption here is that URL shorteners just have one level of
        # redirection to point the short URL to the long version.
        r = requests.get(arg, allow_redirects = False)
        if requests.codes.MOVED != r.status_code:
            raise RuntimeError('Request does not redirect: {}'.format(arg))
        url = r.headers['location']
        qmk.Clipboard.setText(url)
        qmk.Message()(url)

def commands(): return [ LengthenURLCommand() ]
