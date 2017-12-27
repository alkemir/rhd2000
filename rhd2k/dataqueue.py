import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

    queue<Rhd2000DataBlock>* new_data_queue(){ return new queue<Rhd2000DataBlock>; }
    void delete_data_queue(queue<Rhd2000DataBlock>* q) {delete q;}


class DataQueue:
    rhd2klib.new_data_queue.restype = ctypes.c_void_p
    rhd2klib.new_ofstream.argtypes = []
    rhd2klib.delete_data_queue.restype = None
    rhd2klib.delete_data_queue.argtypes = [ctypes.c_void_p]

    def __init__(self):
        self._as_parameter_ = rhd2klib.new_data_queue()

    def __del__(self):
        rhd2klib.delete_data_queue(self)
