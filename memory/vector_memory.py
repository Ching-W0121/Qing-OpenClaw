import runpy

if __name__ == '__main__':
    runpy.run_module('engine.vector_memory', run_name='__main__')
else:
    from engine.vector_memory import *
