import ctypes
import platform
import os

libname = '/librhd2k.so'
if platform.system() == 'Windows' or 'CYGWIN' in platform.system():
    libname =  '/librhd2k.dll'
rhd2klib = ctypes.cdll.LoadLibrary(os.path.dirname(__file__) + libname)

class Ofstream:
    rhd2klib.new_ofstream.restype = ctypes.c_void_p
    rhd2klib.new_ofstream.argtypes = []
    rhd2klib.openFile.restype = None
    rhd2klib.openFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    rhd2klib.closeFile.restype = None
    rhd2klib.closeFile.argtypes = [ctypes.c_void_p]

    def __init__(self):
        self._as_parameter_ = rhd2klib.new_ofstream()

    def open(self, filename):
        rhd2klib.openFile(self, filename)

    def close(self):
        rhd2klib.closeFile(self)
