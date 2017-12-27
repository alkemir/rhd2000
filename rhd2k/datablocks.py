import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

class DataBlock:
    rhd2klib.newBlock.restype = ctypes.c_void_p
    rhd2klib.newBlock.argtypes = [ctypes.c_int]
    rhd2klib.calculateDataBlockSizeInWords.restype = ctypes._uint
    rhd2klib.calculateDataBlockSizeInWords.argtypes = [ctypes.int]
    rhd2klib.getSamplesPerDataBlock.restype = ctypes._uint
    rhd2klib.getSamplesPerDataBlock.argtypes = []
    rhd2klib.fillFromUsbBuffer.restype = None
    rhd2klib.fillFromUsbBuffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    rhd2klib.print.restype = None
    rhd2klib.print.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.write.restype = None
    rhd2klib.write.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    rhd2klib.checkUsbHeader.restype = ctypes.c_bool
    rhd2klib.checkUsbHeader.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]

    def __init__(self, numDataStreams):
        self.pointer = rhd2klib.newBlock(numDataStreams)

    @staticmethod
    def calculateDataBlockSizeInWords():
        return rhd2klib.calculateDataBlockSizeInWords()

    @staticmethod
    def getSamplesPerDataBlock():
        return rhd2klib.getSamplesPerDataBlock()

    def fillFromUsbBuffer(self, usbBuffer, blockIndex, numDataStreams):
        rhd2klib.fillFromUsbBuffer(self.pointer, usbBuffer, blockIndex, numDataStreams)

    def print(self, stream):
        rhd2klib.print(self.pointer, stream)

    def write(self, saveOut, numDataStreams):
        rhd2klib.write(self.pointer, saveOut, numDataStreams)

    def checkUsbHeader(self, usbBuffer, index):
        return rhd2klib.checkUsbHeader(self.pointer, usbBuffer, index)
