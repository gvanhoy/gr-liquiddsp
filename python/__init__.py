# import swig generated symbols into the test namespace
try:
    # this might fail if the module is python-only
    from liquiddsp_swig import *
except ImportError:
    pass

# import any pure python herefrom cognitive_engine import cognitive_engine