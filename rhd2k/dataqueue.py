import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

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
        return rhd2klib.queue_data_front(self)

    def pop(self):
        rhd2klib.queue_data_pop(self)
