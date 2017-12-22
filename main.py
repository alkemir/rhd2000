import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

#AmplifierSampleRate
SampleRate1000Hz = 0
SampleRate1250Hz = 1
SampleRate1500Hz = 2
SampleRate2000Hz = 3
SampleRate2500Hz = 4
SampleRate3000Hz = 5
SampleRate3333Hz = 6
SampleRate4000Hz = 7
SampleRate5000Hz = 8
SampleRate6250Hz = 9
SampleRate8000Hz = 10
SampleRate10000Hz = 11
SampleRate12500Hz = 12
SampleRate15000Hz = 13
SampleRate20000Hz = 14
SampleRate25000Hz = 15
SampleRate30000Hz = 16

#AuxCmdSlot
AuxCmd1 = 0
AuxCmd2 = 1
AuxCmd3 = 2

#BoardPort
PortA = 0
PortB = 1
PortC = 2
PortD = 3

#BoardDataSource
PortA1 = 0
PortA2 = 1
PortB1 = 2
PortB2 = 3
PortC1 = 4
PortC2 = 5
PortD1 = 6
PortD2 = 7
PortA1Ddr = 8
PortA2Ddr = 9
PortB1Ddr = 10
PortB2Ddr = 11
PortC1Ddr = 12
PortC2Ddr = 13
PortD1Ddr = 14
PortD2Ddr = 15

class EvalBoard:
	rhd2klib._new.restype = ctypes.c_void_p
	rhd2klib._new.argtypes = []
	rhd2klib.open.restype = ctypes.c_int
	rhd2klib.open.argtypes = [ctypes.c_void_p]
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
	rhd2klib.fifoCapacityInWords.restype = None
	rhd2klib.fifoCapacityInWords.argtypes = [ctypes.c_void_p]
	    static unsigned int (Rhd2000EvalBoard* b){ return b->fifoCapacityInWords(); }

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
	rhd2klib.readDataBlock.argtypes = [ctypes.c_void_p]
	(Rhd2000EvalBoard* b, Rhd2000DataBlock *dataBlock)

	rhd2klib.readDataBlocks.restype = ctypes.c_bool
	rhd2klib.readDataBlocks.argtypes = [ctypes.c_void_p]
	(Rhd2000EvalBoard* b, int numBlocks, queue<Rhd2000DataBlock> &dataQueue)

	rhd2klib.queueToFile.restype = ctypes.c_int
	rhd2klib.queueToFile.argtypes = [ctypes.c_void_p]
	(Rhd2000EvalBoard* b, queue<Rhd2000DataBlock> &dataQueue, std::ofstream &saveOut)

	rhd2klib.getBoardMode.restype = ctypes.c_int
	rhd2klib.getBoardMode.argtypes = [ctypes.c_void_p]
	rhd2klib.getCableDelayPort.restype = ctypes.c_int
	rhd2klib.getCableDelayPort.argtypes = [ctypes.c_void_p, ctypes.c_uint]
	rhd2klib.getCableDelays.restype = None
	rhd2klib.getCableDelays.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

	def __init__(self):
		self.pointer = rhd2klib._new()

	def open(self):
		return rhd2klib.open(self.pointer)

	def uploadFpgaBitfile(self, filename):
		return rhd2klib.uploadFpgaBitfile(self.pointer, filename)

	def initialize(self):
		rhd2klib.initialize(self.pointer)

	def setSampleRate(self, newSampleRate):
		return rhd2klib.setSampleRate(self.pointer, newSampleRate)

	def getSampleRate(self):
		return rhd2klib.getSampleRate(self.pointer)

	def getSampleRateEnum(self):
		return rhd2klib.getSampleRateEnum(self.pointer)

	def uploadCommandList(self, commandList, auxCommandSlot, bank):
		rhd2klib.uploadCommandList(self.pointer, commandList, auxCommandSlot, bank)

#(ctypes.c_int * len(pyarr))(*pyarr)
"""
    void printCommandList(Rhd2000EvalBoard* b,  vector<int> &commandList){;}
    void selectAuxCommandBank(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port, Rhd2000EvalBoard::AuxCmdSlot auxCommandSlot, int bank){;}
    void selectAuxCommandLength(Rhd2000EvalBoard* b, Rhd2000EvalBoard::AuxCmdSlot auxCommandSlot, int loopIndex, int endIndex){;}
    void resetBoard(Rhd2000EvalBoard* b){ b->resetBoard(); }
    void setContinuousRunMode(Rhd2000EvalBoard* b, bool continuousMode){ b->setContinuousRunMode(continuousMode); }
    void setMaxTimeStep(Rhd2000EvalBoard* b, unsigned int maxTimeStep){ b->setMaxTimeStep(maxTimeStep); }
    void run(Rhd2000EvalBoard* b){ b->run(); }
    bool isRunning(Rhd2000EvalBoard* b){ return b->isRunning(); }
    unsigned int numWordsInFifo(Rhd2000EvalBoard* b){ return b->numWordsInFifo(); }
    static unsigned int fifoCapacityInWords(Rhd2000EvalBoard* b){ return b->fifoCapacityInWords(); }
    void setCableDelay(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port, int delay){ b->setCableDelay(port, delay); }
    void setCableLengthMeters(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port, double lengthInMeters){ b->setCableLengthMeters(port, lengthInMeters); }
    void setCableLengthFeet(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port, double lengthInFeet){ b->setCableLengthFeet(port, lengthInFeet); }
    double estimateCableLengthMeters(Rhd2000EvalBoard* b, int delay){ return b->estimateCableLengthMeters(delay); }
    double estimateCableLengthFeet(Rhd2000EvalBoard* b, int delay){ return b->estimateCableLengthFeet(delay); }
    void setDspSettle(Rhd2000EvalBoard* b, bool enabled){ b->setDspSettle(enabled); }
    void setDataSource(Rhd2000EvalBoard* b, int stream, Rhd2000EvalBoard::BoardDataSource dataSource){ b->setDataSource(stream, dataSource); }
    void enableDataStream(Rhd2000EvalBoard* b, int stream, bool enabled){ b->enableDataStream(stream, enabled); }
    int getNumEnabledDataStreams(Rhd2000EvalBoard* b){ return b->getNumEnabledDataStreams(); }
    void clearTtlOut(Rhd2000EvalBoard* b){ b->clearTtlOut(); }
    void setTtlOut(Rhd2000EvalBoard* b, int ttlOutArray[]){ b->setTtlOut(ttlOutArray); }
    void getTtlIn(Rhd2000EvalBoard* b, int ttlInArray[]){ b->getTtlIn(ttlInArray); }
    void setDacManual(Rhd2000EvalBoard* b, int value){ b->setDacManual(value); }
    void setLedDisplay(Rhd2000EvalBoard* b, int ledArray[]){ b->setLedDisplay(ledArray); }
    void enableDac(Rhd2000EvalBoard* b, int dacChannel, bool enabled){ b->enableDac(dacChannel, enabled); }
    void setDacGain(Rhd2000EvalBoard* b, int gain){ b->setDacGain(gain); }
    void setAudioNoiseSuppress(Rhd2000EvalBoard* b, int noiseSuppress){ b->setAudioNoiseSuppress(noiseSuppress); }
    void selectDacDataStream(Rhd2000EvalBoard* b, int dacChannel, int stream){ b->selectDacDataStream(dacChannel, stream); }
    void selectDacDataChannel(Rhd2000EvalBoard* b, int dacChannel, int dataChannel){ b->selectDacDataChannel(dacChannel, dataChannel); }
    void enableExternalFastSettle(Rhd2000EvalBoard* b, bool enable){ b->enableExternalFastSettle(enable); }
    void setExternalFastSettleChannel(Rhd2000EvalBoard* b, int channel){ b->setExternalFastSettleChannel(channel); }
    void enableExternalDigOut(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port, bool enable){ b->enableExternalDigOut(port, enable); }
    void setExternalDigOutChannel(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port, int channel){ b->setExternalDigOutChannel(port, channel); }
    void enableDacHighpassFilter(Rhd2000EvalBoard* b, bool enable){ b->enableDacHighpassFilter(enable); }
    void setDacHighpassFilter(Rhd2000EvalBoard* b, double cutoff){ b->setDacHighpassFilter(cutoff); }
    void setDacThreshold(Rhd2000EvalBoard* b, int dacChannel, int threshold, bool trigPolarity){ b->setDacThreshold(dacChannel, threshold, trigPolarity); }
    void setTtlMode(Rhd2000EvalBoard* b, int mode){ b->setTtlMode(mode); }
    void flush(Rhd2000EvalBoard* b){ b->flush(); }
    bool readDataBlock(Rhd2000EvalBoard* b, Rhd2000DataBlock *dataBlock){ return b->readDataBlock(dataBlock); }
    bool readDataBlocks(Rhd2000EvalBoard* b, int numBlocks, queue<Rhd2000DataBlock> &dataQueue){ return b->readDataBlocks(numBlocks, dataQueue); }
    int queueToFile(Rhd2000EvalBoard* b, queue<Rhd2000DataBlock> &dataQueue, std::ofstream &saveOut){ return b->queueToFile(dataQueue, saveOut); }
    int getBoardMode(Rhd2000EvalBoard* b){ return b->getBoardMode(); }
    int getCableDelayPort(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port){ return b->getCableDelay(port); }
    void getCableDelays(Rhd2000EvalBoard* b, vector<int> &delays){ b->getCableDelay(delays); }
"""

class Vector(object):
    rhd2klib.new_vector_int.restype = c_void_p
    rhd2klib.new_vector_int.argtypes = []
    rhd2klib.delete_vector_int.restype = None
    rhd2klib.delete_vector_int.argtypes = [c_void_p]
    rhd2klib.vector_int_size.restype = c_int
    rhd2klib.vector_int_size.argtypes = [c_void_p]
    rhd2klib.vector_int_get.restype = c_int
    rhd2klib.vector_int_get.argtypes = [c_void_p, c_int]
    rhd2klib.vector_int_push_back.restype = None
    rhd2klib.vector_int_push_back.argtypes = [c_void_p, c_int]

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



b = EvalBoard()

print (b.pointer)
print ("Opening")
b.open()

print (b.pointer)
print ("Uploading main.bit")
b.uploadFpgaBitfile(b'main.bit')

print ("Initializing")
b.initialize()
