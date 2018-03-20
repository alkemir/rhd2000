import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')


class VectorInt:
    rhd2klib.new_vector_int.restype = ctypes.c_void_p
    rhd2klib.new_vector_int.argtypes = []
    rhd2klib.vector_int_delete.restype = None
    rhd2klib.vector_int_delete.argtypes = [ctypes.c_void_p]
    rhd2klib.vector_int_size.restype = ctypes.c_int
    rhd2klib.vector_int_size.argtypes = [ctypes.c_void_p]
    rhd2klib.vector_int_get.restype = ctypes.c_int
    rhd2klib.vector_int_get.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.vector_int_push_back.restype = None
    rhd2klib.vector_int_push_back.argtypes = [ctypes.c_void_p, ctypes.c_int]

    def __init__(self):
        self._as_parameter_ = rhd2klib.new_vector_int()

    def __del__(self):
        rhd2klib.vector_int_delete(self)

    def __len__(self):
        return rhd2klib.vector_int_size(self)

    def __getitem__(self, i):
        if 0 <= i < len(self):
            return rhd2klib.vector_int_get(self, ctypes.c_int(i))
        raise IndexError('index out of range')

    def __repr__(self):
        return '[{}]'.format(', '.join(str(self[i]) for i in range(len(self))))

    def push(self, i):
        rhd2klib.vector_int_push_back(self, ctypes.c_int(i))
