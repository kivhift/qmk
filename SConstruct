env = Environment(TOOLS=['mingw'])
env.Append(CCFLAGS = '-O2 -Wall')
env['strip_all'] = Action('strip --strip-all $TARGET')

qmk = env.SharedLibrary(source = ['qmk-hook.c'], no_import_lib = 1)
env.AddPostAction(qmk, env['strip_all'])
#vim:filetype=python
