import ctypes

rhd2klib = ctypes.cdll.LoadLibrary('./librhd2k.so')

rhd2klib._new.restype = ctypes.c_void_p
rhd2klib.open.argtypes = [ctypes.c_void_p]

rhd2klib.uploadFpgaBitfile.restype = ctypes.c_bool
rhd2klib.uploadFpgaBitfile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

rhd2klib.initialize.restype = None
rhd2klib.initialize.argtypes = [ctypes.c_void_p]

rhd2klib.setSampleRate.restype = [ctypes.c_bool]
rhd2klib.setSampleRate.argtypes = [ctypes.c_void_p, ctypes.c_int]

rhd2klib.getSampleRate.restype = ctypes.c_void_p
rhd2klib.getSampleRate.argtypes = [ctypes.c_double]


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

class EvalBoard:
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

#    Rhd2000EvalBoard::AmplifierSampleRate getSampleRateEnum(Rhd2000EvalBoard* b){ return b->getSampleRateEnum(); }
 
"""   void uploadCommandList(Rhd2000EvalBoard* b,  vector<int> &commandList, Rhd2000EvalBoard::AuxCmdSlot auxCommandSlot, int bank){;}
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



b = EvalBoard()

print (b.pointer)
print ("Opening")
b.open()

print (b.pointer)
print ("Uploading main.bit")
b.uploadFpgaBitfile(b'main.bit')

print ("Initializing")
b.initialize()
