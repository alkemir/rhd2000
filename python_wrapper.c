#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <time.h>

using namespace std;

#include "rhd2000evalboard.h"
#include "rhd2000registers.h"
#include "rhd2000datablock.h"
#include "okFrontPanelDLL.h"

extern "C" {
    Rhd2000EvalBoard* _new(){ return new Rhd2000EvalBoard(); } 
    int open(Rhd2000EvalBoard* b){ return b->open(); }
    bool uploadFpgaBitfile(Rhd2000EvalBoard* b, string filename){ return b->uploadFpgaBitfile(filename);}
    void initialize(Rhd2000EvalBoard* b){ b->initialize();}
    bool setSampleRate(Rhd2000EvalBoard* b, AmplifierSampleRate newSampleRate){ return b->setSampleRate(newSampleRate); }
    double getSampleRate(Rhd2000EvalBoard* b){ return b->getSampleRate(); }
    AmplifierSampleRate getSampleRateEnum(Rhd2000EvalBoard* b){ b->getSampleRateEnum(); }
    void uploadCommandList(Rhd2000EvalBoard* b,  vector<int> &commandList, AuxCmdSlot auxCommandSlot, int bank){;}
    void printCommandList(Rhd2000EvalBoard* b,  vector<int> &commandList){;}
    void selectAuxCommandBank(Rhd2000EvalBoard* b, BoardPort port, AuxCmdSlot auxCommandSlot, int bank){;}
    void selectAuxCommandLength(Rhd2000EvalBoard* b, AuxCmdSlot auxCommandSlot, int loopIndex, int endIndex){;}
    void resetBoard(Rhd2000EvalBoard* b){ b->resetBoard(); }
    void setContinuousRunMode(Rhd2000EvalBoard* b, bool continuousMode){ b->setContinuousRunMode(continuousMode); }
    void setMaxTimeStep(Rhd2000EvalBoard* b, unsigned int maxTimeStep){ b->setMaxTimeStep(maxTimeStep); }
    void run(Rhd2000EvalBoard* b){ b->run(); }
    bool isRunning(Rhd2000EvalBoard* b){ return b->isRunning(); }
    unsigned int numWordsInFifo(Rhd2000EvalBoard* b){ return b->numWordsInFifo(); }
    static unsigned int fifoCapacityInWords(Rhd2000EvalBoard* b){ return b->fifoCapacityInWords(); }
    void setCableDelay(Rhd2000EvalBoard* b, BoardPort port, int delay){ b->setCableDelay(port, delay); }
    void setCableLengthMeters(Rhd2000EvalBoard* b, BoardPort port, double lengthInMeters){ b->setCableLengthMeters(port, lengthInMeters); }
    void setCableLengthFeet(Rhd2000EvalBoard* b, BoardPort port, double lengthInFeet){ b->setCableLengthFeet(port, lengthInFeet); }
    double estimateCableLengthMeters(Rhd2000EvalBoard* b, int delay){ return b->estimateCableLengthMeters(delay); }
    double estimateCableLengthFeet(Rhd2000EvalBoard* b, int delay){ return b->estimateCableLengthFeet(delay); }
    void setDspSettle(Rhd2000EvalBoard* b, bool enabled){ b->setDspSettle(enabled); }
    void setDataSource(Rhd2000EvalBoard* b, int stream, BoardDataSource dataSource){ b->setDataSource(stream, dataSource); }
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
    void enableExternalDigOut(Rhd2000EvalBoard* b, BoardPort port, bool enable){ b->enableExternalDigOut(port, enable); }
    void setExternalDigOutChannel(Rhd2000EvalBoard* b, BoardPort port, int channel){ b->setExternalDigOutChannel(port, channel); }
    void enableDacHighpassFilter(Rhd2000EvalBoard* b, bool enable){ b->enableDacHighpassFilter(enable); }
    void setDacHighpassFilter(Rhd2000EvalBoard* b, double cutoff){ b->setDacHighpassFilter(cutoff); }
    void setDacThreshold(Rhd2000EvalBoard* b, int dacChannel, int threshold, bool trigPolarity){ b->setDacThreshold(dacChannel, threshold, trigPolarity); }
    void setTtlMode(Rhd2000EvalBoard* b, int mode){ b->setTtlMode(mode); }
    void flush(Rhd2000EvalBoard* b){ b->flush(); }
    bool readDataBlock(Rhd2000EvalBoard* b, Rhd2000DataBlock *dataBlock){ return b->readDataBlock(dataBlock); }
    bool readDataBlocks(Rhd2000EvalBoard* b, int numBlocks, queue<Rhd2000DataBlock> &dataQueue){ return b->readDataBlocks(numBlocks, dataQueue); }
    int queueToFile(Rhd2000EvalBoard* b, queue<Rhd2000DataBlock> &dataQueue, std::ofstream &saveOut){ return b->queueToFile(dataQueue, saveOut); }
    int getBoardMode(Rhd2000EvalBoard* b){ return b->getBoardMode(); }
    int getCableDelay(Rhd2000EvalBoard* b, BoardPort port){ return b->getCableDelay(port); }
    void getCableDelay(Rhd2000EvalBoard* b, vector<int> &delays){ b->getCableDelay(delays); }
}
