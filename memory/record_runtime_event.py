import runpy

if __name__ == '__main__':
    runpy.run_module('engine.record_runtime_event', run_name='__main__')
else:
    from engine.record_runtime_event import *
