#
# Copyright (c) 2012 Joshua Hughes <kivhift@gmail.com>
#
import os
import shlex
import subprocess
import sys
import tempfile
import threading
import webbrowser

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

        op = qmk.CommandOptionParser(name = self._name)
        op.add_option('-v', '--view', dest = 'view', default = False,
            action = 'store_true', help = 'view current log in webbrowser')
        self._optpar = op

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

    @qmk.capture_and_show_exceptions('log')
    def _show_log(self, type_):
        import docutils.core

        entry_file = os.path.join(self._base_dir, type_,
            '%s-%s.rst' % (type_, pu.utils.ym_str('-')))
        html_file = entry_file + '.html'
        style_file = os.path.join(self._base_dir, 'log-style.css')

        if not os.path.exists(entry_file):
            raise ValueError('%s log does not exist' % type_)

        pub = docutils.core.Publisher()
        pub.set_components(reader_name = 'standalone',
            parser_name = 'restructuredtext', writer_name = 'html')
        # Use .get_settings() so as to not have the command-line arguments
        # processed when calling .publish().  It has to be called after
        # .set_components() but before .set_source() and .set_destination() or
        # else bad things happen.
        pub.get_settings()
        pub.set_source(source_path = entry_file)
        pub.set_destination(destination_path = html_file)
        if os.path.exists(style_file):
            pub.settings.stylesheet_path = style_file
        pub.publish()
        webbrowser.open_new_tab('file:///' + html_file.replace('\\', '/'))

    def action(self, arg):
        opts, args = self._optpar.parse_args(
            args = [] if arg is None else shlex.split(
                (arg if sys.hexversion >= 0x02070300 else str(arg))))
        if 0 == len(args):
            subj = 'work'
        else:
            subj = args[0]

        # Don't want to block so fire off a thread to do the actual work.
        threading.Thread(
            target = self._show_log if opts.view else self._make_entry,
            args = (subj,)).start()

def commands(): return [ LogCommand() ]
