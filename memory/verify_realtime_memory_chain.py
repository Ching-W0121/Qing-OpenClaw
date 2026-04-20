import runpy

if __name__ == '__main__':
    runpy.run_module('engine.verify_realtime_memory_chain', run_name='__main__')
else:
    from engine.verify_realtime_memory_chain import *
