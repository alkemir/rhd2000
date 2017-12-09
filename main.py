import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

rhd2klib._new.restype = ctypes.c_void_p
rhd2klib.open.argtypes = [ctypes.c_void_p]

class EvalBoard:
	def __init__(self):
		self.pointer = rhd2klib._new()

	def open(self):
		return rhd2klib.open(self.pointer)


b = EvalBoard()
b.open()
