#!/usr/bin/python3
# -*- coding: utf-8 -*-

from numpy import random
import math

from PyQt5.QtCore import QFile, QIODevice, QDataStream

import constants

dataStreamBuffer = [' '] * \
    (2 * constants.MAX_NUM_DATA_STREAMS * 32 * constants.SAMPLES_PER_DATA_BLOCK)
# Assume maximum number of data blocks = 16
dataStreamBufferArray = [
    [' ']*(2 * constants.SAMPLES_PER_DATA_BLOCK * 16)]*(constants.MAX_NUM_DATA_STREAMS * 32)
bufferArrayIndex = [0]*(constants.MAX_NUM_DATA_STREAMS * 32)


class SignalProcessor():
    """ This class stores and processes short segments of waveform data
    acquired from the USB interface board.  The primary purpose of the
    class is to read from a queue of Rhd2000DataBlock objects and scale
    this raw data appropriately to generate wavefrom vectors with units
    of volts or microvolts.

    The class is also capable of applying a notch filter to amplifier
    waveform data, measuring the amplitude of a particular frequency
    component (useful in the electrode impedance measurements), and
    generating synthetic neural or ECG data for demonstration purposes.
    """

    def __init__(self):
        # Notch filter initial parameters.
        self.notchFilterEnabled = False
        self.a1 = 0.0
        self.a2 = 0.0
        self.b0 = 0.0
        self.b1 = 0.0
        self.b2 = 0.0

        # Highpass filter initial parameters.
        self.highpassFilterEnabled = False
        self.aHpf = 0.0
        self.bHpf = 0.0

        # Set up random number generator in case we are asked to generate synthetic data.
        # (br): replaced

        # Other synthetic waveform variables.
        self.tPulse = 0.0
        self.synthTimeStamp = 0

        # Initialize to have definition here
        self.numDataStreams = 0
        self.amplifierPreFilter = 0
        self.amplifierPostFilter = 0
        self.highpassFilterState = 0
        self.prevAmplifierPreFilter = 0
        self.prevAmplifierPostFilter = 0
        self.auxChannel = 0
        self.supplyVoltage = 0
        self.tempRaw = 0
        self.tempAvg = 0
        self.boardAdc = 0
        self.boardDigIn = 0
        self.boardDigOut = 0
        self.synthSpikeAmplitude = 0
        self.synthSpikeDuration = 0
        self.synthRelativeSpikeRate = 0
        self.synthEcgAmplitude = 0
        self.tempRawHistory = 0
        self.saveListBoardDigIn = 0

        # Filenames
        self.timestampFileName = ""
        self.amplifierFileName = ""
        self.auxInputFileName = ""
        self.supplyFileName = ""
        self.adcInputFileName = ""
        self.digitalInputFileName = ""
        self.digitalOutputFileName = ""

        # Files
        self.timestampFile = None
        self.amplifierFile = None
        self.auxInputFile = None
        self.supplyFile = None
        self.adcInputFile = None
        self.digitalInputFile = None
        self.digitalOutputFile = None

        # Streams
        self.timestampStream = None
        self.amplifierStream = None
        self.auxInputStream = None
        self.supplyStream = None
        self.adcInputStream = None
        self.digitalInputStream = None
        self.digitalOutputStream = None

        # Lists
        self.saveListAmplifier = []
        self.saveListAuxInput = []
        self.saveListSupplyVoltage = []
        self.saveListBoardAdc = []
        self.saveListBoardDigitalIn = []
        self.saveListBoardDigitalOut = []
        self.saveListTempSensor = []

        self.tempHistoryLength = 0
        self.tempHistoryMaxLength = 0

    # Allocate memory to store waveform data.
    def allocateMemory(self, numStreams):
        self.numDataStreams = numStreams

        # The maximum number of Rhd2000DataBlock objects we will need is set by the need
        # to perform electrode impedance measurements at very low frequencies.
        maxNumBlocks = 120

        # Allocate vector memory for waveforms from USB interface board and notch filter.
        self.amplifierPreFilter = allocateDoubleArray3D(
            numStreams, 32, constants.SAMPLES_PER_DATA_BLOCK * maxNumBlocks)
        self.amplifierPostFilter = allocateDoubleArray3D(
            numStreams, 32, constants.SAMPLES_PER_DATA_BLOCK * maxNumBlocks)
        self.highpassFilterState = allocateDoubleArray2D(numStreams, 32)
        self.prevAmplifierPreFilter = allocateDoubleArray3D(numStreams, 32, 2)
        self.prevAmplifierPostFilter = allocateDoubleArray3D(numStreams, 32, 2)
        self.auxChannel = allocateDoubleArray3D(
            numStreams, 3, (constants.SAMPLES_PER_DATA_BLOCK // 4) * maxNumBlocks)
        self.supplyVoltage = allocateDoubleArray2D(numStreams, maxNumBlocks)
        self.tempRaw = allocateDoubleArray1D(numStreams)
        self.tempAvg = allocateDoubleArray1D(numStreams)
        self.boardAdc = allocateDoubleArray2D(
            8, constants.SAMPLES_PER_DATA_BLOCK * maxNumBlocks)
        self.boardDigIn = allocateIntArray2D(
            16, constants.SAMPLES_PER_DATA_BLOCK * maxNumBlocks)
        self.boardDigOut = allocateIntArray2D(
            16, constants.SAMPLES_PER_DATA_BLOCK * maxNumBlocks)

        # Initialize vector memory used in notch filter state.
        fillZerosDoubleArray3D(self.amplifierPostFilter)
        fillZerosDoubleArray3D(self.prevAmplifierPreFilter)
        fillZerosDoubleArray3D(self.prevAmplifierPostFilter)
        fillZerosDoubleArray2D(self.highpassFilterState)

        # Allocate vector memory for generating synthetic neural and ECG waveforms.
        self.synthSpikeAmplitude = allocateDoubleArray3D(numStreams, 32, 2)
        self.synthSpikeDuration = allocateDoubleArray3D(numStreams, 32, 2)
        self.synthRelativeSpikeRate = allocateDoubleArray2D(numStreams, 32)
        self.synthEcgAmplitude = allocateDoubleArray2D(numStreams, 32)

        # Assign random parameters for synthetic waveforms.
        for stream in range(0, numStreams):
            for channel in range(0, 32):
                self.synthEcgAmplitude[stream][channel] = random.uniform(
                    0.5, 3.0)
                for spikeNum in range(0, 2):
                    self.synthSpikeAmplitude[stream][channel][spikeNum] = random.uniform(
                        -400.0, 100.0)
                    self.synthSpikeDuration[stream][channel][spikeNum] = random.uniform(
                        0.3, 1.7)
                    self.synthRelativeSpikeRate[stream][channel] = random.uniform(
                        0.1, 5.0)

        # Initialize vector for averaging temperature readings over time.
        self.tempRawHistory = allocateDoubleArray2D(
            numStreams, maxNumBlocks)
        self.tempHistoryReset(4)

    # Creates lists (vectors, actually) of all enabled waveforms to expedite
    # save-to-disk operations.
    def createSaveList(self, signalSources, addTriggerChannel, triggerChannel):
        self.synthTimeStamp = 0  # for synthetic data mode

        self.saveListAmplifier.clear()
        self.saveListAuxInput.clear()
        self.saveListSupplyVoltage.clear()
        self.saveListBoardAdc.clear()
        self.saveListBoardDigitalIn.clear()
        self.saveListBoardDigitalOut.clear()
        self.saveListTempSensor.clear()

        self.saveListBoardDigIn = False

        for port in range(len(signalSources.signalPort)):
            for index in range(signalSources.signalPort[port].numChannels()):
                currentChannel = signalSources.signalPort[port].channelByNativeOrder(
                    index)
                # Maybe add this channel if it is the trigger channel.
                if addTriggerChannel:
                    if triggerChannel > 15 and currentChannel.signalType == constants.BoardAdcSignal:
                        if currentChannel.nativeChannelNumber == triggerChannel - 16:
                            currentChannel.enabled = True

                elif (triggerChannel < 16 and currentChannel.signalType == constants.BoardDigInSignal):
                    if currentChannel.nativeChannelNumber == triggerChannel:
                        currentChannel.enabled = True

                # Add all enabled channels to their appropriate save list.
                if currentChannel.enabled:
                    if currentChannel.signalType == constants.AmplifierSignal:
                        self.saveListAmplifier.append(currentChannel)
                    elif currentChannel.signalType == constants.AuxInputSignal:
                        self.saveListAuxInput.append(currentChannel)
                    elif currentChannel.signalType == constants.SupplyVoltageSignal:
                        self.saveListSupplyVoltage.append(currentChannel)
                    elif currentChannel.signalType == constants.BoardAdcSignal:
                        self.saveListBoardAdc.append(currentChannel)
                    elif currentChannel.signalType == constants.BoardDigInSignal:
                        self.saveListBoardDigIn = True
                        self.saveListBoardDigitalIn.append(currentChannel)
                    elif currentChannel.signalType == constants.BoardDigOutSignal:
                        self.saveListBoardDigitalOut.append(currentChannel)

                # Use supply voltage signal as a proxy for the presence of a temperature sensor,
                # since these always appear together on each chip.  Add all temperature sensors
                # list, whether or not the corresponding supply voltage signals are enabled.
                if currentChannel.signalType == constants.SupplyVoltageSignal:
                    self.saveListTempSensor.append(currentChannel)

    # Create filename (appended to the specified path) for timestamp data.
    def createTimestampFilename(self, path):
        self.timestampFileName = path + "/" + "time" + ".dat"

    # Create filename (appended to the specified path) for data files in
    # "One File Per Signal Type" format.
    def createSignalTypeFilenames(self, path):
        self.amplifierFileName = path + "/" + "amplifier" + ".dat"
        self.auxInputFileName = path + "/" + "auxiliary" + ".dat"
        self.supplyFileName = path + "/" + "supply" + ".dat"
        self.adcInputFileName = path + "/" + "analogin" + ".dat"
        self.digitalInputFileName = path + "/" + "digitalin" + ".dat"
        self.digitalOutputFileName = path + "/" + "digitalout" + ".dat"

    # Open timestamp save file.
    def openTimestampFile(self):
        self.timestampFile = QFile(self.timestampFileName)

        if not self.timestampFile.open(QIODevice.WriteOnly):
            print("Cannot open file for writing: " +
                  str(self.timestampFile.errorString()) + "\n")

        timestampStream = QDataStream(self.timestampFile)
        timestampStream.setVersion(QDataStream.Qt_4_8)

        # Set to little endian mode for compatibilty with MATLAB,
        # which is little endian on all platforms
        timestampStream.setByteOrder(QDataStream.LittleEndian)

        # Write 4-byte floating-point numbers (instead of the default 8-byte numbers)
        # to save disk space.
        timestampStream.setFloatingPointPrecision(QDataStream.SinglePrecision)

    # Open data files for "One File Per Signal Type" format.
    def openSignalTypeFiles(self, saveTtlOut):
        amplifierFile = 0
        auxInputFile = 0
        supplyFile = 0
        adcInputFile = 0
        digitalInputFile = 0
        digitalOutputFile = 0

        amplifierStream = 0
        auxInputStream = 0
        supplyStream = 0
        adcInputStream = 0
        digitalInputStream = 0
        digitalOutputStream = 0

        if self.saveListAmplifier:
            amplifierFile = QFile(self.amplifierFileName)
            if not amplifierFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(amplifierFile.errorString()) + "\n")
            amplifierStream = QDataStream(amplifierFile)
            amplifierStream.setVersion(QDataStream.Qt_4_8)
            amplifierStream.setByteOrder(QDataStream.LittleEndian)
            amplifierStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

        if self.saveListAuxInput:
            auxInputFile = QFile(self.auxInputFileName)
            if not auxInputFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(auxInputFile.errorString()) + "\n")
            auxInputStream = QDataStream(auxInputFile)
            auxInputStream.setVersion(QDataStream.Qt_4_8)
            auxInputStream.setByteOrder(QDataStream.LittleEndian)
            auxInputStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

        if self.saveListSupplyVoltage:
            supplyFile = QFile(self.supplyFileName)
            if not supplyFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(supplyFile.errorString()) + "\n")
            supplyStream = QDataStream(supplyFile)
            supplyStream.setVersion(QDataStream.Qt_4_8)
            supplyStream.setByteOrder(QDataStream.LittleEndian)
            supplyStream.setFloatingPointPrecision(QDataStream.SinglePrecision)

        if self.saveListBoardAdc:
            adcInputFile = QFile(self.adcInputFileName)
            if not adcInputFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(adcInputFile.errorString()) + "\n")
            adcInputStream = QDataStream(adcInputFile)
            adcInputStream.setVersion(QDataStream.Qt_4_8)
            adcInputStream.setByteOrder(QDataStream.LittleEndian)
            adcInputStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

        if self.saveListBoardDigitalIn:
            digitalInputFile = QFile(self.digitalInputFileName)
            if not digitalInputFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(digitalInputFile.errorString()) + "\n")
            digitalInputStream = QDataStream(digitalInputFile)
            digitalInputStream.setVersion(QDataStream.Qt_4_8)
            digitalInputStream.setByteOrder(QDataStream.LittleEndian)
            digitalInputStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

        if saveTtlOut:
            digitalOutputFile = QFile(self.digitalOutputFileName)
            if not digitalOutputFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(digitalOutputFile.errorString()) + "\n")
            digitalOutputStream = QDataStream(digitalOutputFile)
            digitalOutputStream.setVersion(QDataStream.Qt_4_8)
            digitalOutputStream.setByteOrder(QDataStream.LittleEndian)
            digitalOutputStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

    # Close timestamp save file.
    def closeTimestampFile(self):
        self.timestampFile.close()

    # Close data files for "One File Per Signal Type" format.
    def closeSignalTypeFiles(self):
        if self.amplifierFile:
            self.amplifierFile.close()

        if self.auxInputFile:
            self.auxInputFile.close()

        if self.supplyFile:
            self.supplyFile.close()

        if self.adcInputFile:
            self.adcInputFile.close()

        if self.digitalInputFile:
            self.digitalInputFile.close()

        if self.digitalOutputFile:
            self.digitalOutputFile.close()

    # Create filenames (appended to the specified path) for each waveform.
    def createFilenames(self, signalSources, path):
        for port in range(len(signalSources.signalPort)):
            for index in range(signalSources.signalPort[port].numChannels()):
                currentChannel = signalSources.signalPort[port].channelByNativeOrder(
                    index)
                # Only create filenames for enabled channels.
                if currentChannel.enabled:
                    if currentChannel.signalType == constants.AmplifierSignal:
                        currentChannel.saveFileName = path + "/" + "amp-" + \
                            currentChannel.nativeChannelName + ".dat"
                    if currentChannel.signalType == constants.AuxInputSignal:
                        currentChannel.saveFileName = path + "/" + "aux-" + \
                            currentChannel.nativeChannelName + ".dat"
                    if currentChannel.signalType == constants.SupplyVoltageSignal:
                        currentChannel.saveFileName = path + "/" + "vdd-" + \
                            currentChannel.nativeChannelName + ".dat"
                    if currentChannel.signalType == constants.BoardAdcSignal:
                        currentChannel.saveFileName = path + "/" + "board-" + \
                            currentChannel.nativeChannelName + ".dat"
                    if currentChannel.signalType == constants.BoardDigInSignal:
                        currentChannel.saveFileName = path + "/" + "board-" + \
                            currentChannel.nativeChannelName + ".dat"
                    if currentChannel.signalType == constants.BoardDigOutSignal:
                        currentChannel.saveFileName = path + "/" + "board-" + \
                            currentChannel.nativeChannelName + ".dat"

    # Open individual save data files for all enabled waveforms.
    def openSaveFiles(self, signalSources):
        for port in range(len(signalSources.signalPort)):
            for index in range(signalSources.signalPort[port].numChannels()):
                currentChannel = signalSources.signalPort[port].channelByNativeOrder(
                    index)
                # Only open files for enabled channels.
                if currentChannel.enabled:
                    currentChannel.saveFile = QFile(
                        currentChannel.saveFileName)

                    if not currentChannel.saveFile.open(QIODevice.WriteOnly):
                        print("Cannot open file for writing: " +
                              str(currentChannel.saveFile.errorString()) + "\n")

                    currentChannel.saveStream = QDataStream(
                        currentChannel.saveFile)
                    currentChannel.saveStream.setVersion(QDataStream.Qt_4_8)

                    # Set to little endian mode for compatibilty with MATLAB,
                    # which is little endian on all platforms
                    currentChannel.saveStream.setByteOrder(
                        QDataStream.LittleEndian)

                    # Write 4-byte floating-point numbers (instead of the default 8-byte numbers)
                    # to save disk space.
                    currentChannel.saveStream.setFloatingPointPrecision(
                        QDataStream.SinglePrecision)

    # Close individual save data files for all enabled waveforms.
    def closeSaveFiles(self, signalSources):
        for port in range(len(signalSources.signalPort)):
            for index in range(signalSources.signalPort[port].numChannels()):
                currentChannel = signalSources.signalPort[port].channelByNativeOrder(
                    index)
                # Only close files for enabled channels.
                if currentChannel.enabled:
                    currentChannel.saveFile.close()

    # Reads numBlocks blocks of raw USB data stored in a queue of Rhd2000DataBlock
    # objects, loads this data into this SignalProcessor object, scaling the raw
    # data to generate waveforms with units of volts or microvolts.
    #
    # If lookForTrigger is True, this function looks for a trigger on digital input
    # triggerChannel with triggerPolarity.  If trigger is found, triggerTimeIndex
    # returns timestamp of trigger point.  Otherwise, triggerTimeIndex returns -1,
    # indicating no trigger was found.
    #
    # If saveToDisk is True, a disk-format binary datastream is written to QDataStream out.
    # If saveTemp is True, temperature readings are also saved.  A timestampOffset can be
    # used to reference the trigger point to zero.
    #
    # Returns number of bytes written to binary datastream out if saveToDisk == True.
    
    def loadAmplifierData(self, dataQueue, numBlocks, lookForTrigger, triggerChannel, triggerPolarity, triggerTimeIndex, addToBuffer, bufferQueue, saveToDisk, out, saveFormat, saveTemp, saveTtlOut, timestampOffset):
        indexSupply = 0
        numWordsWritten = 0

        triggerFound = False
        AnalogTriggerThreshold = 1.65

        for i in range(len(self.saveListAmplifier)):
            bufferArrayIndex[i] = 0

        if lookForTrigger:
            triggerTimeIndex = -1

        for block in range(numBlocks):

            # Load and scale RHD2000 amplifier waveforms
            # (sampled at amplifier sampling rate)

            front_ = dataQueue.front()
            for stream in range(self.numDataStreams):
                stream_ = front_.amplifierData[stream]
                for channel in range(32):
                    channel_ = stream_[channel]
                    preFilter_ = self.amplifierPreFilter[stream][channel]
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        # Amplifier waveform units = microvolts
                        preFilter_[t] = 0.195 * (channel_[t] - 32768)

            #TODO(br): Note the index on stream_
            # Load and scale RHD2000 auxiliary input waveforms
            # (sampled at 1/4 amplifier sampling rate)
            front_ = dataQueue.front()
            for stream in range(self.numDataStreams):
                stream_ = front_.auxiliaryData[stream]
                for t in range(0, constants.SAMPLES_PER_DATA_BLOCK, 4):
                    # Auxiliary input waveform units = volts
                    self.auxChannel[stream][0][t] = 0.0000374 * stream_[1][t + 1]
                    self.auxChannel[stream][1][t] = 0.0000374 * stream_[1][t + 2]
                    self.auxChannel[stream][2][t] = 0.0000374 * stream_[1][t + 3]

            # Load and scale RHD2000 supply voltage and temperature sensor waveforms
            # (sampled at 1/60 amplifier sampling rate)
            front_ = dataQueue.front()
            for stream in range(self.numDataStreams):
                stream_ = front_.auxiliaryData[stream]
                # Supply voltage waveform units = volts
                self.supplyVoltage[stream][indexSupply] = 0.0000748 * stream_[1][28]
                # Temperature sensor waveform units = degrees C
                self.tempRaw[stream] = (stream_[1][20] - stream_[1][12]) / 98.9 - 273.15

            indexSupply += 1

            # Average multiple temperature readings to improve accuracy
            self.tempHistoryPush(self.tempRaw)
            self.tempHistoryCalcAvg()

            # Load and scale USB interface board ADC waveforms
            # (sampled at amplifier sampling rate)
            front_ = dataQueue.front()
            for channel in range(8):
                channel_ = front_.boardAdcData[channel]
                target_ = self.boardAdc[channel]
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    # ADC waveform units = volts
                    target_[t] = 0.000050354 * channel_[t]

            if lookForTrigger and not triggerFound and triggerChannel >= 16:
                adc_ = self.boardAdc[triggerChannel - 16]
                if triggerPolarity:
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):            
                        # Trigger on logic low
                        if adc_[t] < AnalogTriggerThreshold:
                            triggerTimeIndex = front_.timeStamp[t]
                            triggerFound = True

                else:
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        # Trigger on logic high
                        if adc_[t] >= AnalogTriggerThreshold:
                            triggerTimeIndex = front_.timeStamp[t]
                            triggerFound = True

            # Load USB interface board digital input and output waveforms
            front_ = dataQueue.front()
            for channel in range(16):
                ttlIn_ = front_.ttlIn
                ttlOut_ = front_.ttlOut
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    self.boardDigIn[channel][t] = (
                        ttlIn_[t] & (1 << channel)) != 0
                    self.boardDigOut[channel][t] = (
                        ttlOut_[t] & (1 << channel)) != 0

            
            if lookForTrigger and not triggerFound and triggerChannel < 16:
                digIn_ = self.boardDigIn[triggerChannel]
                if triggerPolarity:
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        # Trigger on logic low
                        if digIn_[t] == 0:
                            triggerTimeIndex = front_.timeStamp[t]
                            triggerFound = True

                else:
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        # Trigger on logic high
                        if digIn_[t] == 1:
                            triggerTimeIndex = front_.timeStamp[t]
                            triggerFound = True

            # Optionally send binary data to binary output stream
            if saveToDisk:
                if saveFormat == constants.SaveFormatIntan:
                    # Save timestamp data
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQint32 = dataQueue.front(
                        ).timeStamp[t] - timestampOffset
                        # Save qint 32 in little-endian format
                        dataStreamBuffer[bufferIndex] = tempQint32 & 0x000000ff
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0x0000ff00) >> 8
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0x00ff0000) >> 16
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0xff000000) >> 24
                        bufferIndex += 1

                    # Stream out all data at once to speed writing
                    out.writeRawData(dataStreamBuffer, bufferIndex)
                    numWordsWritten += 2 * constants.SAMPLES_PER_DATA_BLOCK

                    # Save amplifier data
                    bufferIndex = 0
                    for i in range(len(self.saveListAmplifier)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            tempQuint16 = dataQueue.front(
                            ).amplifierData[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][t]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                    # Stream out all data at once to speed writing
                    out.writeRawData(dataStreamBuffer, bufferIndex)
                    numWordsWritten += len(self.saveListAmplifier) * \
                        constants.SAMPLES_PER_DATA_BLOCK

                    # Save auxiliary input data
                    bufferIndex = 0
                    for i in range(len(self.saveListAuxInput)):
                        for t in range(0, constants.SAMPLES_PER_DATA_BLOCK, 4):
                            tempQuint16 = dataQueue.front(
                            ).auxiliaryData[self.saveListAuxInput[i].boardStream][1][t + self.saveListAuxInput[i].chipChannel + 1]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                    # Stream out all data at once to speed writing
                    out.writeRawData(dataStreamBuffer, bufferIndex)
                    numWordsWritten += len(self.saveListAuxInput) * \
                        constants.SAMPLES_PER_DATA_BLOCK

                    # Save supply voltage data
                    for i in range(len(self.saveListSupplyVoltage)):
                        out.writeUInt16(
                            dataQueue.front().auxiliaryData[self.saveListSupplyVoltage[i].boardStream][1][28])
                        numWordsWritten += 1

                    # Save temperature sensor data if saveTemp == True
                    # Save as temperature in degrees C, multiplied by 100 and rounded to the nearest
                    # signed integer.
                    if saveTemp:
                        for i in range(len(self.saveListTempSensor)):
                            out.writeUInt16(
                                100.0 * self.tempAvg[self.saveListTempSensor[i].boardStream])
                            numWordsWritten += 1

                    # Save board ADC data
                    bufferIndex = 0
                    for i in range(len(self.saveListBoardAdc)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            tempQuint16 = dataQueue.front(
                            ).boardAdcData[self.saveListBoardAdc[i].nativeChannelNumber][t]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                    # Stream out all data at once to speed writing
                    out.writeRawData(dataStreamBuffer, bufferIndex)
                    numWordsWritten += len(self.saveListBoardAdc) * \
                        constants.SAMPLES_PER_DATA_BLOCK

                    # Save board digital input data
                    if self.saveListBoardDigIn:
                        # If ANY digital inputs are enabled, we save ALL 16 channels, since
                        # we are writing 16-bit chunks of data.
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            out.writeUInt16(dataQueue.front().ttlIn[t])
                            numWordsWritten += 1

                    # Save board digital output data, if saveTtlOut = True
                    if saveTtlOut:
                        # Save all 16 channels, since we are writing 16-bit chunks of data.
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            out.writeUInt16(dataQueue.front().ttlOut[t])
                            numWordsWritten += 1

                elif saveFormat == constants.SaveFormatFilePerSignalType:
                    # Save timestamp data
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQint32 = dataQueue.front(
                        ).timeStamp[t] - timestampOffset
                        # Save qint 32 in little-endian format
                        dataStreamBuffer[bufferIndex] = tempQint32 & 0x000000ff
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0x0000ff00) >> 8
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0x00ff0000) >> 16
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0xff000000) >> 24
                        bufferIndex += 1

                    # Stream out all data at once to speed writing
                    self.timestampStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += 2 * constants.SAMPLES_PER_DATA_BLOCK

                    # Save amplifier data
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        for i in range(len(self.saveListAmplifier)):
                            tempQint16 = dataQueue.front(
                            ).amplifierData[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][t] - 32768
                            # Save qint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQint16 & 0xff00) >> 8
                            bufferIndex += 1

                    if bufferIndex > 0:
                        # Stream out all data at once to speed writing
                        self.amplifierStream.writeRawData(
                            dataStreamBuffer, bufferIndex)
                        numWordsWritten += len(self.saveListAmplifier) * \
                            constants.SAMPLES_PER_DATA_BLOCK

                    # Save auxiliary input data
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tAux = 4 * math.floor(t / 4.0)
                        for i in range(len(self.saveListAuxInput)):
                            tempQuint16 = dataQueue.front(
                            ).auxiliaryData[self.saveListAuxInput[i].boardStream][1][tAux + self.saveListAuxInput[i].chipChannel + 1]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                    if bufferIndex > 0:
                        # Stream out all data at once to speed writing
                        self.auxInputStream.writeRawData(
                            dataStreamBuffer, bufferIndex)
                        numWordsWritten += len(self.saveListAuxInput) * \
                            constants.SAMPLES_PER_DATA_BLOCK

                    # Save supply voltage data
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        for i in range(len(self.saveListSupplyVoltage)):
                            tempQuint16 = dataQueue.front(
                            ).auxiliaryData[self.saveListSupplyVoltage[i].boardStream][1][28]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                    if bufferIndex > 0:
                        # Stream out all data at once to speed writing
                        self.supplyStream.writeRawData(
                            dataStreamBuffer, bufferIndex)
                        numWordsWritten += len(self.saveListSupplyVoltage) * \
                            constants.SAMPLES_PER_DATA_BLOCK

                    # Not saving temperature data in this save format.

                    # Save board ADC data
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        for i in range(len(self.saveListBoardAdc)):
                            tempQuint16 = dataQueue.front(
                            ).boardAdcData[self.saveListBoardAdc[i].nativeChannelNumber][t]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                    if bufferIndex > 0:
                        # Stream out all data at once to speed writing
                        self.adcInputStream.writeRawData(
                            dataStreamBuffer, bufferIndex)
                        numWordsWritten += len(self.saveListBoardAdc) * \
                            constants.SAMPLES_PER_DATA_BLOCK

                    # Save board digital input data
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        if self.saveListBoardDigIn:
                            # If ANY digital inputs are enabled, we save ALL 16 channels, since
                            # we are writing 16-bit chunks of data.
                            self.digitalInputStream.writeUInt16(
                                dataQueue.front().ttlIn[t])
                            numWordsWritten += 1

                    # Save board digital output data, if saveTtlOut = True
                    if saveTtlOut:
                        # Save all 16 channels, since we are writing 16-bit chunks of data.
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            self.digitalOutputStream.writeUInt16(
                                dataQueue.front().ttlOut[t])
                            numWordsWritten += 1

                elif saveFormat == constants.SaveFormatFilePerChannel:
                    # Save timestamp data
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQint32 = dataQueue.front(
                        ).timeStamp[t] - timestampOffset
                        # Save qint 32 in little-endian format
                        dataStreamBuffer[bufferIndex] = tempQint32 & 0x000000ff
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0x0000ff00) >> 8
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0x00ff0000) >> 16
                        bufferIndex += 1
                        dataStreamBuffer[bufferIndex] = (
                            tempQint32 & 0xff000000) >> 24
                        bufferIndex += 1

                    # Stream out all data at once to speed writing
                    self.timestampStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += 2 * constants.SAMPLES_PER_DATA_BLOCK

                    # Save amplifier data to dataStreamBufferArray In in effort to increase write speed we will
                    # collect amplifier data from all data blocks and then write all data at the end of this function.
                    for i in range(len(self.saveListAmplifier)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            tempQint16 = dataQueue.front(
                            ).amplifierData[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][t] - 32768
                            # Save qint16 in little-endian format (LSByte first)
                            dataStreamBufferArray[i][bufferArrayIndex[i]
                                                     ] = tempQint16 & 0x00ff
                            bufferArrayIndex[i] += 1
                            # (MSByte last)
                            dataStreamBufferArray[i][bufferArrayIndex[i]] = (
                                tempQint16 & 0xff00) >> 8
                            bufferArrayIndex[i] += 1

                        numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                    # Save auxiliary input data
                    for i in range(len(self.saveListAuxInput)):
                        bufferIndex = 0
                        for t in range(0, constants.SAMPLES_PER_DATA_BLOCK, 4):
                            # Aux data is sampled at 1/4 amplifier sampling rate write each sample 4 times
                            for j in range(4):
                                tempQuint16 = dataQueue.front(
                                ).auxiliaryData[self.saveListAuxInput[i].boardStream][1][t + self.saveListAuxInput[i].chipChannel + 1]
                                # Save quint16 in little-endian format (LSByte first)
                                dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                                bufferIndex += 1
                                # (MSByte last)
                                dataStreamBuffer[bufferIndex] = (
                                    tempQuint16 & 0xff00) >> 8
                                bufferIndex += 1

                        # Stream out all data at once to speed writing
                        self.saveListAuxInput[i].saveStream.writeRawData(
                            dataStreamBuffer, bufferIndex)
                        numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                    # Save supply voltage data
                    for i in range(len(self.saveListSupplyVoltage)):
                        bufferIndex = 0
                        # Vdd data is sampled at 1/60 amplifier sampling rate write each sample 60 times
                        for j in range(constants.SAMPLES_PER_DATA_BLOCK):
                            tempQuint16 = dataQueue.front(
                            ).auxiliaryData[self.saveListSupplyVoltage[i].boardStream][1][28]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                        self.saveListSupplyVoltage[i].saveStream.writeRawData(
                            dataStreamBuffer, bufferIndex)    # Stream out all data at once to speed writing
                        numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                    # Not saving temperature data in this save format.

                    # Save board ADC data
                    for i in range(len(self.saveListBoardAdc)):
                        bufferIndex = 0
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            tempQuint16 = dataQueue.front(
                            ).boardAdcData[self.saveListBoardAdc[i].nativeChannelNumber][t]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                        # Stream out all data at once to speed writing
                        self.saveListBoardAdc[i].saveStream.writeRawData(
                            dataStreamBuffer, bufferIndex)
                        numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                    # Save board digital input data
                    for i in range(len(self.saveListBoardDigitalIn)):
                        bufferIndex = 0
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            tempQuint16 = ((dataQueue.front().ttlIn[t] & (
                                1 << self.saveListBoardDigitalIn[i].nativeChannelNumber)) != 0)
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                        # (MSB of individual digital input will always be zero)
                        dataStreamBuffer[bufferIndex] = 0
                        bufferIndex += 1

                        self.saveListBoardDigitalIn[i].saveStream.writeRawData(
                            dataStreamBuffer, bufferIndex)    # Stream out all data at once to speed writing
                        numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                    # Save board digital output data, if saveTtlOut = True
                    if saveTtlOut:
                        for i in range(16):
                            bufferIndex = 0
                            for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                                tempQuint16 = (
                                    (dataQueue.front().ttlOut[t] & (1 << i)) != 0)
                                # Save quint16 in little-endian format (LSByte first)
                                dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                                bufferIndex += 1
                            # (MSB of individual digital input will always be zero)
                            dataStreamBuffer[bufferIndex] = 0
                            bufferIndex += 1

                            self.saveListBoardDigitalOut[i].saveStream.writeRawData(
                                dataStreamBuffer, bufferIndex)    # Stream out all data at once to speed writing
                            numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

            if addToBuffer:
                bufferQueue.push(dataQueue.front())

            # We are done with this Rhd2000DataBlock object remove it from dataQueue
            dataQueue.pop()

        # If we are operating on the "One File Per Channel" format, we have saved all amplifier data from
        # multiple data blocks in dataStreamBufferArray.  Now we write it all at once, for each channel.
        if saveToDisk and format == constants.SaveFormatFilePerChannel:
            for i in range(len(self.saveListAmplifier)):
                # Stream out all amplifier data at once to speed writing
                self.saveListAmplifier[i].saveStream.writeRawData(
                    dataStreamBufferArray[i], bufferArrayIndex[i])

        # Return total number of bytes written to binary output stream
        return 2 * numWordsWritten, triggerTimeIndex

    # Save to entire contents of the buffer queue to disk, and empty the queue in the process.
    # Returns number of bytes written to binary datastream out.
    def saveBufferedData(self, bufferQueue, out, saveFormat, saveTemp, saveTtlOut, timestampOffset):
        numWordsWritten = 0

        if saveFormat == constants.SaveFormatIntan:
            while not bufferQueue.empty():
                # Save timestamp data
                bufferIndex = 0
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    tempQint32 = bufferQueue.front(
                    ).timeStamp[t] - timestampOffset
                    # Save qint 32 in little-endian format
                    dataStreamBuffer[bufferIndex] = tempQint32 & 0x000000ff
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0x0000ff00) >> 8
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0x00ff0000) >> 16
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0xff000000) >> 24
                    bufferIndex += 1

                # Stream out all data at once to speed writing
                out.writeRawData(dataStreamBuffer, bufferIndex)
                numWordsWritten += 2 * constants.SAMPLES_PER_DATA_BLOCK

                # Save amplifier data
                bufferIndex = 0
                for i in range(len(self.saveListAmplifier)):
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQuint16 = bufferQueue.front(
                        ).amplifierData[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][t]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                # Stream out all data at once to speed writing
                out.writeRawData(dataStreamBuffer, bufferIndex)
                numWordsWritten += len(self.saveListAmplifier) * \
                    constants.SAMPLES_PER_DATA_BLOCK

                # Save auxiliary input data
                bufferIndex = 0
                for i in range(len(self.saveListAuxInput)):
                    for t in range(0, constants.SAMPLES_PER_DATA_BLOCK, 4):
                        tempQuint16 = bufferQueue.front(
                        ).auxiliaryData[self.saveListAuxInput[i].boardStream][1][t + self.saveListAuxInput[i].chipChannel + 1]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                # Stream out all data at once to speed writing
                out.writeRawData(dataStreamBuffer, bufferIndex)
                numWordsWritten += len(self.saveListAuxInput) * \
                    constants.SAMPLES_PER_DATA_BLOCK

                # Save supply voltage data
                for i in range(len(self.saveListSupplyVoltage)):
                    out.writeUInt16(
                        bufferQueue.front().auxiliaryData[self.saveListSupplyVoltage[i].boardStream][1][28])
                    numWordsWritten += 1

                # Save temperature sensor data if saveTemp == True
                # Save as temperature in degrees C, multiplied by 100 and rounded to the nearest
                # signed integer.
                if saveTemp:
                    # Load and scale RHD2000 supply voltage and temperature sensor waveforms
                    # (sampled at 1/60 amplifier sampling rate)

                    for stream in range(self.numDataStreams):
                        # Temperature sensor waveform units = degrees C
                        self.tempRaw[stream] = (bufferQueue.front().auxiliaryData[stream][1][20] -
                                                bufferQueue.front().auxiliaryData[stream][1][12]) / 98.9 - 273.15

                    # Average multiple temperature readings to improve accuracy
                    self.tempHistoryPush(self.tempRaw)
                    self.tempHistoryCalcAvg()

                    for i in range(len(self.saveListTempSensor)):
                        out.writeInt16(
                            100.0 * self.tempAvg[self.saveListTempSensor[i].boardStream])
                        numWordsWritten += 1

                # Save board ADC data
                bufferIndex = 0
                for i in range(len(self.saveListBoardAdc)):
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQuint16 = bufferQueue.front(
                        ).boardAdcData[self.saveListBoardAdc[i].nativeChannelNumber][t]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                # Stream out all data at once to speed writing
                out.writeRawData(dataStreamBuffer, bufferIndex)
                numWordsWritten += len(self.saveListBoardAdc) * \
                    constants.SAMPLES_PER_DATA_BLOCK

                # Save board digital input data
                if self.saveListBoardDigIn:
                    # If ANY digital inputs are enabled, we save ALL 16 channels, since
                    # we are writing 16-bit chunks of data.
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        out.writeUInt16(bufferQueue.front().ttlIn[t])
                        numWordsWritten += 1

                # Save board digital output data, is saveTtlOut = True
                if saveTtlOut:
                    # We save all 16 channels, since we are writing 16-bit chunks of data.
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        out.writeUInt16(bufferQueue.front().ttlOut[t])
                        numWordsWritten += 1

                # We are done with this Rhd2000DataBlock object remove it from bufferQueue
                bufferQueue.pop()

        elif saveFormat == constants.SaveFormatFilePerSignalType:
            while not bufferQueue.empty():
                # Save timestamp data
                bufferIndex = 0
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    tempQint32 = bufferQueue.front(
                    ).timeStamp[t] - timestampOffset
                    # Save qint 32 in little-endian format
                    dataStreamBuffer[bufferIndex] = tempQint32 & 0x000000ff
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0x0000ff00) >> 8
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0x00ff0000) >> 16
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0xff000000) >> 24
                    bufferIndex += 1

                # Stream out all data at once to speed writing
                self.timestampStream.writeRawData(
                    dataStreamBuffer, bufferIndex)
                numWordsWritten += 2 * constants.SAMPLES_PER_DATA_BLOCK

                # Save amplifier data
                bufferIndex = 0
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    for i in range(len(self.saveListAmplifier)):
                        tempQint16 = (bufferQueue.front(
                        ).amplifierData[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][t] - 32768)
                        # Save qint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQint16 & 0xff00) >> 8
                        bufferIndex += 1

                if bufferIndex > 0:
                    # Stream out all data at once to speed writing
                    self.amplifierStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += len(self.saveListAmplifier) * \
                        constants.SAMPLES_PER_DATA_BLOCK

                # Save auxiliary input data
                bufferIndex = 0
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    tAux = 4 * math.floor(t / 4.0)
                    for i in range(len(self.saveListAuxInput)):
                        tempQuint16 = bufferQueue.front(
                        ).auxiliaryData[self.saveListAuxInput[i].boardStream][1][tAux + self.saveListAuxInput[i].chipChannel + 1]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                if bufferIndex > 0:
                    # Stream out all data at once to speed writing
                    self.auxInputStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += len(self.saveListAuxInput) * \
                        constants.SAMPLES_PER_DATA_BLOCK

                # Save supply voltage data
                bufferIndex = 0
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    for i in range(len(self.saveListSupplyVoltage)):
                        tempQuint16 = bufferQueue.front(
                        ).auxiliaryData[self.saveListSupplyVoltage[i].boardStream][1][28]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                if (bufferIndex > 0):
                    # Stream out all data at once to speed writing
                    self.supplyStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += len(self.saveListSupplyVoltage) * \
                        constants.SAMPLES_PER_DATA_BLOCK

                # Not saving temperature data in this save format.

                # Save board ADC data
                bufferIndex = 0
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    for i in range(len(self.saveListBoardAdc)):
                        tempQuint16 = bufferQueue.front(
                        ).boardAdcData[self.saveListBoardAdc[i].nativeChannelNumber][t]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                if bufferIndex > 0:
                    # Stream out all data at once to speed writing
                    self.adcInputStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += len(self.saveListBoardAdc) * \
                        constants.SAMPLES_PER_DATA_BLOCK

                # Save board digital input data
                if self.saveListBoardDigIn:
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        # If ANY digital inputs are enabled, we save ALL 16 channels, since
                        # we are writing 16-bit chunks of data.
                        self.digitalInputStream.writeUInt16(
                            bufferQueue.front().ttlIn[t])
                        numWordsWritten += 1

                # Save board digital output data, if saveTtlOut = True
                if saveTtlOut:
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        # We save all 16 channels, since we are writing 16-bit chunks of data.
                        self.digitalOutputStream.writeUInt16(
                            bufferQueue.front().ttlOut[t])
                        numWordsWritten += 1

                # We are done with this Rhd2000DataBlock object remove it from bufferQueue
                bufferQueue.pop()

        if saveFormat == constants.SaveFormatFilePerChannel:
            while not bufferQueue.empty():
                # Save timestamp data
                bufferIndex = 0
                for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                    tempQint32 = bufferQueue.front(
                    ).timeStamp[t] - timestampOffset
                    # Save qint 32 in little-endian format
                    dataStreamBuffer[bufferIndex] = tempQint32 & 0x000000ff
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0x0000ff00) >> 8
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0x00ff0000) >> 16
                    bufferIndex += 1
                    dataStreamBuffer[bufferIndex] = (
                        tempQint32 & 0xff000000) >> 24
                    bufferIndex += 1

                # Stream out all data at once to speed writing
                self.timestampStream.writeRawData(
                    dataStreamBuffer, bufferIndex)
                numWordsWritten += 2 * constants.SAMPLES_PER_DATA_BLOCK

                # Save amplifier data
                for i in range(len(self.saveListAmplifier)):
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQint16 = (bufferQueue.front(
                        ).amplifierData[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][t] - 32768)
                        # Save qint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQint16 & 0xff00) >> 8
                        bufferIndex += 1

                    # Stream out all data at once to speed writing
                    self.saveListAmplifier[i].saveStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                # Save auxiliary input data
                for i in range(len(self.saveListAuxInput)):
                    bufferIndex = 0
                    for t in range(0, constants.SAMPLES_PER_DATA_BLOCK, 4):
                            # Aux data is sampled at 1/4 amplifier sampling rate write each sample 4 times
                        for j in range(4):
                            tempQuint16 = bufferQueue.front(
                            ).auxiliaryData[self.saveListAuxInput[i].boardStream][1][t + self.saveListAuxInput[i].chipChannel + 1]
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSByte last)
                            dataStreamBuffer[bufferIndex] = (
                                tempQuint16 & 0xff00) >> 8
                            bufferIndex += 1

                    # Stream out all data at once to speed writing
                    self.saveListAuxInput[i].saveStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                # Save supply voltage data
                for i in range(len(self.saveListSupplyVoltage)):
                    bufferIndex = 0
                    # Vdd data is sampled at 1/60 amplifier sampling rate write each sample 60 times
                    for j in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQuint16 = bufferQueue.front(
                        ).auxiliaryData[self.saveListSupplyVoltage[i].boardStream][1][28]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                    self.saveListSupplyVoltage[i].saveStream.writeRawData(
                        dataStreamBuffer, bufferIndex)    # Stream out all data at once to speed writing
                    numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                # Not saving temperature data in this save format.

                # Save board ADC data
                for i in range(len(self.saveListBoardAdc)):
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQuint16 = bufferQueue.front(
                        ).boardAdcData[self.saveListBoardAdc[i].nativeChannelNumber][t]
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSByte last)
                        dataStreamBuffer[bufferIndex] = (
                            tempQuint16 & 0xff00) >> 8
                        bufferIndex += 1

                    # Stream out all data at once to speed writing
                    self.saveListBoardAdc[i].saveStream.writeRawData(
                        dataStreamBuffer, bufferIndex)
                    numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                # Save board digital input data
                for i in range(len(self.saveListBoardDigitalIn)):
                    bufferIndex = 0
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        tempQuint16 = ((bufferQueue.front().ttlIn[t] & (
                            1 << self.saveListBoardDigitalIn[i].nativeChannelNumber)) != 0)
                        # Save quint16 in little-endian format (LSByte first)
                        dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                        bufferIndex += 1
                        # (MSB of individual digital input will always be zero)
                        dataStreamBuffer[bufferIndex] = 0
                        bufferIndex += 1

                    self.saveListBoardDigitalIn[i].saveStream.writeRawData(
                        dataStreamBuffer, bufferIndex)    # Stream out all data at once to speed writing
                    numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                # Save board digital output data, if saveTtlOut = True
                if saveTtlOut:
                    for i in range(16):
                        bufferIndex = 0
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            tempQuint16 = (
                                (bufferQueue.front().ttlOut[t] & (1 << i)) != 0)
                            # Save quint16 in little-endian format (LSByte first)
                            dataStreamBuffer[bufferIndex] = tempQuint16 & 0x00ff
                            bufferIndex += 1
                            # (MSB of individual digital input will always be zero)
                            dataStreamBuffer[bufferIndex] = 0
                            bufferIndex += 1

                        self.saveListBoardDigitalOut[i].saveStream.writeRawData(
                            dataStreamBuffer, bufferIndex)    # Stream out all data at once to speed writing
                        numWordsWritten += constants.SAMPLES_PER_DATA_BLOCK

                # We are done with this Rhd2000DataBlock object remove it from bufferQueue
                bufferQueue.pop()

        # Return total number of bytes written to binary output stream
        return (2 * numWordsWritten)

    # This function behaves similarly to loadAmplifierData, but generates
    # synthetic neural or ECG data for demonstration purposes when there is
    # no USB interface board present.
    # Returns number of bytes written to binary datastream out if saveToDisk == True.
    def loadSyntheticData(self, numBlocks, sampleRate, saveToDisk, out, saveFormat, saveTemp, saveTtlOut):
        indexSupply = 0
        indexDig = 0
        numWordsWritten = 0

        tStepMsec = 1000.0 / sampleRate

        # If the sample rate is 5 kS/s or higher, generate synthetic neural data
        # otherwise, generate synthetic ECG data.
        if sampleRate > 4999.9:
            # Generate synthetic neural data.
            for block in range(numBlocks):
                for stream in range(self.numDataStreams):
                    for channel in range(32):
                        spikePresent = False
                        spikeNum = 0
                        if random.random() < self.synthRelativeSpikeRate[stream][channel] * tStepMsec:
                            spikePresent = True
                            # add some random time jitter
                            spikeDelay = random.uniform(0.0, 0.3)
                            # choose between one of two spike types
                            if random.random() < 0.3:
                                spikeNum = 1

                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            # Create realistic background Gaussian noise of 2.4 uVrms (would be more in cortex)
                            self.amplifierPreFilter[stream][channel][constants.SAMPLES_PER_DATA_BLOCK *
                                                                     block + t] = 2.4 * random.normal(0, 1)
                            if spikePresent:
                                # Create synthetic spike
                                if t * tStepMsec > spikeDelay and t * tStepMsec < self.synthSpikeDuration[stream][channel][spikeNum] + spikeDelay:
                                    self.amplifierPreFilter[stream][channel][constants.SAMPLES_PER_DATA_BLOCK * block + t] += self.synthSpikeAmplitude[stream][channel][spikeNum] * math.exp(-2.0 * (
                                        t * tStepMsec - spikeDelay)) * math.sin(2.0 * math.pi * (t * tStepMsec - spikeDelay) / self.synthSpikeDuration[stream][channel][spikeNum])

        else:
            # Generate synthetic ECG data.
            for t in range(constants.SAMPLES_PER_DATA_BLOCK * numBlocks):
                # Piece together half sine waves to model QRS complex, P wave, and T wave
                if self.tPulse < 80.0:
                    # P wave
                    ecgValue = 40.0 * \
                        math.sin(2.0 * math.pi * self.tPulse / 160.0)
                elif self.tPulse > 100.0 and self.tPulse < 120.0:
                    ecgValue = -250.0 * \
                        math.sin(2.0 * math.pi *
                                 (self.tPulse - 100.0) / 40.0)  # Q
                elif self.tPulse > 120.0 and self.tPulse < 180.0:
                    ecgValue = 1000.0 * \
                        math.sin(2.0 * math.pi *
                                 (self.tPulse - 120.0) / 120.0)  # R
                elif self.tPulse > 180.0 and self.tPulse < 260.0:
                    ecgValue = -120.0 * \
                        math.sin(2.0 * math.pi *
                                 (self.tPulse - 180.0) / 160.0)  # S
                elif self.tPulse > 340.0 and self.tPulse < 400.0:
                    ecgValue = 60.0 * \
                        math.sin(2.0 * math.pi *
                                 (self.tPulse - 340.0) / 120.0)  # T wave
                else:
                    ecgValue = 0.0

                for stream in range(self.numDataStreams):
                    for channel in range(32):
                        # Multiply basic ECG waveform by channel-specific amplitude, and
                        # add 2.4 uVrms noise.
                        self.amplifierPreFilter[stream][channel][t] = self.synthEcgAmplitude[stream][channel] * \
                            ecgValue + 2.4 * random.gauss(0, 1)

                self.tPulse += tStepMsec

        # Repeat ECG waveform with regular period.
        if self.tPulse > 840.0:
            self.tPulse = 0.0

        for block in range(numBlocks):
            # Generate synthetic auxiliary input data.
            for t in range(0, constants.SAMPLES_PER_DATA_BLOCK, 4):
                for stream in range(self.numDataStreams):
                    # Just use DC values.
                    self.auxChannel[stream][0][t] = 0.5
                    self.auxChannel[stream][1][t] = 1.0
                    self.auxChannel[stream][2][t] = 2.0

            # Generate synthetic supply voltage and temperature data.
            for stream in range(self.numDataStreams):
                self.supplyVoltage[stream][indexSupply] = 3.3
                self.tempRaw[stream] = 25.0

            indexSupply += 1

            # Average multiple temperature readings to improve accuracy
            self.tempHistoryPush(self.tempRaw)
            self.tempHistoryCalcAvg()

            # Generate synthetic USB interface board ADC data.
            for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                for channel in range(8):
                    self.boardAdc[channel][t] = 0.0

            # Generate synthetic USB interface board digital I/O data.
            for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                for channel in range(16):
                    self.boardDigIn[channel][indexDig] = 0
                    self.boardDigOut[channel][indexDig] = 0

                indexDig += 1

        # Optionally send binary data to binary output stream
        if saveToDisk:
            if saveFormat == constants.SaveFormatIntan:
                for block in range(numBlocks):
                    # Save timestamp data
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        out.writeInt32(self.synthTimeStamp)
                        self.synthTimeStamp += 1
                        numWordsWritten += 2

                    # Save amplifier data
                    for i in range(len(self.saveListAmplifier)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            out.writeUInt16((self.amplifierPreFilter[self.saveListAmplifier[i].boardStream]
                                             [self.saveListAmplifier[i].chipChannel][60 * block + t] / 0.195) + 32768)
                            numWordsWritten += 1

                    # Save auxiliary input data
                    for i in range(len(self.saveListAuxInput)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK / 4):
                            out.writeUInt16(self.auxChannel[self.saveListAuxInput[i].boardStream]
                                            [self.saveListAuxInput[i].chipChannel][15 * block + t] / 0.0000374)
                            numWordsWritten += 1

                    # Save supply voltage data
                    for i in range(len(self.saveListSupplyVoltage)):
                        out.writeUInt16(
                            self.supplyVoltage[self.saveListSupplyVoltage[i].boardStream][block] / 0.0000748)
                        numWordsWritten += 1

                    # Save temperature sensor data if saveTemp == True
                    # Save as temperature in degrees C, multiplied by 100 and rounded to the nearest
                    # signed integer.
                    if saveTemp:
                        for i in range(len(self.saveListTempSensor)):
                            out.writeInt16(
                                100.0 * self.tempAvg[self.saveListTempSensor[i].boardStream])
                            numWordsWritten += 1

                    # Save board ADC data
                    for i in range(len(self.saveListBoardAdc)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            out.writeUInt16(0)
                            numWordsWritten += 1

                    # Save board digital input data
                    if self.saveListBoardDigIn:
                        # If ANY digital inputs are enabled, we save ALL 16 channels, since
                        # we are writing 16-bit chunks of data.
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            out.writeUInt16(0)
                            numWordsWritten += 1

                    # Save board digital output data
                    if saveTtlOut:
                        # We save all 16 channels, since we are writing 16-bit chunks of data.
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            out.writeUInt16(0)
                            numWordsWritten += 1

            elif saveFormat == constants.SaveFormatFilePerSignalType:
                for block in range(numBlocks):
                    # Save timestamp data
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        self.timestampStream.writeInt32(self.synthTimeStamp)
                        self.synthTimeStamp += 1
                        numWordsWritten += 2

                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        # Save amplifier data
                        for i in range(len(self.saveListAmplifier)):
                            self.amplifierStream.writeInt16(
                                self.amplifierPreFilter[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][60 * block + t] / 0.195)
                            numWordsWritten += 1

                        # Save auxiliary input data
                        tAux = math.floor(t / 4.0)
                        for i in range(len(self.saveListAuxInput)):
                            self.auxInputStream.writeUInt16(
                                self.auxChannel[self.saveListAuxInput[i].boardStream][self.saveListAuxInput[i].chipChannel][15 * block + tAux] / 0.0000374)
                            numWordsWritten += 1

                        # Save supply voltage data
                        for i in range(len(self.saveListSupplyVoltage)):
                            self.supplyStream.writeUInt16(
                                self.supplyVoltage[self.saveListSupplyVoltage[i].boardStream][block] / 0.0000748)
                            numWordsWritten += 1

                        # Not saving temperature data in this save format.

                        # Save board ADC data
                        for i in range(len(self.saveListBoardAdc)):
                            self.adcInputStream.writeUInt16(0)
                            numWordsWritten += 1

                        # Save board digital input data
                        if self.saveListBoardDigIn:
                            self.digitalInputStream.writeUInt16(0)
                            numWordsWritten += 1

                        # Save board digital output data
                        if saveTtlOut:
                            self.digitalOutputStream.writeUInt16(0)
                            numWordsWritten += 1

            elif saveFormat == constants.SaveFormatFilePerChannel:
                for block in range(numBlocks):
                    # Save timestamp data
                    for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                        self.timestampStream.writeInt32(self.synthTimeStamp)
                        self.synthTimeStamp += 1
                        numWordsWritten += 2

                    # Save amplifier data
                    for i in range(len(self.saveListAmplifier)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            self.saveListAmplifier[i].saveStream.writeInt16(
                                self.amplifierPreFilter[self.saveListAmplifier[i].boardStream][self.saveListAmplifier[i].chipChannel][60 * block + t] / 0.195)
                            numWordsWritten += 1

                    # Save auxiliary input data
                    for i in range(len(self.saveListAuxInput)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK / 4):
                            # Aux data is sampled at 1/4 amplifier sampling rate write each sample 4 times
                            for j in range(4):
                                self.saveListAuxInput[i].saveStream.writeUInt16(
                                    self.auxChannel[self.saveListAuxInput[i].boardStream][self.saveListAuxInput[i].chipChannel][15 * block + t] / 0.0000374)
                                numWordsWritten += 1

                    # Save supply voltage data
                    for i in range(len(self.saveListSupplyVoltage)):
                        # Vdd data is sampled at 1/60 amplifier sampling rate write each sample 60 times
                        for j in range(constants.SAMPLES_PER_DATA_BLOCK):
                            self.saveListSupplyVoltage[i].saveStream.writeUInt16(
                                self.supplyVoltage[self.saveListSupplyVoltage[i].boardStream][block] / 0.0000748)
                            numWordsWritten += 1

                    # Not saving temperature data in this save format.

                    # Save board ADC data
                    for i in range(len(self.saveListBoardAdc)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            self.saveListBoardAdc[i].saveStream.writeUInt16(0)
                            numWordsWritten += 1

                    # Save board digital input data
                    for i in range(len(self.saveListBoardDigitalIn)):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            self.saveListBoardDigitalIn[i].saveStream.writeUInt16(
                                0)
                            numWordsWritten += 1

                    # Save board digital output data
                    for i in range(16):
                        for t in range(constants.SAMPLES_PER_DATA_BLOCK):
                            self.saveListBoardDigitalOut[i].saveStream.writeUInt16(
                                0)
                            numWordsWritten += 1

        # Return total number of bytes written to binary output stream
        return 2 * numWordsWritten

    # Set notch filter parameters.  All filter parameters are given in Hz (or
    # in Samples/s).  A bandwidth of 10 Hz is recommended for 50 or 60 Hz notch
    # filters.  Narrower bandwidths will produce extended ringing in the time
    # domain in response to large transients.
    def setNotchFilter(self, notchFreq, bandwidth, sampleFreq):
        d = math.exp(-math.pi * bandwidth / sampleFreq)

        # Calculate biquad IIR filter coefficients.
        self.a1 = -(1.0 + d * d) * math.cos(2.0 *
                                            math.pi * notchFreq / sampleFreq)
        self.a2 = d * d
        self.b0 = (1 + d * d) / 2.0
        self.b1 = self.a1
        self.b2 = self.b0

    # Enables or disables amplifier waveform notch filter.
    def setNotchFilterEnabled(self, enable):
        self.notchFilterEnabled = enable

    # Set highpass filter parameters.  All filter parameters are given in Hz (or
    # in Samples/s).
    def setHighpassFilter(self, cutoffFreq, sampleFreq):
        self.aHpf = math.exp(-1.0 * 2.0 * math.pi * cutoffFreq / sampleFreq)
        self.bHpf = 1.0 - self.aHpf

    # Enables or disables amplifier waveform highpass filter.
    def setHighpassFilterEnabled(self, enable):
        self.highpassFilterEnabled = enable

    # Runs notch filter only on amplifier channels that are visible
    # on the display (according to channelVisible).
    def filterData(self, numBlocks, channelVisible):
        length = constants.SAMPLES_PER_DATA_BLOCK * numBlocks

        # Note: Throughout this function, and elsewhere in this source code, we access
        # multidimensional 'QVector' containers using the at() function, so instead of
        # writing:
        #            x = my3dQVector[i][j][k]
        # we write:
        #            x = my3dQVector[i].at(j).at(k)
        #
        # Web research suggests that using at() instead of [] to access the contents
        # of a multidimensional QVector results in faster code, and some preliminary
        # experiments at Intan bear this out.  Web research also suggests that the
        # opposite could be True of C++ STL (non-Qt) 'vector' containers, so some
        # experimentation may be needed to optimize the runtime performance of code.

        if self.notchFilterEnabled:
            for stream in range(self.numDataStreams):
                for channel in range(32):
                    if channelVisible[stream][channel]:
                        # Execute biquad IIR notch filter.  The filter "looks backwards" two timesteps,
                        # so we must use the prevAmplifierPreFilter and prevAmplifierPostFilter
                        # variables to store the last two samples from the previous block of
                        # waveform data so that the filter works smoothly across the "seams".
                        self.amplifierPostFilter[stream][channel][0] = self.b2 * self.prevAmplifierPreFilter[stream][channel][0] + self.b1 * self.prevAmplifierPreFilter[stream][channel][1] + \
                            self.b0 * self.amplifierPreFilter[stream][channel][0] - self.a2 * \
                            self.prevAmplifierPostFilter[stream][channel][0] - \
                            self.a1 * \
                            self.prevAmplifierPostFilter[stream][channel][1]
                        self.amplifierPostFilter[stream][channel][1] = self.b2 * self.prevAmplifierPreFilter[stream][channel][1] + self.b1 * self.amplifierPreFilter[stream][channel][0] + \
                            self.b0 * self.amplifierPreFilter[stream][channel][1] - self.a2 * \
                            self.prevAmplifierPostFilter[stream][channel][1] - \
                            self.a1 * \
                            self.amplifierPostFilter[stream][channel][0]
                        for t in range(2, length):
                            self.amplifierPostFilter[stream][channel][t] = self.b2 * self.amplifierPreFilter[stream][channel][t-2] + self.b1 * self.amplifierPreFilter[stream][channel][t-1] + self.b0 * \
                                self.amplifierPreFilter[stream][channel][t] - self.a2 * self.amplifierPostFilter[stream][channel][t -
                                                                                                                                  2] - self.a1 * self.amplifierPostFilter[stream][channel][t-1]
        else:
            # If the notch filter is disabled, simply copy the data without filtering.
            for stream in range(self.numDataStreams):
                for channel in range(32):
                    if channelVisible[stream][channel]:
                        for t in range(length):
                            self.amplifierPostFilter[stream][channel][t] = self.amplifierPreFilter[stream][channel][t]

        # Save the last two data points from each waveform to use in successive IIR filter
        # calculations.
        for stream in range(self.numDataStreams):
            for channel in range(32):
                self.prevAmplifierPreFilter[stream][channel][0] = self.amplifierPreFilter[stream][channel][length - 2]
                self.prevAmplifierPreFilter[stream][channel][1] = self.amplifierPreFilter[stream][channel][length - 1]
                self.prevAmplifierPostFilter[stream][channel][0] = self.amplifierPostFilter[stream][channel][length - 2]
                self.prevAmplifierPostFilter[stream][channel][1] = self.amplifierPostFilter[stream][channel][length - 1]

        # Apply first-order high-pass filter, if selected
        if self.highpassFilterEnabled:
            for stream in range(self.numDataStreams):
                for channel in range(32):
                    if channelVisible[stream][channel]:
                        for t in range(length):
                            temp = self.amplifierPostFilter[stream][channel][t]
                            self.amplifierPostFilter[stream][channel][t] -= self.highpassFilterState[stream][channel]
                            self.highpassFilterState[stream][channel] = self.aHpf * \
                                self.highpassFilterState[stream][channel] + \
                                self.bHpf * temp

    # Return the magnitude and phase (in degrees) of a selected frequency component (in Hz)
    # for a selected amplifier channel on the selected USB data stream.
    def measureComplexAmplitude(self, measuredMagnitude, measuredPhase, capIndex, stream, chipChannel, numBlocks, sampleRate, frequency, numPeriods):
        period = round(sampleRate / frequency)
        startIndex = 0
        endIndex = startIndex + numPeriods * period - 1

        # Move the measurement window to the end of the waveform to ignore start-up transient.
        while endIndex < constants.SAMPLES_PER_DATA_BLOCK * numBlocks - period:
            startIndex += period
            endIndex += period

        # Measure real (iComponent) and imaginary (qComponent) amplitude of frequency component.
        iComponent, qComponent = self.amplitudeOfFreqComponent(self.amplifierPreFilter[stream][chipChannel],
                                                               startIndex, endIndex, sampleRate, frequency)
        # Calculate magnitude and phase from real (I) and imaginary (Q) components.
        measuredMagnitude[stream][chipChannel][capIndex] = math.sqrt(
            iComponent * iComponent + qComponent * qComponent)
        measuredPhase[stream][chipChannel][capIndex] = constants.RADIANS_TO_DEGREES * \
            math.atan2(qComponent, iComponent)

    # Returns the real and imaginary amplitudes of a selected frequency component in the vector
    # data, between a start index and end index.
    def amplitudeOfFreqComponent(self, data, startIndex, endIndex, sampleRate, frequency):
        length = endIndex - startIndex + 1
        k = 2.0 * math.pi * frequency / sampleRate  # precalculate for speed

        # Perform correlation with sine and cosine waveforms.
        meanI = 0.0
        meanQ = 0.0
        for t in range(startIndex, endIndex+1):
            meanI += data[t] * math.cos(k * t)
            meanQ += data[t] * -1.0 * math.sin(k * t)

        meanI /= float(length)
        meanQ /= float(length)

        realComponent = 2.0 * meanI
        imagComponent = 2.0 * meanQ
        return realComponent, imagComponent

    # Returns the total number of temperature sensors connected to the interface board.
    # Only returns valid value after createSaveList() has been called.
    def getNumTempSensors(self):
        return len(self.saveListTempSensor)

    # Reset the vector and variables used to calculate running average
    # of temperature sensor readings.
    def tempHistoryReset(self, requestedLength):
        if self.numDataStreams == 0:
            return

        # Clear data in raw temperature sensor history vectors.
        for stream in range(self.numDataStreams):
            for i in range(len(self.tempRawHistory)):
                self.tempRawHistory[stream][i] = 0.0

        self.tempHistoryLength = 0

        # Set number of samples used to average temperature sensor readings.
        # This number must be at least four, and must be an integer multiple of
        # four.  (See RHD2000 datasheet for details on temperature sensor operation.)

        self.tempHistoryMaxLength = requestedLength

        if self.tempHistoryMaxLength < 4:
            self.tempHistoryMaxLength = 4
        elif self.tempHistoryMaxLength > len(self.tempRawHistory[0]):
            self.tempHistoryMaxLength = len(self.tempRawHistory[0])

        multipleOfFour = 4 * \
            math.floor((float(self.tempHistoryMaxLength)) / 4.0)

        self.tempHistoryMaxLength = multipleOfFour

    # Returns the total number of bytes saved to disk per data block.
    def bytesPerBlock(self, saveFormat, saveTemperature, saveTtlOut):
        bytespb = 0
        bytespb += 4 * constants.SAMPLES_PER_DATA_BLOCK  # timestamps
        bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK * \
            len(self.saveListAmplifier)
        if saveFormat == constants.SaveFormatIntan:
            bytespb += 2 * (constants.SAMPLES_PER_DATA_BLOCK / 4) * \
                len(self.saveListAuxInput)
            bytespb += 2 * (constants.SAMPLES_PER_DATA_BLOCK / 60) * \
                len(self.saveListSupplyVoltage)
            if saveTemperature:
                bytespb += 2 * (constants.SAMPLES_PER_DATA_BLOCK / 60) * \
                    len(self.saveListSupplyVoltage)

        else:
            bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK * \
                len(self.saveListAuxInput)
            bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK * \
                len(self.saveListSupplyVoltage)

        bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK * \
            len(self.saveListBoardAdc)
        if saveFormat == constants.SaveFormatIntan or saveFormat == constants.SaveFormatFilePerSignalType:
            if self.saveListBoardDigIn:
                bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK

        else:
            bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK * \
                len(self.saveListBoardDigitalIn)

        if saveTtlOut:
            if saveFormat == constants.SaveFormatIntan or saveFormat == constants.SaveFormatFilePerSignalType:
                bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK
        else:
            bytespb += 2 * constants.SAMPLES_PER_DATA_BLOCK * 16
        return bytespb

    # Push raw temperature sensor readings into the queue-like vector that
    # stores the last tempHistoryLength readings.
    def tempHistoryPush(self, tempData):
        for stream in range(self.numDataStreams):
            i = self.tempHistoryLength
            while i > 0:
                self.tempRawHistory[stream][i] = self.tempRawHistory[stream][i-1]
                i -= 1

            self.tempRawHistory[stream][0] = tempData[stream]

        if self.tempHistoryLength < self.tempHistoryMaxLength:
            self.tempHistoryLength += 1

    # Calculate running average of temperature from stored raw sensor readings.
    # Results are stored in the tempAvg vector.
    def tempHistoryCalcAvg(self):
        for stream in range(self.numDataStreams):
            self.tempAvg[stream] = 0.0
            for i in range(self.tempHistoryLength):
                self.tempAvg[stream] += self.tempRawHistory[stream][i]

            if self.tempHistoryLength > 0:
                self.tempAvg[stream] /= self.tempHistoryLength

# Allocates memory for a 3-D array of doubles.


def allocateDoubleArray3D(xSize, ySize, zSize):
    if xSize == 0:
        return None  # CHECK
    ret = [0]*xSize
    for i in range(0, xSize):
        ret[i] = [0]*ySize
        for j in range(0, ySize):
            ret[i][j] = [0.0]*zSize
    return ret

# Allocates memory for a 2-D array of doubles.


def allocateDoubleArray2D(xSize, ySize):
    if xSize == 0:
        return None  # CHECK
    ret = [0]*xSize
    for i in range(0, xSize):
        ret[i] = [0.0]*ySize
    return ret

# Allocates memory for a 2-D array of integers.


def allocateIntArray2D(xSize, ySize):
    if xSize == 0:
        return None  # CHECK
    ret = [0]*xSize
    for i in range(0, xSize):
        ret[i] = [0]*ySize
    return ret

# Allocates memory for a 1-D array of doubles.


def allocateDoubleArray1D(xSize):
    ret = [0.0]*xSize
    return ret

# Fill a 3-D array of doubles with zero.


def fillZerosDoubleArray3D(array3D):
    xSize = len(array3D)
    if xSize == 0:
        return

    ySize = len(array3D[0])
    zSize = len(array3D[0][0])

    for x in range(xSize):
        for y in range(ySize):
            for z in range(zSize):
                array3D[x][y][z] = 0.0

# Fill a 2-D array of doubles with zero.


def fillZerosDoubleArray2D(array2D):
    xSize = len(array2D)
    if xSize == 0:
        return

    ySize = len(array2D[0])
    for x in range(xSize):
        for y in range(ySize):
            array2D[x][y] = 0.0
