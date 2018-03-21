#!/usr/bin/python3
# -*- coding: utf-8 -*-


class SignalChannel():
    # Data structure containing description of a particular signal channel
    # (e.g., an amplifier channel on a particular RHD2000 chip, a digital
    # input from the USB interface board, etc.).
    def __init__(self, initCustomChannelName="", initNativeChannelName="",
                 initNativeChannelNumber=-1, initSignalType=None,
                 initBoardChannel=None, initBoardStream=None, initSignalGroup=0):

        self.signalGroup = initSignalGroup

        self.enabled = True
        self.alphaOrder = -1
        self.userOrder = initNativeChannelNumber

        self.voltageTriggerMode = True
        self.voltageThreshold = 0
        self.digitalTriggerChannel = 0
        self.digitalEdgePolarity = True

        self.electrodeImpedanceMagnitude = 0.0
        self.electrodeImpedancePhase = 0.0

        self.customChannelName = initCustomChannelName
        self.nativeChannelName = initNativeChannelName
        self.nativeChannelNumber = initNativeChannelNumber
        self.signalType = initSignalType
        self.boardStream = initBoardStream
        self.chipChannel = initBoardChannel

    # Streams this signal channel out to binary data stream.
    def writeToStream(self, outStream):
        outStream.writeQString(self.nativeChannelName)
        outStream.writeQString(self.customChannelName)
        outStream.writeInt16(self.nativeChannelNumber)
        outStream.writeInt16(self.userOrder)
        outStream.writeInt16(self.signalType)
        outStream.writeInt16(self.enabled)
        outStream.writeInt16(self.chipChannel)
        outStream.writeInt16(self.boardStream)
        outStream.writeInt16(self.voltageTriggerMode)
        outStream.writeInt16(self.voltageThreshold)
        outStream.writeInt16(self.digitalTriggerChannel)
        outStream.writeInt16(self.digitalEdgePolarity)
        outStream.writeDouble(self.electrodeImpedanceMagnitude)
        outStream.writeDouble(self.electrodeImpedancePhase)

    @staticmethod
    def readFromStream(inStream):
        # Streams this signal channel in from binary data stream.
        ret = SignalChannel()
        ret.nativeChannelName = inStream.readQString()
        ret.customChannelName = inStream.readQString()
        ret.nativeChannelNumber = int(inStream.readInt16())
        ret.userOrder = int(inStream.readInt16())
        ret.signalType = int(inStream.readInt16())
        ret.enabled = bool(inStream.readInt16())
        ret.chipChannel = int(inStream.readInt16())
        ret.boardStream = int(inStream.readInt16())
        ret.voltageTriggerMode = bool(inStream.readInt16())
        ret.voltageThreshold = int(inStream.readInt16())
        ret.digitalTriggerChannel = int(inStream.readInt16())
        ret.digitalEdgePolarity = bool(inStream.readInt16())
        ret.electrodeImpedanceMagnitude = inStream.readDouble()
        ret.electrodeImpedancePhase = inStream.readDouble()
        return ret
