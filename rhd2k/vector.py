import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

class Vector(object):
    rhd2klib.new_int_vector.restype = ctypes.c_void_p
    rhd2klib.new_int_vector.argtypes = []
    rhd2klib.delete_int_vector.restype = None
    rhd2klib.delete_int_vector.argtypes = [ctypes.c_void_p]
    rhd2klib.vector_int_size.restype = ctypes.c_int
    rhd2klib.vector_int_size.argtypes = [ctypes.c_void_p]
    rhd2klib.vector_int_get.restype = ctypes.c_int
    rhd2klib.vector_int_get.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.vector_int_push_back.restype = None
    rhd2klib.vector_int_push_back.argtypes = [ctypes.c_void_p, ctypes.c_int]

    def __init__(self):
        self.pointer = rhd2klib.new_vector_int()

    def __del__(self):
        rhd2klib.delete_vector_int(self.vector)

    def __len__(self):
        return rhd2klib.vector_int_size(self.vector)

    def __getitem__(self, i):
        if 0 <= i < len(self):
            return rhd2klib.vector_get(self.vector, ctypes.c_int(i))
        raise IndexError('index out of range')

    def __repr__(self):
        return '[{}]'.format(', '.join(str(self[i]) for i in range(len(self))))

    def push(self, i):
        rhd2klib.vector_push_back(self.vector, ctypes.c_int(i))
