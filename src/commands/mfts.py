#
# Copyright (c) 2011-2012 Joshua Hughes <kivhift@gmail.com>
#
# This is inspired by the project at https://github.com/holman/boom.

import json
import os
import string

import qmk


class MFTSCommand(qmk.Command):
    '''Squirrel away text snippets or retrieve them.'''

    sub_cmds = 'add echo get ls open rm'.split()

    def __init__(self):
        super(MFTSCommand, self).__init__(self)
        self._name = 'mfts'
        self._help = self.__doc__
        self._stash = {}
        self._stash_file = os.path.join(qmk.base_dir(), 'mfts.json')
        if os.path.exists(self._stash_file):
            try:
                with open(self._stash_file, 'rb') as f:
                    self._stash = json.load(f)
            except Exception, e:
                qmk.ErrorMessage()('mfts: Had trouble loading %s: %s' % (
                    self._stash_file, str(e)))

    def __nodes_and_leaf(self, arg):
        nodes = map(string.strip, arg.split('.'))
        leaf = nodes.pop()

        return nodes, leaf

    def _add(self, arg):
        if not arg:
            raise ValueError('add: Need reference to work with.')

        ref, snip = qmk.left_word_and_rest(arg)
        if not snip:
            snip = qmk.Clipboard.text()
            if not snip:
                raise ValueError('add: Need explicit snippet or clipboard.')

        nodes, leaf = self.__nodes_and_leaf(ref)
        d = self._stash
        sn = []
        for n in nodes:
            sn.append(n)
            if not d.has_key(n):
                d[n] = {}
            elif type(d[n]) is not dict:
                raise ValueError(
                    'add: %s is invalid.  There is a snippet @ %s' % (
                    ref, '.'.join(sn)))

            d = d[n]

        if d.has_key(leaf) and type(d[leaf]) is dict:
            # XXX: Ask if this is what's wanted.
            raise ValueError(
                'add: trying to blow away extant sub-list @ %s' % ref)

        d[leaf] = snip

        with open(self._stash_file, 'wb') as f:
            json.dump(self._stash, f)

    def __ref_only(self, arg, pre = ''):
        ref, _x = qmk.left_word_and_rest(arg)
        if _x:
            raise ValueError('%sJust need reference.' % pre)
        if not ref:
            ref = qmk.Clipboard.text()
            if not ref:
                raise ValueError('%sNeed reference to work with.' % pre)

        return ref

    def __get_sub_dict(self, ref, nodes, pre = ''):
        d = self._stash
        sn = []
        for n in nodes:
            sn.append(n)
            if not d.has_key(n):
                raise ValueError('%s%s is invalid.  No sub-list @ %s' % (
                    pre, ref, '.'.join(sn)))
            elif type(d[n]) is not dict:
                raise ValueError('%s%s is invalid.  Snippet @ %s' % (
                    pre, ref, '.'.join(sn)))
            d = d[n]

        return d

    def __get_leaf(self, ref, pre = ''):
        nodes, leaf = self.__nodes_and_leaf(ref)

        d = self.__get_sub_dict(ref, nodes, pre)

        if not d.has_key(leaf) or type(d[leaf]) is dict:
            raise ValueError('%sNo snippet @ %s' % (pre, ref))

        return d[leaf]

    def _echo(self, arg):
        p = 'echo: '
        qmk.Message()(self.__get_leaf(self.__ref_only(arg, p), p))

    def _get(self, arg):
        p = 'get: '
        qmk.Clipboard.setText(self.__get_leaf(self.__ref_only(arg, p), p))

    def _ls(self, arg):
        p = 'ls: '
        if not arg:
            ls = []
            pad = ''
            d = self._stash
        else:
            ref = self.__ref_only(arg, p)
            ls = [ref + '.']
            pad = '  '
            nodes, leaf = self.__nodes_and_leaf(ref)
            d = self.__get_sub_dict(ref, nodes, p)
            if d.has_key(leaf) and type(d[leaf]) is dict:
                d = d[leaf]
            else:
                raise ValueError('%s%s is not a sub-list.' % (p, ref))

        keys = d.keys()
        keys.sort()

        for k in keys:
            if type(d[k]) is dict:
                ls.append('%s%s. (%d)' % (pad, k, len(d[k])))
            else:
                ls.append('%s%s %s' % (pad, k, d[k]))

        qmk.Message()('\n'.join(ls))

    def _open(self, arg):
        p = 'open: '
        os.startfile(self.__get_leaf(self.__ref_only(arg, p), p))

    def _rm(self, arg):
        p = 'rm: '
        ref = self.__ref_only(arg, p)
        nodes, leaf = self.__nodes_and_leaf(ref)
        d = self.__get_sub_dict(ref, nodes, p)

        if not d.has_key(leaf) or type(d[leaf]) is dict:
            raise ValueError('%sNo snippet @ %s' % (p, ref))

        del d[leaf]
        while not d and d != self._stash:
            ref, _x = ref.rsplit('.', 1)
            nodes, leaf = self.__nodes_and_leaf(ref)
            d = self.__get_sub_dict(ref, nodes, p)
            del d[leaf]

        with open(self._stash_file, 'wb') as f:
            json.dump(self._stash, f)

    def action(self, arg):
        if arg is None:
            return

        act, subarg = qmk.left_word_and_rest(arg)
        if act in MFTSCommand.sub_cmds:
            getattr(self, '_%s' % act)(subarg)
            return

        self._get(arg)

def commands(): return [ MFTSCommand() ]
