import runpy

if __name__ == '__main__':
    runpy.run_module('engine.import_reference_memories', run_name='__main__')
else:
    from engine.import_reference_memories import *
