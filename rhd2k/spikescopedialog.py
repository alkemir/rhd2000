from PyQt5.QtWidgets import QDialog, QGroupBox, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QComboBox, QPushButton, QSpinBox

import constants

from spikeplot import SpikePlot
# Spike scope dialog.
# self dialog allows users to view 3-msec snippets of neural spikes triggered
# either from a selectable voltage threshold or a digital input threshold.  Multiple
# spikes are superimposed on the display so that users can compare spike shapes.


class SpikeScopeDialog(QDialog):
    def __init__(self, inSignalProcessor, inSignalSources, initialChannel, parent):
        super().__init__(parent)
        self.setWindowTitle("Spike Scope")

        self.signalProcessor = inSignalProcessor
        self.signalSources = inSignalSources

        self.spikePlot = SpikePlot(
            self.signalProcessor, initialChannel, self, self)
        self.currentChannel = initialChannel

        self.resetToZeroButton = QPushButton("Zero")
        clearScopeButton = QPushButton("Clear Scope")
        applyToAllButton = QPushButton("Apply to Entire Port")

        self.resetToZeroButton.clicked.connect(self.resetThresholdToZero)
        clearScopeButton.clicked.connect(self.clearScope)
        applyToAllButton.clicked.connect(self.applyToAll)

        self.triggerTypeComboBox = QComboBox()
        self.triggerTypeComboBox.addItem("Voltage Threshold")
        self.triggerTypeComboBox.addItem("Digital Input")
        self.triggerTypeComboBox.setCurrentIndex(0)

        self.triggerTypeComboBox.currentIndexChanged.connect(
            self.setTriggerType)

        self.thresholdSpinBox = QSpinBox()
        self.thresholdSpinBox.setRange(-5000, 5000)
        self.thresholdSpinBox.setSingleStep(5)
        self.thresholdSpinBox.setValue(0)

        self.thresholdSpinBox.valueChanged.connect(self.setVoltageThreshold)

        thresholdSpinBoxLayout = QHBoxLayout()
        thresholdSpinBoxLayout.addWidget(self.resetToZeroButton)
        thresholdSpinBoxLayout.addWidget(self.thresholdSpinBox)
        thresholdSpinBoxLayout.addWidget(
            QLabel(constants.QSTRING_MU_SYMBOL + "V"))
        # thresholdSpinBoxLayout.addStretch(1)

        self.digitalInputComboBox = QComboBox()
        self.digitalInputComboBox.addItem("Digital Input 0")
        self.digitalInputComboBox.addItem("Digital Input 1")
        self.digitalInputComboBox.addItem("Digital Input 2")
        self.digitalInputComboBox.addItem("Digital Input 3")
        self.digitalInputComboBox.addItem("Digital Input 4")
        self.digitalInputComboBox.addItem("Digital Input 5")
        self.digitalInputComboBox.addItem("Digital Input 6")
        self.digitalInputComboBox.addItem("Digital Input 7")
        self.digitalInputComboBox.addItem("Digital Input 8")
        self.digitalInputComboBox.addItem("Digital Input 9")
        self.digitalInputComboBox.addItem("Digital Input 10")
        self.digitalInputComboBox.addItem("Digital Input 11")
        self.digitalInputComboBox.addItem("Digital Input 12")
        self.digitalInputComboBox.addItem("Digital Input 13")
        self.digitalInputComboBox.addItem("Digital Input 14")
        self.digitalInputComboBox.addItem("Digital Input 15")
        self.digitalInputComboBox.setCurrentIndex(0)

        self.digitalInputComboBox.currentIndexChanged.connect(
            self.setDigitalInput)

        self.edgePolarityComboBox = QComboBox()
        self.edgePolarityComboBox.addItem("Rising Edge")
        self.edgePolarityComboBox.addItem("Falling Edge")
        self.edgePolarityComboBox.setCurrentIndex(0)

        self.edgePolarityComboBox.currentIndexChanged.connect(
            self.setEdgePolarity)

        numSpikesComboBox = QComboBox()
        numSpikesComboBox.addItem("Show 10 Spikes")
        numSpikesComboBox.addItem("Show 20 Spikes")
        numSpikesComboBox.addItem("Show 30 Spikes")
        numSpikesComboBox.setCurrentIndex(1)

        numSpikesComboBox.currentIndexChanged.connect(self.setNumSpikes)

        self.yScaleList = []
        self.yScaleList.append(50)
        self.yScaleList.append(100)
        self.yScaleList.append(200)
        self.yScaleList.append(500)
        self.yScaleList.append(1000)
        self.yScaleList.append(2000)
        self.yScaleList.append(5000)

        self.yScaleComboBox = QComboBox()
        for i in range(len(self.yScaleList)):
            self.yScaleComboBox.addItem("+/-" + str(self.yScaleList[i]) +
                                        " " + constants.QSTRING_MU_SYMBOL + "V")
        self.yScaleComboBox.setCurrentIndex(4)

        self.yScaleComboBox.currentIndexChanged.connect(self.changeYScale)

        triggerLayout = QVBoxLayout()
        triggerLayout.addWidget(QLabel("Type:"))
        triggerLayout.addWidget(self.triggerTypeComboBox)
        triggerLayout.addWidget(QLabel("Voltage Threshold:"))
        triggerLayout.addLayout(thresholdSpinBoxLayout)
        triggerLayout.addWidget(QLabel("(or click in scope to set)"))
        triggerLayout.addWidget(QLabel("Digital Source:"))
        triggerLayout.addWidget(self.digitalInputComboBox)
        triggerLayout.addWidget(self.edgePolarityComboBox)

        displayLayout = QVBoxLayout()
        displayLayout.addWidget(QLabel("Voltage Scale:"))
        displayLayout.addWidget(self.yScaleComboBox)
        displayLayout.addWidget(numSpikesComboBox)
        displayLayout.addWidget(clearScopeButton)

        triggerGroupBox = QGroupBox("Trigger Settings")
        triggerGroupBox.setLayout(triggerLayout)

        displayGroupBox = QGroupBox("Display Settings")
        displayGroupBox.setLayout(displayLayout)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(triggerGroupBox)
        leftLayout.addWidget(applyToAllButton)
        leftLayout.addWidget(displayGroupBox)
        leftLayout.addStretch(1)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addWidget(self.spikePlot)
        mainLayout.setStretch(0, 0)
        mainLayout.setStretch(1, 1)

        self.setLayout(mainLayout)

        self.setTriggerType(self.triggerTypeComboBox.currentIndex())
        self.setNumSpikes(numSpikesComboBox.currentIndex())
        self.setVoltageThreshold(self.thresholdSpinBox.value())
        self.setDigitalInput(self.digitalInputComboBox.currentIndex())
        self.setEdgePolarity(self.edgePolarityComboBox.currentIndex())

    def changeYScale(self, index):
        self.spikePlot.setYScale(self.yScaleList[index])

    def setYScale(self, index):
        self.yScaleComboBox.setCurrentIndex(index)
        self.spikePlot.setYScale(self.yScaleList[index])

    def setSampleRate(self, newSampleRate):
        self.spikePlot.setSampleRate(newSampleRate)

    # Select a voltage trigger if index == 0.
    # Select a digital input trigger if index == 1.
    def setTriggerType(self, index):
        self.thresholdSpinBox.setEnabled(index == 0)
        self.resetToZeroButton.setEnabled(index == 0)
        self.digitalInputComboBox.setEnabled(index == 1)
        self.edgePolarityComboBox.setEnabled(index == 1)
        self.spikePlot.setVoltageTriggerMode(index == 0)

    def resetThresholdToZero(self):
        self.thresholdSpinBox.setValue(0)

    def updateWaveform(self, numBlocks):
        self.spikePlot.updateWaveform(numBlocks)

    # Set number of spikes plotted superimposed.
    def setNumSpikes(self, index):
        if index == 0:
            num = 10
        elif index == 1:
            num = 20
        elif index == 2:
            num = 30

        self.spikePlot.setMaxNumSpikeWaveforms(num)

    def clearScope(self):
        self.spikePlot.clearScope()

    def setDigitalInput(self, index):
        self.spikePlot.setDigitalTriggerChannel(index)

    def setVoltageThreshold(self, value):
        self.spikePlot.setVoltageThreshold(value)

    def setVoltageThresholdDisplay(self, value):
        self.thresholdSpinBox.setValue(value)

    def setEdgePolarity(self, index):
        self.spikePlot.setDigitalEdgePolarity(index == 0)

    # Set Spike Scope to a signal channel source.
    def setNewChannel(self, newChannel):
        self.spikePlot.setNewChannel(newChannel)
        self.currentChannel = newChannel
        if newChannel.voltageTriggerMode:
            self.triggerTypeComboBox.setCurrentIndex(0)
        else:
            self.triggerTypeComboBox.setCurrentIndex(1)

        self.thresholdSpinBox.setValue(newChannel.voltageThreshold)
        self.digitalInputComboBox.setCurrentIndex(
            newChannel.digitalTriggerChannel)
        if newChannel.digitalEdgePolarity:
            self.edgePolarityComboBox.setCurrentIndex(0)
        else:
            self.edgePolarityComboBox.setCurrentIndex(1)

    def expandYScale(self):
        if self.yScaleComboBox.currentIndex() > 0:
            self.yScaleComboBox.setCurrentIndex(
                self.yScaleComboBox.currentIndex() - 1)
            self.changeYScale(self.yScaleComboBox.currentIndex())

    def contractYScale(self):
        if self.yScaleComboBox.currentIndex() < len(self.yScaleList) - 1:
            self.yScaleComboBox.setCurrentIndex(
                self.yScaleComboBox.currentIndex() + 1)
            self.changeYScale(self.yScaleComboBox.currentIndex())

    # Apply trigger settings to all channels on selected port.
    def applyToAll(self):
        r = QMessageBox.question(
            self, "Trigger Settings", "Do you really want to copy the current channel's trigger settings to <b>all</b> amplifier channels on self port?", QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            for i in range(self.currentChannel.signalGroup.numChannels()):
                self.currentChannel.signalGroup.channel[i].voltageTriggerMode = self.currentChannel.voltageTriggerMode
                self.currentChannel.signalGroup.channel[i].voltageThreshold = self.currentChannel.voltageThreshold
                self.currentChannel.signalGroup.channel[
                    i].digitalTriggerChannel = self.currentChannel.digitalTriggerChannel
                self.currentChannel.signalGroup.channel[i].digitalEdgePolarity = self.currentChannel.digitalEdgePolarity
