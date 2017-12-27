import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

class Registers:
    rhd2klib.newRegisters.restype = ctypes.c_void_p
    rhd2klib.newRegisters.argtypes = [ctypes.c_double]
    rhd2klib.defineSampleRate.restype = None
    rhd2klib.defineSampleRate.argtypes = [ctypes.c_void_p, ctypes.c_double]
    rhd2klib.setFastSettle.restype = None
    rhd2klib.setFastSettle.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    rhd2klib.setDigOutLow.restype = None
    rhd2klib.setDigOutLow.argtypes = [ctypes.c_void_p]
    rhd2klib.setDigOutHigh.restype = None
    rhd2klib.setDigOutHigh.argtypes = [ctypes.c_void_p]
    rhd2klib.setDigOutHiZ.restype = None
    rhd2klib.setDigOutHiZ.argtypes = [ctypes.c_void_p]
    rhd2klib.enableAux1.restype = None
    rhd2klib.enableAux1.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    rhd2klib.enableAux2.restype = None
    rhd2klib.enableAux2.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    rhd2klib.enableAux3.restype = None
    rhd2klib.enableAux3.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    rhd2klib.enableDsp.restype = None
    rhd2klib.enableDsp.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    #rhd2klib.disableDsp.restype = None
    #rhd2klib.disableDsp.argtypes = [ctypes.c_void_p]
    rhd2klib.setDspCutoffFreq.restype = ctypes.c_double
    rhd2klib.setDspCutoffFreq.argtypes = [ctypes.c_void_p, ctypes.c_double]
    rhd2klib.getDspCutoffFreq.restype = ctypes.c_double
    rhd2klib.getDspCutoffFreq.argtypes = [ctypes.c_void_p]
    rhd2klib.enableZcheck.restype = None
    rhd2klib.enableZcheck.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    rhd2klib.setZcheckDacPower.restype = None
    rhd2klib.setZcheckDacPower.argtypes = [ctypes.c_void_p, ctypes.c_bool]
    rhd2klib.setZcheckScale.restype = None
    rhd2klib.setZcheckScale.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.setZcheckPolarity.restype = None
    rhd2klib.setZcheckPolarity.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.setZcheckChannel.restype = ctypes.c_int
    rhd2klib.setZcheckChannel.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.setAmpPowered.restype = None
    rhd2klib.setAmpPowered.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_bool]
    rhd2klib.powerUpAllAmps.restype = None
    rhd2klib.powerUpAllAmps.argtypes = [ctypes.c_void_p]
    rhd2klib.powerDownAllAmps.restype = None
    rhd2klib.powerDownAllAmps.argtypes = [ctypes.c_void_p]
    rhd2klib.getRegisterValue.restype = ctypes.c_int
    rhd2klib.getRegisterValue.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.setUpperBandwidth.restype = ctypes.c_double
    rhd2klib.setUpperBandwidth.argtypes = [ctypes.c_void_p, ctypes.c_double]
    rhd2klib.setLowerBandwidth.restype = ctypes.c_double
    rhd2klib.setLowerBandwidth.argtypes = [ctypes.c_void_p, ctypes.c_double]
    rhd2klib.createCommandListRegisterConfig.restype = ctypes.c_int
    rhd2klib.createCommandListRegisterConfig.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
    rhd2klib.createCommandListTempSensor.restype = ctypes.c_int
    rhd2klib.createCommandListTempSensor.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    rhd2klib.createCommandListUpdateDigOut.restype = ctypes.c_int
    rhd2klib.createCommandListUpdateDigOut.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    rhd2klib.createCommandListZcheckDac.restype = ctypes.c_int
    rhd2klib.createCommandListZcheckDac.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double, ctypes.c_double]
    rhd2klib.createRhd2000Command0.restype = ctypes.c_int
    rhd2klib.createRhd2000Command0.argtypes = [ctypes.c_void_p, ctypes.c_int]
    rhd2klib.createRhd2000Command1.restype = ctypes.c_int
    rhd2klib.createRhd2000Command1.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    rhd2klib.createRhd2000Command2.restype = ctypes.c_int
    rhd2klib.createRhd2000Command2.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]

    def __init__(self, sampleRate):
        self.pointer = rhd2klib.newRegisters(sampleRate)

    def defineSampleRate(self, newSampleRate):
        rhd2klib.defineSampleRate(self.pointer, newSampleRate)

    def setFastSettle(self, enabled):
        rhd2klib.setFastSettle(self.pointer, enabled)

    def setDigOutLow(self):
        rhd2klib.setDigOutLow(self.pointer)

    def setDigOutHigh(self):
        rhd2klib.setDigOutHigh(self.pointer)

    def setDigOutHiZ(self):
        rhd2klib.setDigOutHiZ(self.pointer)

    def enableAux1(self, enabled):
        rhd2klib.enableAux1(self.pointer, enabled)

    def enableAux2(self, enabled):
        rhd2klib.enableAux2(self.pointer, enabled)

    def enableAux3(self, enabled):
        rhd2klib.enableAux3(self.pointer, enabled)

    def enableDsp(self, enabled):
        rhd2klib.enableDsp(self.pointer, enabled)

    #def disableDsp(self):
    #    rhd2klib.disableDsp(self.pointer)

    def setDspCutoffFreq(self, newDspCutoffFreq):
        return rhd2klib.setDspCutoffFreq(self.pointer, newDspCutoffFreq)

    def getDspCutoffFreq(self):
        return rhd2klib.getDspCutoffFreq(self.pointer)

    def enableZcheck(self, enabled):
        rhd2klib.enableZcheck(self.pointer, enabled)

    def setZcheckDacPower(self, enabled):
        rhd2klib.setZcheckDacPower(self.pointer, enabled)

    def setZcheckScale(self, scale):
        rhd2klib.setZcheckScale(self.pointer, scale)

    def setZcheckPolarity(self, polarity):
        rhd2klib.setZcheckPolarity(self.pointer, polarity)

    def setZcheckChannel(self, channel):
        return rhd2klib.setZcheckChannel(self.pointer, channel)

    def setAmpPowered(self, channel, powered):
        rhd2klib.setAmpPowered(self.pointer, channel, powered)

    def powerUpAllAmps(self):
        rhd2klib.powerUpAllAmps(self.pointer)

    def powerDownAllAmps(self):
        rhd2klib.powerDownAllAmps(self.pointer)

    def getRegisterValue(self, reg):
        return rhd2klib.getRegisterValue(self.pointer, reg)

    def setUpperBandwidth(self, upperBandwidth):
        return rhd2klib.setUpperBandwidth(self.pointer, upperBandwidth)

    def setLowerBandwidth(self, lowerBandwidth):
        return rhd2klib.setLowerBandwidth(self.pointer, lowerBandwidth)

    def createCommandListRegisterConfig(self, commandList, calibrate):
        return rhd2klib.createCommandListRegisterConfig(self.pointer, commandList.pointer, calibrate)

    def createCommandListTempSensor(self, commandList):
        return rhd2klib.createCommandListTempSensor(self.pointer, commandList.pointer)

    def createCommandListUpdateDigOut(self, commandList):
        return rhd2klib.createCommandListUpdateDigOut(self.pointer, commandList.pointer)

    def createCommandListZcheckDac(self, commandList, frequency, amplitude):
        return rhd2klib.createCommandListZcheckDac(self.pointer, commandList.pointer, frequency, amplitude)

    def createRhd2000Command0(self, commandType):
        return rhd2klib.createRhd2000Command0(self.pointer, commandType)

    def createRhd2000Command1(self, commandType, arg1):
        return rhd2klib.createRhd2000Command0(self.pointer, commandType, arg1)

    def createRhd2000Command2(self, commandType, arg1, arg2):
        return rhd2klib.createRhd2000Command0(self.pointer, commandType, arg1, arg2)
