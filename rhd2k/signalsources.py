#!/usr/bin/python3
# -*- coding: utf-8 -*-

import constants
from signalgroup import SignalGroup


class SignalSources():
    def __init__(self):
        # We have six signal ports: four SPI ports (A-D), the interface board
        # ADC inputs, and the interface board digital inputs.
        self.signalPort = []
        for i in range(7):
            self.signalPort.append(SignalGroup())

        self.signalPort[0].name = "Port A"
        self.signalPort[1].name = "Port B"
        self.signalPort[2].name = "Port C"
        self.signalPort[3].name = "Port D"
        self.signalPort[4].name = "Board ADC Inputs"
        self.signalPort[5].name = "Board Digital Inputs"
        self.signalPort[6].name = "Board Digital Outputs"

        self.signalPort[0].prefix = "A"
        self.signalPort[1].prefix = "B"
        self.signalPort[2].prefix = "C"
        self.signalPort[3].prefix = "D"
        self.signalPort[4].prefix = "ADC"
        self.signalPort[5].prefix = "DIN"
        self.signalPort[6].prefix = "DOUT"

        self.signalPort[0].enabled = False
        self.signalPort[1].enabled = False
        self.signalPort[2].enabled = False
        self.signalPort[3].enabled = False
        # Board analog inputs are always enabled
        self.signalPort[4].enabled = True
        # Board digital inputs are always enabled
        self.signalPort[5].enabled = True
        self.signalPort[6].enabled = True

        # Add 8 board analog input signals
        for channel in range(8):
            self.signalPort[4].addBoardAdcChannel(channel)
            self.signalPort[4].channel[channel].enabled = False

        # Add 16 board digital input signals
        for channel in range(16):
            self.signalPort[5].addBoardDigInChannel(channel)
            self.signalPort[5].channel[channel].enabled = False

        # Add 16 board digital output signals
        for channel in range(16):
            self.signalPort[6].addBoardDigOutChannel(channel)
            self.signalPort[6].channel[channel].enabled = True

        # Amplifier channels on SPI ports A-D are added later, if amplifier
        # boards are found to be connected to these ports.

    # Return a pointer to a SignalChannel with a particular nativeName (e.g., "A-02").
    def findChannelFromName(self, nativeName):
        for i in range(len(self.signalPort)):
            for j in range(self.signalPort[i].numChannels()):
                if self.signalPort[i].channel[j].nativeChannelName == nativeName:
                    channel = self.signalPort[i].channel[j]
                    return channel

        return 0

    # Return a pointer to a SignalChannel corresponding to a particular USB interface
    # data stream and chip channel number.
    def findAmplifierChannel(self, boardStream, chipChannel):
        for i in range(len(self.signalPort)):
            for j in range(self.signalPort[i].numChannels()):
                if self.signalPort[i].channel[j].signalType == constants.AmplifierSignal and self.signalPort[i].channel[j].boardStream == boardStream and self.signalPort[i].channel[j].chipChannel == chipChannel:
                    channel = self.signalPort[i].channel[j]
                    return channel
        return 0

    def writeToStream(self, outStream):
        outStream.writeInt16(len(self.signalPort))
        for port in self.signalPort:
            port.writeToStream(outStream)

    # Stream all signal sources in from binary data stream.
    @staticmethod
    def readFromStream(inStream, signalSources):
        tempQint16 = inStream.readInt16()
        nGroups = int(tempQint16)

        signalSources.signalPort.clear()
        for i in range(nGroups):
            signalSources.signalPort.append(
                SignalGroup.readFromStream(inStream))
