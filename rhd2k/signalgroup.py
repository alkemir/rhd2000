#!/usr/bin/python3
# -*- coding: utf-8 -*-

import constants
from signalchannel import SignalChannel


class SignalGroup():
    def __init__(self, initialName=None, initialPrefix=None):
        self.name = initialName
        self.prefix = initialPrefix
        self.enabled = True
        self.channel = []

    # Add new amplifier channel to this signal group.
    def addAmplifierChannel(self):
        newChannel = SignalChannel(initSignalGroup=self)
        self.channel.append(newChannel)

    # Add new amplifier channel (with specified properties) to this signal group.
    def addAmplifierChannelSpecific(self, nativeChannelNumber, chipChannel, boardStream):
        nativeChannelName = self.prefix + "-" + "%03d" % nativeChannelNumber
        customChannelName = nativeChannelName

        newChannel = SignalChannel(customChannelName, nativeChannelName,
                                   nativeChannelNumber, constants.AmplifierSignal,
                                   chipChannel, boardStream, self)
        self.channel.append(newChannel)
        self.updateAlphabeticalOrder()

    # Add new auxiliary input channel to this signal group.
    def addAuxInputChannel(self, nativeChannelNumber, chipChannel, nameNumber, boardStream):
        nativeChannelName = self.prefix + "-" + "AUX" + str(nameNumber)
        customChannelName = nativeChannelName

        newChannel = SignalChannel(customChannelName, nativeChannelName,
                                   nativeChannelNumber, constants.AuxInputSignal,
                                   chipChannel, boardStream, self)
        self.channel.append(newChannel)
        self.updateAlphabeticalOrder()

    # Add new supply voltage channel to this signal group.
    def addSupplyVoltageChannel(self, nativeChannelNumber, chipChannel, nameNumber, boardStream):
        nativeChannelName = self.prefix + "-" + "VDD" + str(nameNumber)
        customChannelName = nativeChannelName

        newChannel = SignalChannel(customChannelName, nativeChannelName,
                                   nativeChannelNumber, constants.SupplyVoltageSignal,
                                   chipChannel, boardStream, self)
        self.channel.append(newChannel)
        self.updateAlphabeticalOrder()

    # Add new USB interface board ADC channel to this signal group.
    def addBoardAdcChannel(self, nativeChannelNumber):
        nativeChannelName = self.prefix + "-" + "%02d" % nativeChannelNumber
        customChannelName = nativeChannelName

        newChannel = SignalChannel(customChannelName, nativeChannelName,
                                   nativeChannelNumber, constants.BoardAdcSignal,
                                   nativeChannelNumber, 0, self)
        self.channel.append(newChannel)
        self.updateAlphabeticalOrder()

    # Add new USB interface board digital input channel to this signal group.
    def addBoardDigInChannel(self, nativeChannelNumber):
        nativeChannelName = self.prefix + "-" + "%02d" % nativeChannelNumber
        customChannelName = nativeChannelName

        newChannel = SignalChannel(customChannelName, nativeChannelName,
                                   nativeChannelNumber, constants.BoardDigInSignal,
                                   nativeChannelNumber, 0, self)
        self.channel.append(newChannel)
        self.updateAlphabeticalOrder()

    # Add new USB interface board digital output channel to this signal group.
    def addBoardDigOutChannel(self, nativeChannelNumber):
        nativeChannelName = self.prefix + "-" + "%02d" % nativeChannelNumber
        customChannelName = nativeChannelName

        newChannel = SignalChannel(customChannelName, nativeChannelName,
                                   nativeChannelNumber, constants.BoardDigOutSignal,
                                   nativeChannelNumber, 0, self)
        self.channel.append(newChannel)
        self.updateAlphabeticalOrder()

    # Add a previously-created signal channel to this signal group.
    def addChannel(self, newChannel):
        self.channel.append(newChannel)
        self.updateAlphabeticalOrder()

    # Returns a pointer to a signal channel with a particular native order index.
    def channelByNativeOrder(self, index):
        for i in range(len(self.channel)):
            if self.channel[i].nativeChannelNumber == index:
                return self.channel[i]
        return 0

    # Returns a pointer to a signal channel with a particular alphabetical order index.
    def channelByAlphaOrder(self, index):
        for i in range(len(self.channel)):
            if self.channel[i].alphaOrder == index:
                return self.channel[i]
        return 0

    # Returns a pointer to a signal channel with a particular user-selected order index
    def channelByIndex(self, index):
        for i in range(len(self.channel)):
            if self.channel[i].userOrder == index:
                return self.channel[i]

        print("SignalGroup.channelByUserOrder: index " +
              str(index) + " not found.\n")
        return 0

    # Returns the total number of channels in this signal group.
    def numChannels(self):
        return len(self.channel)

    # Returns the total number of AMPLIFIER channels in this signal group.
    def numAmplifierChannels(self):
        count = 0
        for i in range(len(self.channel)):
            if self.channel[i].signalType == constants.AmplifierSignal:
                count += 1

        return count

    # Updates the alphabetical order indices of all signal channels in this signal group.
    def updateAlphabeticalOrder(self):
        size = len(self.channel)

        # Mark all alphaetical order indices with -1 to indicate they have not yet
        # been assigned an order.
        for i in range(size):
            self.channel[i].alphaOrder = -1

        for i in range(size):
            # Find the first remaining non-alphabetized item.
            j = 0
            while self.channel[j].alphaOrder != -1:
                j += 1
            currentFirstName = self.channel[j].customChannelName
            currentFirstIndex = j

            # Now compare all other remaining items.
            j += 1
            while j < size:
                if self.channel[j].alphaOrder == -1:
                    if self.channel[j].customChannelName.lower() < currentFirstName.lower():
                        currentFirstName = self.channel[j].customChannelName
                        currentFirstIndex = j
                j += 1

            # Now assign correct alphabetical order to this item.
            self.channel[currentFirstIndex].alphaOrder = i

    # Restores channels to their original order.
    def setOriginalChannelOrder(self):
        for i in range(len(self.channel)):
            self.channel[i].userOrder = self.channel[i].nativeChannelNumber

    # Orders signal channels alphabetically.
    def setAlphabeticalChannelOrder(self):
        self.updateAlphabeticalOrder()
        for i in range(len(self.channel)):
            self.channel[i].userOrder = self.channel[i].alphaOrder

    # Diagnostic routine to display all channels in this group (to cout).
    def print(self):
        print("SignalGroup " + self.name + " (" + self.prefix +
              ") enabled:" + self.enabled + "\n")
        for i in range(len(self.channel)):
            print("  SignalChannel " + self.channel[i].nativeChannelNumber + " " + self.channel[i].customChannelName.toStdString() + " (" +
                  self.channel[i].nativeChannelName.toStdString() + ") stream:" + self.channel[i].boardStream +
                  " channel:" + self.channel[i].chipChannel + "\n")
        print("\n")

    # Streams all signal channels in this group out to binary data stream.
    def writeToStream(self, outStream):
        outStream.writeQString(self.name)
        outStream.writeQString(self.prefix)
        outStream.writeInt16(self.enabled)
        outStream.writeInt16(self.numChannels())
        outStream.writeInt16(self.numAmplifierChannels())
        for i in range(self.numChannels()):
            self.channel[i].writeToStream(outStream)

    # Streams all signal channels in this group in from binary data stream.
    @staticmethod
    def readFromStream(inStream):
        ret = SignalGroup()
        ret.name = inStream.readQString()
        ret.prefix = inStream.readQString()
        ret.enabled = bool(inStream.readInt16())
        nTotal = int(inStream.readInt16())
        nAmps = int(inStream.readInt16())

        # Delete all existing SignalChannel objects in this SignalGroup
        ret.channel.clear()

        for i in range(nTotal):
            ret.addAmplifierChannel()
            ret.channel[i] = SignalChannel.readFromStream(inStream)

        ret.updateAlphabeticalOrder()
        return ret
