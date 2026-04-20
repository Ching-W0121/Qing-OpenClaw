import runpy

if __name__ == '__main__':
    runpy.run_module('engine.memory_search', run_name='__main__')
else:
    from engine.memory_search import *
