import ctypes
import platform
import os

from rhd2000datablock import Rhd2000DataBlock

libname = '/librhd2k.so'
if platform.system() == 'Windows' or 'CYGWIN' in platform.system():
    libname =  '/librhd2k.dll'
rhd2klib = ctypes.cdll.LoadLibrary(os.path.dirname(__file__) + libname)


class DataQueue:
    rhd2klib.new_queue_data.restype = ctypes.c_void_p
    rhd2klib.new_ofstream.argtypes = []
    rhd2klib.queue_data_delete.restype = None
    rhd2klib.queue_data_delete.argtypes = [ctypes.c_void_p]
    rhd2klib.queue_data_size.restype = ctypes.c_uint
    rhd2klib.queue_data_size.argtypes = [ctypes.c_void_p]
    rhd2klib.queue_data_front.restype = ctypes.c_void_p
    rhd2klib.queue_data_front.argtypes = [ctypes.c_void_p]
    rhd2klib.queue_data_pop.restype = None
    rhd2klib.queue_data_pop.argtypes = [ctypes.c_void_p]

    def __init__(self):
        self._as_parameter_ = rhd2klib.new_queue_data()

    def __del__(self):
        rhd2klib.queue_data_delete(self)

    def __len__(self):
        return int(rhd2klib.queue_data_size(self))

    def front(self):
        return Rhd2000DataBlock(0, ptr=rhd2klib.queue_data_front(self))

    def pop(self):
        rhd2klib.queue_data_pop(self)
