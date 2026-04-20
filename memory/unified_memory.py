import runpy

if __name__ == '__main__':
    runpy.run_module('engine.unified_memory', run_name='__main__')
else:
    from engine.unified_memory import *
