import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')


class Rhd2000DataBlock:
    rhd2klib.newBlock.restype = ctypes.c_void_p
    rhd2klib.newBlock.argtypes = [ctypes.c_int]
    rhd2klib.calculateDataBlockSizeInWords.restype = ctypes.c_uint
    rhd2klib.calculateDataBlockSizeInWords.argtypes = [ctypes.c_int]
    rhd2klib.getSamplesPerDataBlock.restype = ctypes.c_uint
    rhd2klib.getSamplesPerDataBlock.argtypes = []
    rhd2klib.fillFromUsbBuffer.restype = None
    rhd2klib.fillFromUsbBuffer.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    rhd2klib.printData.restype = None
    rhd2klib.printData.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.write.restype = None
    rhd2klib.write.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    rhd2klib.checkUsbHeader.restype = ctypes.c_bool
    rhd2klib.checkUsbHeader.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    rhd2klib.readAmplifier.restype = ctypes.POINTER(ctypes.c_int)
    rhd2klib.readAmplifier.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    rhd2klib.readAuxiliary.restype = ctypes.POINTER(ctypes.c_int)
    rhd2klib.readAuxiliary.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    rhd2klib.readADC.restype = ctypes.POINTER(ctypes.c_int)
    rhd2klib.readADC.argtypes = [ctypes.c_void_p, ctypes.c_int]

    def __init__(self, numDataStreams, ptr=None):
        if ptr is None:
            self._as_parameter_ = rhd2klib.newBlock(numDataStreams)
            return
        self._as_parameter_ = ptr

    @staticmethod
    def calculateDataBlockSizeInWords(numDataStreams):
        return rhd2klib.calculateDataBlockSizeInWords(numDataStreams)

    @staticmethod
    def getSamplesPerDataBlock():
        return rhd2klib.getSamplesPerDataBlock()

    def fillFromUsbBuffer(self, usbBuffer, blockIndex, numDataStreams):
        rhd2klib.fillFromUsbBuffer(self, usbBuffer, blockIndex, numDataStreams)

    def printData(self, stream):
        rhd2klib.printData(self, stream)

    def write(self, saveOut, numDataStreams):
        rhd2klib.write(self, saveOut, numDataStreams)

    def checkUsbHeader(self, usbBuffer, index):
        return rhd2klib.checkUsbHeader(self, usbBuffer, index)

    def readAmplifier(self, stream, channel):
        return rhd2klib.readAmplifier(self, stream, channel)

    def readAuxiliary(self, stream, channel):
        return rhd2klib.readAuxiliary(self, stream, channel)

    def readADC(self, adc):
        return rhd2klib.readADC(self, adc)
