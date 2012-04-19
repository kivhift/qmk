#
# Copyright (c) 2012 Joshua Hughes <kivhift@gmail.com>
#
import os
import subprocess
import tempfile
import threading

import qmk
import pu.utils

class LogCommand(qmk.Command):
    '''Make log entries using restructured text.'''
    def __init__(self):
        super(LogCommand, self).__init__(self)
        self._name = 'log'
        self._help = self.__doc__

        self._ui = pu.utils.get_user_info()
        self._base_dir = os.path.join(qmk.base_dir(), 'logs')
        if not os.path.exists(self._base_dir):
            os.mkdir(self._base_dir, 0755)

    @qmk.capture_and_show_exceptions('log')
    def _make_entry(self, type_):
        _, entry_tmp_file = tempfile.mkstemp(
            prefix = type_, suffix = '.rst', dir = self._base_dir)
        os.close(_)

        start_time = pu.utils.ISO_8601_time_stamp()
        subprocess.call([self._ui.EDITOR, entry_tmp_file])
        end_time = pu.utils.ISO_8601_time_stamp()

        if 0 == os.stat(entry_tmp_file).st_size:
            os.remove(entry_tmp_file)
            return

        entry_dir = os.path.join(self._base_dir, type_)
        if not os.path.exists(entry_dir):
            os.mkdir(entry_dir, 0755)

        st = start_time.split('-')
        YM = '-'.join(st[:2])
        entry_file = os.path.join(entry_dir, '%s-%s.rst' % (type_, YM))
        write_title = (
            not os.path.exists(entry_file)
            or 0 == os.stat(entry_file).st_size)
        with open(entry_file, 'ab') as fout:
            if write_title:
                title = '%s log for %s' % (type_, YM)
                fout.write('\n'.join((title, '=' * len(title), '', '')))

            with open(entry_tmp_file, 'rb') as fin:
                fout.write('\n'.join(
                    (start_time, '-' * len(start_time), '', '')))
                for ln in fin:
                    fout.write(ln.rstrip() + '\n')
                fout.write('\n'.join(
                    ('', '.. Editing finished: ' + end_time, '', '')))
            os.remove(entry_tmp_file)

    def action(self, arg):
        if arg is None:
            subj = 'work'
        else:
            subj = arg.strip()

        # Don't want to block so fire off a thread to do the actual work.
        threading.Thread(target = self._make_entry, args = (subj,)).start()

def commands(): return [ LogCommand() ]
