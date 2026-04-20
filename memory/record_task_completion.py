import runpy

if __name__ == '__main__':
    runpy.run_module('engine.record_task_completion', run_name='__main__')
else:
    from engine.record_task_completion import *
