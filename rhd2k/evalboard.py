import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

class EvalBoard:
	rhd2klib.newBoard.restype = ctypes.c_void_p
	rhd2klib.newBoard.argtypes = []
	rhd2klib.openBoard.restype = ctypes.c_int
	rhd2klib.openBoard.argtypes = [ctypes.c_void_p]
	rhd2klib.uploadFpgaBitfile.restype = ctypes.c_bool
	rhd2klib.uploadFpgaBitfile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
	rhd2klib.initialize.restype = None
	rhd2klib.initialize.argtypes = [ctypes.c_void_p]
	rhd2klib.setSampleRate.restype = ctypes.c_bool
	rhd2klib.setSampleRate.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.getSampleRate.restype = ctypes.c_double
	rhd2klib.getSampleRate.argtypes = [ctypes.c_void_p]
	rhd2klib.getSampleRateEnum.restype = ctypes.c_uint
	rhd2klib.getSampleRateEnum.argtypes = [ctypes.c_void_p]
	rhd2klib.uploadCommandList.restype = None
	rhd2klib.uploadCommandList.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_int]
	rhd2klib.printCommandList.restype = None
	rhd2klib.printCommandList.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
	rhd2klib.selectAuxCommandBank.restype = None
	rhd2klib.selectAuxCommandBank.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_int]
	rhd2klib.selectAuxCommandLength.restype = None
	rhd2klib.selectAuxCommandLength.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int]
	rhd2klib.resetBoard.restype = None
	rhd2klib.resetBoard.argtypes = [ctypes.c_void_p]
	rhd2klib.setContinuousRunMode.restype = None
	rhd2klib.setContinuousRunMode.argtypes = [ctypes.c_void_p, ctypes.c_bool]
	rhd2klib.setMaxTimeStep.restype = None
	rhd2klib.setMaxTimeStep.argtypes = [ctypes.c_void_p, ctypes.c_uint]
	rhd2klib.run.restype = None
	rhd2klib.run.argtypes = [ctypes.c_void_p]
	rhd2klib.isRunning.restype = ctypes.c_bool
	rhd2klib.isRunning.argtypes = [ctypes.c_void_p]
	rhd2klib.numWordsInFifo.restype = ctypes.c_uint
	rhd2klib.numWordsInFifo.argtypes = [ctypes.c_void_p]
	rhd2klib.fifoCapacityInWords.restype = ctypes.c_uint
	rhd2klib.fifoCapacityInWords.argtypes = []
	rhd2klib.setCableDelay.restype = None
	rhd2klib.setCableDelay.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int]
	rhd2klib.setCableLengthMeters.restype = None
	rhd2klib.setCableLengthMeters.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_double]
	rhd2klib.setCableLengthFeet.restype = None
	rhd2klib.setCableLengthFeet.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_double]
	rhd2klib.estimateCableLengthMeters.restype = ctypes.c_double
	rhd2klib.estimateCableLengthMeters.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.estimateCableLengthFeet.restype = ctypes.c_double
	rhd2klib.estimateCableLengthFeet.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.setDspSettle.restype = None
	rhd2klib.setDspSettle.argtypes = [ctypes.c_void_p, ctypes.c_bool]
	rhd2klib.setDataSource.restype = None
	rhd2klib.setDataSource.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint]
	rhd2klib.enableDataStream.restype = None
	rhd2klib.enableDataStream.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_bool]
	rhd2klib.getNumEnabledDataStreams.restype = ctypes.c_int
	rhd2klib.getNumEnabledDataStreams.argtypes = [ctypes.c_void_p]
	rhd2klib.clearTtlOut.restype = None
	rhd2klib.clearTtlOut.argtypes = [ctypes.c_void_p]
	rhd2klib.setTtlOut.restype = None
	rhd2klib.setTtlOut.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
	rhd2klib.getTtlIn.restype = None
	rhd2klib.getTtlIn.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
	rhd2klib.setDacManual.restype = None
	rhd2klib.setDacManual.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.setLedDisplay.restype = None
	rhd2klib.setLedDisplay.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
	rhd2klib.enableDac.restype = None
	rhd2klib.enableDac.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_bool]
	rhd2klib.setDacGain.restype = None
	rhd2klib.setDacGain.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.setAudioNoiseSuppress.restype = None
	rhd2klib.setAudioNoiseSuppress.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.selectDacDataStream.restype = None
	rhd2klib.selectDacDataStream.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
	rhd2klib.selectDacDataChannel.restype = None
	rhd2klib.selectDacDataChannel.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
	rhd2klib.enableExternalFastSettle.restype = None
	rhd2klib.enableExternalFastSettle.argtypes = [ctypes.c_void_p, ctypes.c_bool]
	rhd2klib.setExternalFastSettleChannel.restype = None
	rhd2klib.setExternalFastSettleChannel.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.enableExternalDigOut.restype = None
	rhd2klib.enableExternalDigOut.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_bool]
	rhd2klib.setExternalDigOutChannel.restype = None
	rhd2klib.setExternalDigOutChannel.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int]
	rhd2klib.enableDacHighpassFilter.restype = None
	rhd2klib.enableDacHighpassFilter.argtypes = [ctypes.c_void_p, ctypes.c_bool]
	rhd2klib.setDacHighpassFilter.restype = None
	rhd2klib.setDacHighpassFilter.argtypes = [ctypes.c_void_p, ctypes.c_double]
	rhd2klib.setDacThreshold.restype = None
	rhd2klib.setDacThreshold.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
	rhd2klib.setTtlMode.restype = None
	rhd2klib.setTtlMode.argtypes = [ctypes.c_void_p, ctypes.c_int]
	rhd2klib.flush.restype = None
	rhd2klib.flush.argtypes = [ctypes.c_void_p]
	rhd2klib.readDataBlock.restype = ctypes.c_bool
	rhd2klib.readDataBlock.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
	rhd2klib.readDataBlocks.restype = ctypes.c_bool
	rhd2klib.readDataBlocks.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
	rhd2klib.queueToFile.restype = ctypes.c_int
	rhd2klib.queueToFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
	rhd2klib.getBoardMode.restype = ctypes.c_int
	rhd2klib.getBoardMode.argtypes = [ctypes.c_void_p]
	rhd2klib.getCableDelayPort.restype = ctypes.c_int
	rhd2klib.getCableDelayPort.argtypes = [ctypes.c_void_p, ctypes.c_uint]
	rhd2klib.getCableDelays.restype = None
	rhd2klib.getCableDelays.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

	def __init__(self):
		self._as_parameter_ = rhd2klib.newBoard()

	def open(self):
		return rhd2klib.openBoard(self)

	def uploadFpgaBitfile(self, filename):
		return rhd2klib.uploadFpgaBitfile(self, filename)

	def initialize(self):
		rhd2klib.initialize(self)

	def setSampleRate(self, newSampleRate):
		return rhd2klib.setSampleRate(self, newSampleRate)

	def getSampleRate(self):
		return rhd2klib.getSampleRate(self)

	def getSampleRateEnum(self):
		return rhd2klib.getSampleRateEnum(self)

	def uploadCommandList(self, commandList, auxCommandSlot, bank):
		rhd2klib.uploadCommandList(self, commandList, auxCommandSlot, bank)

	def printCommandList(self, commandList):
		rhd2klib.printCommandList(self, commandList)

	def selectAuxCommandBank(self, port, auxCommandSlot, bank):
		rhd2klib.selectAuxCommandBank(self, port, auxCommandSlot, bank)

	def selectAuxCommandLength(self, auxCommandSlot, loopIndex, endIndex):
		rhd2klib.selectAuxCommandLength(self, auxCommandSlot, loopIndex, endIndex)

	def resetBoard(self):
		rhd2klib.resetBoard(self)

	def setContinuousRunMode(self, continuousMode):
		rhd2klib.setContinuousRunMode(self, continuousMode)

	def setMaxTimeStep(self, maxTimeStep):
		rhd2klib.setMaxTimeStep(self, maxTimeStep)

	def run(self):
		rhd2klib.run(self)

	def isRunning(self):
		return rhd2klib.isRunning(self)

	def numWordsInFifo(self):
		return rhd2klib.numWordsInFifo(self)

	@staticmethod
	def fifoCapacityInWords():
		return rhd2klib.fifoCapacityInWords()

	def setCableDelay(self, port, delay):
		rhd2klib.setCableDelay(self, port, delay)

	def setCableLengthMeters(self, port, lengthInMeters):
		rhd2klib.setCableLengthMeters(self, port, lengthInMeters)

	def setCableLengthFeet(self, port, lengthInFeet):
		rhd2klib.setCableLengthFeet(self, port, lengthInFeet)

	def estimateCableLengthMeters(self, delay):
		return rhd2klib.estimateCableLengthMeters(self, delay)

	def estimateCableLengthFeet(self, delay):
		return rhd2klib.estimateCableLengthFeet(self, delay)

	def setDspSettle(self, enabled):
		rhd2klib.setDspSettle(self, enabled)

	def setDataSource(self, stream, dataSource):
		rhd2klib.setDataSource(self, stream, dataSource)

	def enableDataStream(self, stream, enabled):
		rhd2klib.enableDataStream(self, stream, enabled)

	def getNumEnabledDataStreams(self):
		return rhd2klib.getNumEnabledDataStreams(self)

	def clearTtlOut(self):
		rhd2klib.clearTtlOut(self)

	def setTtlOut(self, ttlOutArray):
		ttlOutArray = (ctypes.c_int * len(ttlOutArray))(*ttlOutArray)
		rhd2klib.setTtlOut(self, ttlOutArray)

	def getTtlIn(self, length):
		ttlInArray = (ctypes.c_int * length)
		rhd2klib.getTtlIn(self, ttlInArray)
		return ttlInArray #test this

	def setDacManual(self, value):
		rhd2klib.setDacManual(self, value)

	def setLedDisplay(self, ledArray):
		ledArray = (ctypes.c_int * len(ledArray))(*ledArray)
		rhd2klib.setLedDisplay(self, ledArray)

	def enableDac(self, dacChannel, enabled):
		rhd2klib.enableDac(self, dacChannel, enabled)

	def setDacGain(self, gain):
		rhd2klib.setDacGain(self, gain)

	def setAudioNoiseSuppress(self, noiseSuppress):
		rhd2klib.setAudioNoiseSuppress(self, noiseSuppress)

	def selectDacDataStream(self, dacChannel, stream):
		rhd2klib.selectDacDataStream(self, dacChannel, stream)

	def selectDacDataChannel(self, dacChannel, dataChannel):
		rhd2klib.selectDacDataChannel(self, dacChannel, dataChannel)

	def enableExternalFastSettle(self, enable):
		rhd2klib.enableExternalFastSettle(self, enable)

	def setExternalFastSettleChannel(self, channel):
		rhd2klib.setExternalFastSettleChannel(self, channel)

	def enableExternalDigOut(self, port, enable):
		rhd2klib.enableExternalDigOut(self, port, enable)

	def setExternalDigOutChannel(self, port, channel):
		rhd2klib.setExternalDigOutChannel(self, port, channel)

	def enableDacHighpassFilter(self, enable):
		rhd2klib.enableDacHighpassFilter(self, enable)

	def setDacHighpassFilter(self, cutoff):
		rhd2klib.setDacHighpassFilter(self, cutoff)

	def setDacThreshold(self, dacChannel, threshold, trigPolarity):
		rhd2klib.setDacThreshold(self, dacChannel, threshold, trigPolarity)

	def setTtlMode(self, mode):
		rhd2klib.setTtlMode(self, mode)

	def flush(self):
		rhd2klib.flush(self)

	def readDataBlock(self, dataBlock):
		return rhd2klib.readDataBlock(self, dataBlock)

	def readDataBlocks(self, numBlocks, dataQueue):
		return rhd2klib.readDataBlocks(self, numBlocks, dataQueue)

	def queueToFile(self, dataQueue, saveOut):
		return rhd2klib.queueToFile(self, dataQueue, saveOut)

	def getBoardMode(self):
		return rhd2klib.getBoardMode(self)

	def getCableDelayPort(self, port):
		return rhd2klib.getCableDelay(self, port)

	def getCableDelays(self, delays):
		rhd2klib.getCableDelays(self, delays)
