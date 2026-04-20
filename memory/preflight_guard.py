import runpy

if __name__ == '__main__':
    runpy.run_module('monitor.preflight_guard', run_name='__main__')
else:
    from monitor.preflight_guard import *
