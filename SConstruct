#
# Copyright (c) 2009-2012 Joshua Hughes <kivhift@gmail.com>
#
env = Environment(
    TOOLS=['mingw'],
    CCFLAGS = '-Wextra -Wall -O2'
)
env['strip_all'] = Action('strip --strip-all $TARGET')

env.SConscript('src/SConscript', variant_dir = 'build', duplicate = 0,
    exports = 'env')

# vim:filetype=python
