import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

class DataQueue:
    rhd2klib.new_data_queue.restype = ctypes.c_void_p
    rhd2klib.new_ofstream.argtypes = []
    rhd2klib.delete_data_queue.restype = None
    rhd2klib.delete_data_queue.argtypes = [ctypes.c_void_p]
    rhd2klib.data_queue_size.restype = ctypes.c_uint
    rhd2klib.data_queue_size.argtypes = [ctypes.c_void_p]

    def __init__(self):
        self._as_parameter_ = rhd2klib.new_data_queue()

    def __del__(self):
        rhd2klib.delete_data_queue(self)

    def __len__(self):
        return int(rhd2klib.data_queue_size(self))
