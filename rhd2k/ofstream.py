import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

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
