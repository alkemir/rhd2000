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
    Rhd2000EvalBoard* newBoard(){ return new Rhd2000EvalBoard(); }
    int openBoard(Rhd2000EvalBoard* b){ return b->open(); }
    bool uploadFpgaBitfile(Rhd2000EvalBoard* b, char* filename){ return b->uploadFpgaBitfile(string(filename)); }
    void initialize(Rhd2000EvalBoard* b){ b->initialize(); }
    bool setSampleRate(Rhd2000EvalBoard* b, Rhd2000EvalBoard::AmplifierSampleRate newSampleRate){ return b->setSampleRate(newSampleRate); }
    double getSampleRate(Rhd2000EvalBoard* b){ return b->getSampleRate(); }
    Rhd2000EvalBoard::AmplifierSampleRate getSampleRateEnum(Rhd2000EvalBoard* b){ return b->getSampleRateEnum(); }
    void uploadCommandList(Rhd2000EvalBoard* b, vector<int> &commandList, Rhd2000EvalBoard::AuxCmdSlot auxCommandSlot, int bank){ b->uploadCommandList(commandList, auxCommandSlot, bank); }
    void printCommandList(Rhd2000EvalBoard* b, vector<int> &commandList){ b->printCommandList(commandList); }
    void selectAuxCommandBank(Rhd2000EvalBoard* b, Rhd2000EvalBoard::BoardPort port, Rhd2000EvalBoard::AuxCmdSlot auxCommandSlot, int bank){ b->selectAuxCommandBank(port, auxCommandSlot, bank); }
    void selectAuxCommandLength(Rhd2000EvalBoard* b, Rhd2000EvalBoard::AuxCmdSlot auxCommandSlot, int loopIndex, int endIndex){ b->selectAuxCommandLength(auxCommandSlot, loopIndex, endIndex); }
    void resetBoard(Rhd2000EvalBoard* b){ b->resetBoard(); }
    void setContinuousRunMode(Rhd2000EvalBoard* b, bool continuousMode){ b->setContinuousRunMode(continuousMode); }
    void setMaxTimeStep(Rhd2000EvalBoard* b, unsigned int maxTimeStep){ b->setMaxTimeStep(maxTimeStep); }
    void run(Rhd2000EvalBoard* b){ b->run(); }
    bool isRunning(Rhd2000EvalBoard* b){ return b->isRunning(); }
    unsigned int numWordsInFifo(Rhd2000EvalBoard* b){ return b->numWordsInFifo(); }
    unsigned int fifoCapacityInWords(){ return Rhd2000EvalBoard::fifoCapacityInWords(); }
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
}

extern "C" {
    vector<int>* new_vector_int(){ return new vector<int>; }
    void vector_int_delete(vector<int>* v){ delete v; }
    int vector_int_size(vector<int>* v){ return v->size(); }
    int vector_int_get(vector<int>* v, int i){ return v->at(i); }
    void vector_int_push_back(vector<int>* v, int i){ v->push_back(i); }
}

extern "C" {
    queue<Rhd2000DataBlock>* new_queue_data(){ return new queue<Rhd2000DataBlock>; }
    void queue_data_delete(queue<Rhd2000DataBlock>* q) {delete q;}
    unsigned int queue_data_size(queue<Rhd2000DataBlock>* q) { return q->size(); }
    Rhd2000DataBlock* queue_data_front(queue<Rhd2000DataBlock>* q) { return &(q->front()); }
    void queue_data_pop(queue<Rhd2000DataBlock>* q) { q->pop(); }
}

extern "C" {
    ofstream* new_ofstream() { return new ofstream; }
    void openFile(ofstream* out, char* filename) { out->open(string(filename), ios::binary | ios::out); }
    void closeFile(ofstream* out) { out->close(); }
}

extern "C" {
    Rhd2000Registers* newRegisters(double sampleRate){ return new Rhd2000Registers(sampleRate); }
    void defineSampleRate(Rhd2000Registers* r, double newSampleRate){ r->defineSampleRate(newSampleRate); }
    void setFastSettle(Rhd2000Registers* r, bool enabled){ r->setFastSettle(enabled); }
    void setDigOutLow(Rhd2000Registers* r){ r->setDigOutLow(); }
    void setDigOutHigh(Rhd2000Registers* r){ r->setDigOutHigh(); }
    void setDigOutHiZ(Rhd2000Registers* r){ r->setDigOutHiZ(); }
    void enableAux1(Rhd2000Registers* r, bool enabled){ r->enableAux1(enabled); }
    void enableAux2(Rhd2000Registers* r, bool enabled){ r->enableAux2(enabled); }
    void enableAux3(Rhd2000Registers* r, bool enabled){ r->enableAux3(enabled); }
    void enableDsp(Rhd2000Registers* r, bool enabled){ r->enableDsp(enabled); }
    //void disableDsp(Rhd2000Registers* r){ r->disableDsp(); }
    double setDspCutoffFreq(Rhd2000Registers* r, double newDspCutoffFreq){ return r->setDspCutoffFreq(newDspCutoffFreq); }
    double getDspCutoffFreq(Rhd2000Registers* r) { return r->getDspCutoffFreq(); }
    void enableZcheck(Rhd2000Registers* r, bool enabled){ r->enableZcheck(enabled); }
    void setZcheckDacPower(Rhd2000Registers* r, bool enabled){ r->setZcheckDacPower(enabled); }
    void setZcheckScale(Rhd2000Registers* r, Rhd2000Registers::ZcheckCs scale){ r->setZcheckScale(scale); }
    void setZcheckPolarity(Rhd2000Registers* r, Rhd2000Registers::ZcheckPolarity polarity){ r->setZcheckPolarity(polarity); }
    int setZcheckChannel(Rhd2000Registers* r, int channel){ return r->setZcheckChannel(channel); }
    void setAmpPowered(Rhd2000Registers* r, int channel, bool powered){ r->setAmpPowered(channel, powered); }
    void powerUpAllAmps(Rhd2000Registers* r){ r->powerUpAllAmps(); }
    void powerDownAllAmps(Rhd2000Registers* r){ r->powerDownAllAmps(); }
    int getRegisterValue(Rhd2000Registers* r, int reg) { return r->getRegisterValue(reg); }
    double setUpperBandwidth(Rhd2000Registers* r, double upperBandwidth){ return r->setUpperBandwidth(upperBandwidth); }
    double setLowerBandwidth(Rhd2000Registers* r, double lowerBandwidth){ return r->setLowerBandwidth(lowerBandwidth); }
    int createCommandListRegisterConfig(Rhd2000Registers* r, vector<int> &commandList, bool calibrate){ return r->createCommandListRegisterConfig(commandList, calibrate); }
    int createCommandListTempSensor(Rhd2000Registers* r, vector<int> &commandList){ return r->createCommandListTempSensor(commandList); }
    int createCommandListUpdateDigOut(Rhd2000Registers* r, vector<int> &commandList){ return r->createCommandListUpdateDigOut(commandList); }
    int createCommandListZcheckDac(Rhd2000Registers* r, vector<int> &commandList, double frequency, double amplitude){ return r->createCommandListZcheckDac(commandList, frequency, amplitude); }
    int createRhd2000Command0(Rhd2000Registers* r, Rhd2000Registers::Rhd2000CommandType commandType){ return r->createRhd2000Command(commandType); }
    int createRhd2000Command1(Rhd2000Registers* r, Rhd2000Registers::Rhd2000CommandType commandType, int arg1){ return r->createRhd2000Command(commandType, arg1); }
    int createRhd2000Command2(Rhd2000Registers* r, Rhd2000Registers::Rhd2000CommandType commandType, int arg1, int arg2){ return r->createRhd2000Command(commandType, arg1, arg2); }
}

extern "C" {
  Rhd2000DataBlock* newBlock(int numDataStreams){ return new Rhd2000DataBlock(numDataStreams); }
  unsigned int calculateDataBlockSizeInWords(int numDataStreams){ return Rhd2000DataBlock::calculateDataBlockSizeInWords(numDataStreams); }
  unsigned int getSamplesPerDataBlock(){ return Rhd2000DataBlock::getSamplesPerDataBlock(); }
  void fillFromUsbBuffer(Rhd2000DataBlock* d, unsigned char usbBuffer[], int blockIndex, int numDataStreams){ d->fillFromUsbBuffer(usbBuffer, blockIndex, numDataStreams); }
  void printData(Rhd2000DataBlock* d, int stream){ d->print(stream); }
  void write(Rhd2000DataBlock* d, ofstream &saveOut, int numDataStreams){ d->write(saveOut, numDataStreams); }
  bool checkUsbHeader(Rhd2000DataBlock* d, unsigned char usbBuffer[], int index){ return d->checkUsbHeader(usbBuffer, index); }
  int* readAmplifier(Rhd2000DataBlock* d, int stream, int channel) { return d->readAmplifier(stream, channel); }
  int* readAuxiliary(Rhd2000DataBlock* d, int stream, int channel) { return d->readAuxiliary(stream, channel); }
  int* readADC(Rhd2000DataBlock* d, int adc) { return d->readADC(adc); }
}
