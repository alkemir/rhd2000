# not /usr/bin/python3
# -*- coding: utf-8 -*-

# TODO: The trigger and record buttons are activated upon loading settings
# although synthMode is set. This seems like a bug.

# TODO: cSeries variable is not used.

import math
import sys

from PyQt5.QtWidgets import QMainWindow, QAction, QLabel, QPushButton, QRadioButton, QSlider
from PyQt5.QtWidgets import QButtonGroup, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt5.QtWidgets import QFrame, QLineEdit, QCheckBox, QSpinBox, QTabWidget, QWidget
from PyQt5.QtWidgets import QApplication, QScrollArea, QMessageBox, QFileDialog, qApp, QProgressDialog
from PyQt5.QtGui import QIcon, QDoubleValidator, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QFile, QDir, QIODevice, QDataStream, QDateTime, QCoreApplication, QTime, QTextStream

import constants

from auxdigoutconfigdialog import AuxDigOutConfigDialog
from bandwidthdialog import BandwidthDialog
from cabledelaydialog import CableDelayDialog
from dataqueue import DataQueue
from helpdialogcomparators import HelpDialogComparators
from helpdialogchipfilters import HelpDialogChipFilters
from helpdialogdacs import HelpDialogDacs
from helpdialogfastsettle import HelpDialogFastSettle
from helpdialoghighpassfilter import HelpDialogHighpassFilter
from helpdialognotchfilter import HelpDialogNotchFilter
from impedancefreqdialog import ImpedanceFreqDialog
from keyboardshortcutdialog import KeyboardShortcutDialog
from renamechanneldialog import RenameChannelDialog
from rhd2000datablock import Rhd2000DataBlock
from rhd2000evalboard import Rhd2000EvalBoard
from rhd2000registers import Rhd2000Registers
from setsaveformatdialog import SetSaveFormatDialog
from signalsources import SignalSources
from signalprocessor import SignalProcessor
from spikescopedialog import SpikeScopeDialog
from triggerrecorddialog import TriggerRecordDialog
from vector import VectorInt
from waveplot import WavePlot


class MainWindow(QMainWindow):
    """Main window of the application"""

    def __init__(self):
        super().__init__()

        # Default amplifier bandwidth settings
        self.desiredLowerBandwidth = 0.1
        self.desiredUpperBandwidth = 7500.0
        self.desiredDspCutoffFreq = 1.0

        # Defaults for linting
        self.dspEnabled = True
        self.keyboardShortcutDialog = None
        self.helpDialogChipFilters = None
        self.helpDialogComparators = None
        self.helpDialogDacs = None
        self.helpDialogHighpassFilter = None
        self.helpDialogNotchFilter = None
        self.helpDialogFastSettle = None
        self.spikeScopeDialog = None
        self.auxDigOutConfigDialog = None
        self.triggerRecordDialog = None
        self.saveBaseFileName = ""

        self.evalBoard = Rhd2000EvalBoard()
        self.saveFormat = None
        self.infoFile = None
        self.infoFileName = ""
        self.infoStream = None
        self.saveStream = None

        self.actualDspCutoffFreq = 0.0
        self.actualLowerBandwidth = 0.0
        self.actualUpperBandwidth = 0.0

        self.boardSampleRate = 0
        self.saveFileName = ""

        # Default electrode impedance measurement frequency
        self.desiredImpedanceFreq = 1000.0

        self.actualImpedanceFreq = 0.0
        self.impedanceFreqValid = False

        # Set up vectors for 8 DACs on USB interface board
        self.dacEnabled = [False]*8
        self.dacSelectedChannel = [0]*8

        self.cableLengthPortA = 1.0
        self.cableLengthPortB = 1.0
        self.cableLengthPortC = 1.0
        self.cableLengthPortD = 1.0

        self.chipId = [-1]*constants.MAX_NUM_DATA_STREAMS
        self.ttlOut = [0]*16

        for i in range(0, 16):
            self.ttlOut[i] = 0

        self.evalBoardMode = 0

        self.recordTriggerChannel = 0
        self.recordTriggerPolarity = 0
        self.recordTriggerBuffer = 1
        self.postTriggerTime = 1
        self.saveTriggerChannel = True

        self.signalSources = SignalSources()

        self.channelVisible = [[False]*32]*constants.MAX_NUM_DATA_STREAMS

        self.signalProcessor = SignalProcessor()
        self.notchFilterFrequency = 60.0
        self.notchFilterBandwidth = 10.0
        self.notchFilterEnabled = False
        self.signalProcessor.setNotchFilterEnabled(self.notchFilterEnabled)
        self.highpassFilterFrequency = 250.0
        self.highpassFilterEnabled = False
        self.signalProcessor.setHighpassFilterEnabled(
            self.highpassFilterEnabled)

        self.running = False
        self.recording = False
        self.triggerSet = False
        self.triggered = False

        self.saveTemp = False
        self.saveTtlOut = False
        self.validFilename = False
        self.synthMode = False
        self.fastSettleEnabled = False

        self.wavePlot = WavePlot(self.signalProcessor,
                                 self.signalSources, self, self)

        self.wavePlot.selectedChannelChanged.connect(self.newSelectedChannel)

        self.createActions()
        self.createMenus()
        self.createStatusBar()
        self.createLayout()

        self.recordButton.setEnabled(self.validFilename)
        self.triggerButton.setEnabled(self.validFilename)
        self.stopButton.setEnabled(False)

        self.manualDelayEnabled = [False]*4
        self.manualDelay = [0]*4

        self.openInterfaceBoard()

        self.changeSampleRate(self.sampleRateComboBox.currentIndex())
        self.sampleRateComboBox.setCurrentIndex(14)

        self.scanPorts()
        self.setStatusBarReady()

        if not self.synthMode:
            self.setDacThreshold1(0)
            self.setDacThreshold2(0)
            self.setDacThreshold3(0)
            self.setDacThreshold4(0)
            self.setDacThreshold5(0)
            self.setDacThreshold6(0)
            self.setDacThreshold7(0)
            self.setDacThreshold8(0)

            self.evalBoard.enableDacHighpassFilter(False)
            self.evalBoard.setDacHighpassFilter(250.0)

        self.auxDigOutEnabled = [False]*4
        self.auxDigOutChannel = [0]*4
        self.updateAuxDigOut()

        # Default data file format.
        self.setSaveFormat(constants.SaveFormatIntan)
        self.newSaveFilePeriodMinutes = 1

        # Default settings for display scale combo boxes.
        self.yScaleComboBox.setCurrentIndex(3)
        self.tScaleComboBox.setCurrentIndex(4)

        self.changeTScale(self.tScaleComboBox.currentIndex())
        self.changeYScale(self.yScaleComboBox.currentIndex())

        self.dataQueue = DataQueue()
        self.filteredDataQueue = DataQueue()

        # CHECK
        # sounds

        self.adjustSize()

    def scanPorts(self):
        self.statusBar().showMessage("Scanning ports...")

        # Scan SPI Ports.
        self.findConnectedAmplifiers()

        # Configure SignalProcessor object for the required number of data streams.
        if not self.synthMode:
            self.signalProcessor.allocateMemory(
                self.evalBoard.getNumEnabledDataStreams())
            self.setWindowTitle("Intan Technologies RHD2000 Interface")
        else:
            self.signalProcessor.allocateMemory(1)
            self.setWindowTitle("Intan Technologies RHD2000 Interface "
                                "(Demonstration Mode with Synthesized Biopotentials)")

        # Turn on appropriate(optional) LEDs for Ports A-D
        if not self.synthMode:
            self.ttlOut[11] = 0
            self.ttlOut[12] = 0
            self.ttlOut[13] = 0
            self.ttlOut[14] = 0
            if self.signalSources.signalPort[0].enabled:
                self.ttlOut[11] = 1
            if self.signalSources.signalPort[1].enabled:
                self.ttlOut[12] = 1
            if self.signalSources.signalPort[2].enabled:
                self.ttlOut[13] = 1
            if self.signalSources.signalPort[3].enabled:
                self.ttlOut[14] = 1
            self.evalBoard.setTtlOut(self.ttlOut)

        # Switch display to the first port that has an amplifier connected.
        if self.signalSources.signalPort[0].enabled:
            self.wavePlot.initialize(0)
        elif self.signalSources.signalPort[1].enabled:
            self.wavePlot.initialize(1)
        elif self.signalSources.signalPort[2].enabled:
            self.wavePlot.initialize(2)
        elif self.signalSources.signalPort[3].enabled:
            self.wavePlot.initialize(3)
        else:
            self.wavePlot.initialize(4)
            QMessageBox.information(self, "No RHD2000 Amplifiers Detected",
                                    "No RHD2000 amplifiers are connected to the interface board."
                                    "<p>Connect amplifier modules and click 'Rescan Ports A-D' under "
                                    "the Configure tab."
                                    "<p>You may record from analog and digital inputs on the evaluation "
                                    "board in the absence of amplifier modules.")

        self.wavePlot.setSampleRate(self.boardSampleRate)
        self.changeTScale(self.tScaleComboBox.currentIndex())
        self.changeYScale(self.yScaleComboBox.currentIndex())

        self.statusBar().clearMessage()

    def createLayout(self):
        self.setWindowIcon(QIcon(":/images/Intan_Icon_32p_trans24.png"))

        self.runButton = QPushButton("&Run")
        self.stopButton = QPushButton("&Stop")
        self.recordButton = QPushButton("Record")
        self.triggerButton = QPushButton("Trigger")
        self.baseFilenameButton = QPushButton("Select Base Filename")
        self.setSaveFormatButton = QPushButton("Select File Format")

        self.changeBandwidthButton = QPushButton("Change Bandwidth")
        self.renameChannelButton = QPushButton("Rename Channel")
        self.enableChannelButton = QPushButton("Enable/Disable (Space)")
        self.enableAllButton = QPushButton("Enable All on Port")
        self.disableAllButton = QPushButton("Disable All on Port")
        self.spikeScopeButton = QPushButton("Open Spike Scope")

        self.helpDialogChipFiltersButton = QPushButton("?")
        self.helpDialogChipFiltersButton.clicked.connect(self.chipFiltersHelp)

        self.helpDialogComparatorsButton = QPushButton("?")
        self.helpDialogComparatorsButton.clicked.connect(self.comparatorsHelp)

        self.helpDialogDacsButton = QPushButton("?")
        self.helpDialogDacsButton.clicked.connect(self.dacsHelp)

        self.helpDialogHighpassFilterButton = QPushButton("?")
        self.helpDialogHighpassFilterButton.clicked.connect(
            self.highpassFilterHelp)

        self.helpDialogNotchFilterButton = QPushButton("?")
        self.helpDialogNotchFilterButton.clicked.connect(self.notchFilterHelp)

        self.helpDialogSettleButton = QPushButton("?")
        self.helpDialogSettleButton.clicked.connect(self.fastSettleHelp)

        self.displayPortAButton = QRadioButton(
            self.signalSources.signalPort[0].name)
        self.displayPortBButton = QRadioButton(
            self.signalSources.signalPort[1].name)
        self.displayPortCButton = QRadioButton(
            self.signalSources.signalPort[2].name)
        self.displayPortDButton = QRadioButton(
            self.signalSources.signalPort[3].name)
        self.displayAdcButton = QRadioButton(
            self.signalSources.signalPort[4].name)
        self.displayDigInButton = QRadioButton(
            self.signalSources.signalPort[5].name)

        self.displayButtonGroup = QButtonGroup()
        self.displayButtonGroup.addButton(self.displayPortAButton, 0)
        self.displayButtonGroup.addButton(self.displayPortBButton, 1)
        self.displayButtonGroup.addButton(self.displayPortCButton, 2)
        self.displayButtonGroup.addButton(self.displayPortDButton, 3)
        self.displayButtonGroup.addButton(self.displayAdcButton, 4)
        self.displayButtonGroup.addButton(self.displayDigInButton, 5)

        portGroupBox = QGroupBox("Ports")
        displayLayout = QVBoxLayout()
        displayLayout.addWidget(self.displayPortAButton)
        displayLayout.addWidget(self.displayPortBButton)
        displayLayout.addWidget(self.displayPortCButton)
        displayLayout.addWidget(self.displayPortDButton)
        displayLayout.addWidget(self.displayAdcButton)
        displayLayout.addWidget(self.displayDigInButton)
        displayLayout.addStretch(1)
        portGroupBox.setLayout(displayLayout)

        channelGroupBox = QGroupBox("Channels")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.renameChannelButton)
        channelLayout.addWidget(self.enableChannelButton)
        channelLayout.addWidget(self.enableAllButton)
        channelLayout.addWidget(self.disableAllButton)
        channelLayout.addStretch(1)
        channelGroupBox.setLayout(channelLayout)

        portChannelLayout = QHBoxLayout()
        portChannelLayout.addWidget(portGroupBox)
        portChannelLayout.addWidget(channelGroupBox)

        # Combo box for selecting number of frames displayed on screen.
        self.numFramesComboBox = QComboBox()
        self.numFramesComboBox.addItem("1")
        self.numFramesComboBox.addItem("2")
        self.numFramesComboBox.addItem("4")
        self.numFramesComboBox.addItem("8")
        self.numFramesComboBox.addItem("16")
        self.numFramesComboBox.addItem("32")
        self.numFramesComboBox.setCurrentIndex(4)

        # Create list of voltage scales and associated combo box.
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
            self.yScaleComboBox.addItem(
                "+/-" + str(self.yScaleList[i]) + " " + constants.QSTRING_MU_SYMBOL + "V")

        # Create list of time scales and associated combo box.
        self.tScaleList = []
        self.tScaleList.append(10)
        self.tScaleList.append(20)
        self.tScaleList.append(50)
        self.tScaleList.append(100)
        self.tScaleList.append(200)
        self.tScaleList.append(500)
        self.tScaleList.append(1000)
        self.tScaleList.append(2000)
        self.tScaleList.append(5000)

        self.tScaleComboBox = QComboBox()
        for i in range(len(self.tScaleList)):
            self.tScaleComboBox.addItem(str(self.tScaleList[i]) + " ms")

        # Amplifier sample rate combo box.
        self.sampleRateComboBox = QComboBox()
        self.sampleRateComboBox.addItem("1.00 kS/s")
        self.sampleRateComboBox.addItem("1.25 kS/s")
        self.sampleRateComboBox.addItem("1.50 kS/s")
        self.sampleRateComboBox.addItem("2.00 kS/s")
        self.sampleRateComboBox.addItem("2.50 kS/s")
        self.sampleRateComboBox.addItem("3.00 kS/s")
        self.sampleRateComboBox.addItem("3.33 kS/s")
        self.sampleRateComboBox.addItem("4.00 kS/s")
        self.sampleRateComboBox.addItem("5.00 kS/s")
        self.sampleRateComboBox.addItem("6.25 kS/s")
        self.sampleRateComboBox.addItem("8.00 kS/s")
        self.sampleRateComboBox.addItem("10.0 kS/s")
        self.sampleRateComboBox.addItem("12.5 kS/s")
        self.sampleRateComboBox.addItem("15.0 kS/s")
        self.sampleRateComboBox.addItem("20.0 kS/s")
        self.sampleRateComboBox.addItem("25.0 kS/s")
        self.sampleRateComboBox.addItem("30.0 kS/s")
        self.sampleRateComboBox.setCurrentIndex(16)

        # Notch filter combo box.
        self.notchFilterComboBox = QComboBox()
        self.notchFilterComboBox.addItem("Disabled")
        self.notchFilterComboBox.addItem("50 Hz")
        self.notchFilterComboBox.addItem("60 Hz")
        self.notchFilterComboBox.setCurrentIndex(0)

        self.runButton.clicked.connect(self.runInterfaceBoard)
        self.stopButton.clicked.connect(self.stopInterfaceBoard)
        self.recordButton.clicked.connect(self.recordInterfaceBoard)
        self.triggerButton.clicked.connect(self.triggerRecordInterfaceBoard)
        self.baseFilenameButton.clicked.connect(self.selectBaseFilenameSlot)
        self.changeBandwidthButton.clicked.connect(self.changeBandwidth)
        self.renameChannelButton.clicked.connect(self.renameChannel)
        self.enableChannelButton.clicked.connect(self.toggleChannelEnable)
        self.enableAllButton.clicked.connect(self.enableAllChannels)
        self.disableAllButton.clicked.connect(self.disableAllChannels)
        self.setSaveFormatButton.clicked.connect(self.setSaveFormatDialog)

        self.numFramesComboBox.currentIndexChanged.connect(
            self.changeNumFrames)
        self.yScaleComboBox.currentIndexChanged.connect(self.changeYScale)
        self.tScaleComboBox.currentIndexChanged.connect(self.changeTScale)
        self.sampleRateComboBox.currentIndexChanged.connect(
            self.changeSampleRate)
        self.notchFilterComboBox.currentIndexChanged.connect(
            self.changeNotchFilter)
        self.displayButtonGroup.buttonClicked[int].connect(self.changePort)

        self.dacGainSlider = QSlider(Qt.Horizontal)
        self.dacNoiseSuppressSlider = QSlider(Qt.Horizontal)

        self.dacGainSlider.setRange(0, 7)
        self.dacGainSlider.setValue(0)
        self.dacNoiseSuppressSlider.setRange(0, 64)
        self.dacNoiseSuppressSlider.setValue(0)

        self.dacGainLabel = QLabel()
        self.dacNoiseSuppressLabel = QLabel()
        self.setDacGainLabel(0)
        self.setDacNoiseSuppressLabel(0)

        self.dacGainSlider.valueChanged.connect(self.changeDacGain)
        self.dacNoiseSuppressSlider.valueChanged.connect(
            self.changeDacNoiseSuppress)

        fifoLagLabel = QLabel("0 ms")
        fifoLagLabel.setStyleSheet("color: green")

        fifoFullLabel = QLabel("(0% full)")
        fifoFullLabel.setStyleSheet("color: black")

        runStopLayout = QHBoxLayout()
        runStopLayout.addWidget(self.runButton)
        runStopLayout.addWidget(self.stopButton)
        runStopLayout.addWidget(QLabel("FIFO lag:"))
        runStopLayout.addStretch(1)
        runStopLayout.addWidget(fifoLagLabel)
        runStopLayout.addWidget(fifoFullLabel)

        recordLayout = QHBoxLayout()
        recordLayout.addWidget(self.recordButton)
        recordLayout.addWidget(self.triggerButton)
        recordLayout.addWidget(self.setSaveFormatButton)
        recordLayout.addStretch(1)

        self.saveFilenameLineEdit = QLineEdit()
        self.saveFilenameLineEdit.setEnabled(False)

        filenameSelectLayout = QHBoxLayout()
        filenameSelectLayout.addWidget(self.baseFilenameButton)
        filenameSelectLayout.addWidget(
            QLabel("(Date and time stamp will be added)"))
        filenameSelectLayout.addStretch(1)

        baseFilenameLayout = QHBoxLayout()
        baseFilenameLayout.addWidget(QLabel("Base Filename"))
        baseFilenameLayout.addWidget(self.saveFilenameLineEdit)

        numWaveformsLayout = QHBoxLayout()
        numWaveformsLayout.addWidget(QLabel("Voltage Scale (+/-)"))
        numWaveformsLayout.addWidget(self.yScaleComboBox)
        numWaveformsLayout.addStretch(1)
        numWaveformsLayout.addWidget(self.spikeScopeButton)

        self.spikeScopeButton.clicked.connect(self.spikeScope)

        scaleLayout = QHBoxLayout()
        scaleLayout.addWidget(QLabel("Time Scale (</>)"))
        scaleLayout.addWidget(self.tScaleComboBox)
        scaleLayout.addStretch(1)
        scaleLayout.addWidget(QLabel("Waveforms ([/])"))
        scaleLayout.addWidget(self.numFramesComboBox)

        displayOrderLayout = QVBoxLayout()
        displayOrderLayout.addLayout(numWaveformsLayout)
        displayOrderLayout.addLayout(scaleLayout)
        displayOrderLayout.addStretch(1)

        leftLayout1 = QVBoxLayout()
        leftLayout1.addLayout(runStopLayout)
        leftLayout1.addLayout(recordLayout)
        leftLayout1.addLayout(filenameSelectLayout)
        leftLayout1.addLayout(baseFilenameLayout)
        leftLayout1.addLayout(portChannelLayout)
        leftLayout1.addLayout(displayOrderLayout)

        groupBox1 = QFrame()
        groupBox1.setLayout(leftLayout1)

        frameTab1 = QFrame()
        frameTab2 = QFrame()
        frameTab3 = QFrame()
        frameTab4 = QFrame()

        self.impedanceFreqSelectButton = QPushButton(
            "Select Impedance Test Frequency")
        self.runImpedanceTestButton = QPushButton("Run Impedance Measurement")
        self.runImpedanceTestButton.setEnabled(False)

        self.impedanceFreqSelectButton.clicked.connect(
            self.changeImpedanceFrequency)
        self.runImpedanceTestButton.clicked.connect(
            self.runImpedanceMeasurement)

        self.showImpedanceCheckBox = QCheckBox(
            "Show Last Measured Electrode Impedances")
        self.showImpedanceCheckBox.clicked.connect(self.showImpedances)

        saveImpedancesButton = QPushButton(
            "Save Impedance Measurements in CSV Format")
        saveImpedancesButton.setEnabled(False)
        saveImpedancesButton.clicked.connect(self.saveImpedances)

        impedanceFreqSelectLayout = QHBoxLayout()
        impedanceFreqSelectLayout.addWidget(self.impedanceFreqSelectButton)
        impedanceFreqSelectLayout.addStretch(1)

        runImpedanceTestLayout = QHBoxLayout()
        runImpedanceTestLayout.addWidget(self.runImpedanceTestButton)
        runImpedanceTestLayout.addStretch(1)

        saveImpedancesLayout = QHBoxLayout()
        saveImpedancesLayout.addWidget(saveImpedancesButton)
        saveImpedancesLayout.addStretch(1)

        self.desiredImpedanceFreqLabel = QLabel(
            "Desired Impedance Test Frequency: 1000 Hz")
        self.actualImpedanceFreqLabel = QLabel(
            "Actual Impedance Test Frequency: -")

        impedanceLayout = QVBoxLayout()
        impedanceLayout.addLayout(impedanceFreqSelectLayout)
        impedanceLayout.addWidget(self.desiredImpedanceFreqLabel)
        impedanceLayout.addWidget(self.actualImpedanceFreqLabel)
        impedanceLayout.addLayout(runImpedanceTestLayout)
        impedanceLayout.addWidget(self.showImpedanceCheckBox)
        impedanceLayout.addLayout(saveImpedancesLayout)
        impedanceLayout.addWidget(
            QLabel("(Impedance measurements are also saved with data.)"))
        impedanceLayout.addStretch(1)

        frameTab2.setLayout(impedanceLayout)

        dacGainLayout = QHBoxLayout()
        dacGainLayout.addWidget(QLabel("Electrode-to-DAC Total Gain"))
        dacGainLayout.addWidget(self.dacGainSlider)
        dacGainLayout.addWidget(self.dacGainLabel)
        dacGainLayout.addStretch(1)

        dacNoiseSuppressLayout = QHBoxLayout()
        dacNoiseSuppressLayout.addWidget(
            QLabel("Audio Noise Slicer (DAC 1,2)"))
        dacNoiseSuppressLayout.addWidget(self.dacNoiseSuppressSlider)
        dacNoiseSuppressLayout.addWidget(self.dacNoiseSuppressLabel)
        dacNoiseSuppressLayout.addStretch(1)

        self.dacButton1 = QRadioButton("")
        self.dacButton2 = QRadioButton("")
        self.dacButton3 = QRadioButton("")
        self.dacButton4 = QRadioButton("")
        self.dacButton5 = QRadioButton("")
        self.dacButton6 = QRadioButton("")
        self.dacButton7 = QRadioButton("")
        self.dacButton8 = QRadioButton("")

        for i in range(8):
            self.setDacChannelLabel(i, "n/a", "n/a")

        self.dacButtonGroup = QButtonGroup()
        self.dacButtonGroup.addButton(self.dacButton1, 0)
        self.dacButtonGroup.addButton(self.dacButton2, 1)
        self.dacButtonGroup.addButton(self.dacButton3, 2)
        self.dacButtonGroup.addButton(self.dacButton4, 3)
        self.dacButtonGroup.addButton(self.dacButton5, 4)
        self.dacButtonGroup.addButton(self.dacButton6, 5)
        self.dacButtonGroup.addButton(self.dacButton7, 6)
        self.dacButtonGroup.addButton(self.dacButton8, 7)
        self.dacButton1.setChecked(True)

        self.dacEnableCheckBox = QCheckBox("DAC Enabled")
        self.dacLockToSelectedBox = QCheckBox("Lock DAC 1 to Selected")
        dacSetButton = QPushButton("Set DAC to Selected")

        self.dacEnableCheckBox.clicked.connect(self.dacEnable)
        dacSetButton.clicked.connect(self.dacSetChannel)
        self.dacButtonGroup.buttonClicked[int].connect(self.dacSelected)

        dacControlLayout = QHBoxLayout()
        dacControlLayout.addWidget(self.dacEnableCheckBox)
        dacControlLayout.addWidget(dacSetButton)
        dacControlLayout.addStretch(1)
        dacControlLayout.addWidget(self.dacLockToSelectedBox)

        dacHeadingLayout = QHBoxLayout()
        dacHeadingLayout.addWidget(QLabel("<b><u>DAC Channel</u></b>"))
        dacHeadingLayout.addWidget(self.helpDialogDacsButton)
        dacHeadingLayout.addStretch(1)
        dacHeadingLayout.addWidget(
            QLabel("<b><u>Digital Out Threshold</u></b>"))
        dacHeadingLayout.addWidget(self.helpDialogComparatorsButton)

        self.dac1ThresholdSpinBox = QSpinBox()
        self.dac1ThresholdSpinBox.setRange(-6400, 6400)
        self.dac1ThresholdSpinBox.setSingleStep(5)
        self.dac1ThresholdSpinBox.setValue(0)

        self.dac2ThresholdSpinBox = QSpinBox()
        self.dac2ThresholdSpinBox.setRange(-6400, 6400)
        self.dac2ThresholdSpinBox.setSingleStep(5)
        self.dac2ThresholdSpinBox.setValue(0)

        self.dac3ThresholdSpinBox = QSpinBox()
        self.dac3ThresholdSpinBox.setRange(-6400, 6400)
        self.dac3ThresholdSpinBox.setSingleStep(5)
        self.dac3ThresholdSpinBox.setValue(0)

        self.dac4ThresholdSpinBox = QSpinBox()
        self.dac4ThresholdSpinBox.setRange(-6400, 6400)
        self.dac4ThresholdSpinBox.setSingleStep(5)
        self.dac4ThresholdSpinBox.setValue(0)

        self.dac5ThresholdSpinBox = QSpinBox()
        self.dac5ThresholdSpinBox.setRange(-6400, 6400)
        self.dac5ThresholdSpinBox.setSingleStep(5)
        self.dac5ThresholdSpinBox.setValue(0)

        self.dac6ThresholdSpinBox = QSpinBox()
        self.dac6ThresholdSpinBox.setRange(-6400, 6400)
        self.dac6ThresholdSpinBox.setSingleStep(5)
        self.dac6ThresholdSpinBox.setValue(0)

        self.dac7ThresholdSpinBox = QSpinBox()
        self.dac7ThresholdSpinBox.setRange(-6400, 6400)
        self.dac7ThresholdSpinBox.setSingleStep(5)
        self.dac7ThresholdSpinBox.setValue(0)

        self.dac8ThresholdSpinBox = QSpinBox()
        self.dac8ThresholdSpinBox.setRange(-6400, 6400)
        self.dac8ThresholdSpinBox.setSingleStep(5)
        self.dac8ThresholdSpinBox.setValue(0)

        dac1Layout = QHBoxLayout()
        dac1Layout.addWidget(self.dacButton1)
        dac1Layout.addStretch(1)
        dac1Layout.addWidget(self.dac1ThresholdSpinBox)
        dac1Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        dac2Layout = QHBoxLayout()
        dac2Layout.addWidget(self.dacButton2)
        dac2Layout.addStretch(1)
        dac2Layout.addWidget(self.dac2ThresholdSpinBox)
        dac2Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        dac3Layout = QHBoxLayout()
        dac3Layout.addWidget(self.dacButton3)
        dac3Layout.addStretch(1)
        dac3Layout.addWidget(self.dac3ThresholdSpinBox)
        dac3Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        dac4Layout = QHBoxLayout()
        dac4Layout.addWidget(self.dacButton4)
        dac4Layout.addStretch(1)
        dac4Layout.addWidget(self.dac4ThresholdSpinBox)
        dac4Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        dac5Layout = QHBoxLayout()
        dac5Layout.addWidget(self.dacButton5)
        dac5Layout.addStretch(1)
        dac5Layout.addWidget(self.dac5ThresholdSpinBox)
        dac5Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        dac6Layout = QHBoxLayout()
        dac6Layout.addWidget(self.dacButton6)
        dac6Layout.addStretch(1)
        dac6Layout.addWidget(self.dac6ThresholdSpinBox)
        dac6Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        dac7Layout = QHBoxLayout()
        dac7Layout.addWidget(self.dacButton7)
        dac7Layout.addStretch(1)
        dac7Layout.addWidget(self.dac7ThresholdSpinBox)
        dac7Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        dac8Layout = QHBoxLayout()
        dac8Layout.addWidget(self.dacButton8)
        dac8Layout.addStretch(1)
        dac8Layout.addWidget(self.dac8ThresholdSpinBox)
        dac8Layout.addWidget(QLabel(constants.QSTRING_MU_SYMBOL + "V"))

        self.dac1ThresholdSpinBox.valueChanged.connect(self.setDacThreshold1)
        self.dac2ThresholdSpinBox.valueChanged.connect(self.setDacThreshold2)
        self.dac3ThresholdSpinBox.valueChanged.connect(self.setDacThreshold3)
        self.dac4ThresholdSpinBox.valueChanged.connect(self.setDacThreshold4)
        self.dac5ThresholdSpinBox.valueChanged.connect(self.setDacThreshold5)
        self.dac6ThresholdSpinBox.valueChanged.connect(self.setDacThreshold6)
        self.dac7ThresholdSpinBox.valueChanged.connect(self.setDacThreshold7)
        self.dac8ThresholdSpinBox.valueChanged.connect(self.setDacThreshold8)

        dacMainLayout = QVBoxLayout()
        dacMainLayout.addLayout(dacGainLayout)
        dacMainLayout.addLayout(dacNoiseSuppressLayout)
        dacMainLayout.addLayout(dacControlLayout)
        dacMainLayout.addLayout(dacHeadingLayout)
        dacMainLayout.addLayout(dac1Layout)
        dacMainLayout.addLayout(dac2Layout)
        dacMainLayout.addLayout(dac3Layout)
        dacMainLayout.addLayout(dac4Layout)
        dacMainLayout.addLayout(dac5Layout)
        dacMainLayout.addLayout(dac6Layout)
        dacMainLayout.addLayout(dac7Layout)
        dacMainLayout.addLayout(dac8Layout)
        dacMainLayout.addStretch(1)
        # dacMainLayout.addWidget(dacLockToSelectedBox)

        frameTab3.setLayout(dacMainLayout)

        configLayout = QVBoxLayout()
        self.scanButton = QPushButton("Rescan Ports A-D")
        self.setCableDelayButton = QPushButton("Manual")
        self.digOutButton = QPushButton("Configure Realtime Control")
        self.fastSettleCheckBox = QCheckBox("Manual")
        self.externalFastSettleCheckBox = QCheckBox("Realtime Settle Control:")
        self.externalFastSettleSpinBox = QSpinBox()
        self.externalFastSettleSpinBox.setRange(0, 15)
        self.externalFastSettleSpinBox.setSingleStep(1)
        self.externalFastSettleSpinBox.setValue(0)

        scanLayout = QHBoxLayout()
        scanLayout.addWidget(self.scanButton)
        scanLayout.addStretch(1)
        scanLayout.addWidget(self.setCableDelayButton)

        scanGroupBox = QGroupBox("Connected RHD2000 Amplifiers")
        scanGroupBox.setLayout(scanLayout)

        digOutLayout = QHBoxLayout()
        digOutLayout.addWidget(self.digOutButton)
        digOutLayout.addStretch(1)

        digOutGroupBox = QGroupBox("Auxiliary Digital Output Pins")
        digOutGroupBox.setLayout(digOutLayout)

        configTopLayout = QHBoxLayout()
        configTopLayout.addWidget(scanGroupBox)
        configTopLayout.addWidget(digOutGroupBox)

        fastSettleLayout = QHBoxLayout()
        fastSettleLayout.addWidget(self.fastSettleCheckBox)
        fastSettleLayout.addStretch(1)
        fastSettleLayout.addWidget(self.externalFastSettleCheckBox)
        fastSettleLayout.addWidget(QLabel("DIN"))
        fastSettleLayout.addWidget(self.externalFastSettleSpinBox)
        fastSettleLayout.addWidget(self.helpDialogSettleButton)

        fastSettleGroupBox = QGroupBox("Amplifier Fast Settle (Blanking)")
        fastSettleGroupBox.setLayout(fastSettleLayout)

        self.note1LineEdit = QLineEdit()
        self.note2LineEdit = QLineEdit()
        self.note3LineEdit = QLineEdit()
        # Note: default maxLength of a QLineEdit is 32767
        self.note1LineEdit.setMaxLength(255)
        self.note2LineEdit.setMaxLength(255)
        self.note3LineEdit.setMaxLength(255)

        notesLayout = QVBoxLayout()
        notesLayout.addWidget(
            QLabel("The following text will be appended to saved data files."))
        notesLayout.addWidget(QLabel("Note 1:"))
        notesLayout.addWidget(self.note1LineEdit)
        notesLayout.addWidget(QLabel("Note 2:"))
        notesLayout.addWidget(self.note2LineEdit)
        notesLayout.addWidget(QLabel("Note 3:"))
        notesLayout.addWidget(self.note3LineEdit)
        notesLayout.addStretch(1)

        notesGroupBox = QGroupBox("Notes")
        notesGroupBox.setLayout(notesLayout)

        configLayout.addLayout(configTopLayout)
        configLayout.addWidget(fastSettleGroupBox)
        configLayout.addWidget(notesGroupBox)
        configLayout.addStretch(1)

        frameTab4.setLayout(configLayout)

        self.scanButton.clicked.connect(self.scanPorts)
        self.setCableDelayButton.clicked.connect(self.manualCableDelayControl)
        self.digOutButton.clicked.connect(self.configDigOutControl)
        self.fastSettleCheckBox.stateChanged.connect(self.enableFastSettle)
        self.externalFastSettleCheckBox.toggled.connect(
            self.enableExternalFastSettle)
        self.externalFastSettleSpinBox.valueChanged.connect(
            self.setExternalFastSettleChannel)

        tabWidget1 = QTabWidget()
        tabWidget1.addTab(frameTab1, "Bandwidth")
        tabWidget1.addTab(frameTab2, "Impedance")
        tabWidget1.addTab(frameTab3, "DAC/Audio")
        tabWidget1.addTab(frameTab4, "Configure")

        self.dspCutoffFreqLabel = QLabel("0.00 Hz")
        self.lowerBandwidthLabel = QLabel("0.00 Hz")
        self.upperBandwidthLabel = QLabel("0.00 kHz")

        sampleRateLayout = QHBoxLayout()
        sampleRateLayout.addWidget(QLabel("Amplifier Sampling Rate"))
        sampleRateLayout.addWidget(self.sampleRateComboBox)
        sampleRateLayout.addStretch(1)

        changeBandwidthLayout = QHBoxLayout()
        changeBandwidthLayout.addWidget(self.changeBandwidthButton)
        changeBandwidthLayout.addStretch(1)
        changeBandwidthLayout.addWidget(self.helpDialogChipFiltersButton)

        bandwidthLayout = QVBoxLayout()
        bandwidthLayout.addWidget(self.dspCutoffFreqLabel)
        bandwidthLayout.addWidget(self.lowerBandwidthLabel)
        bandwidthLayout.addWidget(self.upperBandwidthLabel)
        bandwidthLayout.addLayout(changeBandwidthLayout)

        bandwidthGroupBox = QGroupBox("Amplifier Hardware Bandwidth")
        bandwidthGroupBox.setLayout(bandwidthLayout)

        self.highpassFilterCheckBox = QCheckBox(
            "Software/DAC High-Pass Filter")
        self.highpassFilterCheckBox.clicked.connect(self.enableHighpassFilter)

        self.highpassFilterLineEdit = QLineEdit(
            "%.0f" % self.highpassFilterFrequency)
        self.highpassFilterLineEdit.setValidator(
            QDoubleValidator(0.01, 9999.99, 2, self))
        self.highpassFilterLineEdit.textChanged.connect(
            self.highpassFilterLineEditChanged)

        highpassFilterLayout = QHBoxLayout()
        highpassFilterLayout.addWidget(self.highpassFilterCheckBox)
        highpassFilterLayout.addWidget(self.highpassFilterLineEdit)
        highpassFilterLayout.addWidget(QLabel("Hz"))
        highpassFilterLayout.addStretch(1)
        highpassFilterLayout.addWidget(self.helpDialogHighpassFilterButton)

        notchFilterLayout = QHBoxLayout()
        notchFilterLayout.addWidget(QLabel("Notch Filter Setting"))
        notchFilterLayout.addWidget(self.notchFilterComboBox)
        notchFilterLayout.addStretch(1)
        notchFilterLayout.addWidget(self.helpDialogNotchFilterButton)

        offchipFilterLayout = QVBoxLayout()
        offchipFilterLayout.addLayout(highpassFilterLayout)
        offchipFilterLayout.addLayout(notchFilterLayout)

        notchFilterGroupBox = QGroupBox("Software Filters")
        notchFilterGroupBox.setLayout(offchipFilterLayout)

        self.plotPointsCheckBox = QCheckBox(
            "Plot Points Only to Reduce CPU Load")
        self.plotPointsCheckBox.clicked.connect(self.plotPointsMode)

        cpuLoadLayout = QVBoxLayout()
        cpuLoadLayout.addWidget(self.plotPointsCheckBox)
        cpuLoadLayout.addStretch(1)

        cpuLoadGroupBox = QGroupBox("CPU Load Management")
        cpuLoadGroupBox.setLayout(cpuLoadLayout)

        freqLayout = QVBoxLayout()
        freqLayout.addLayout(sampleRateLayout)
        freqLayout.addWidget(bandwidthGroupBox)
        freqLayout.addWidget(notchFilterGroupBox)
        freqLayout.addWidget(cpuLoadGroupBox)
        freqLayout.addStretch(1)

        frameTab1.setLayout(freqLayout)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(groupBox1)
        leftLayout.addWidget(tabWidget1)
        leftLayout.addStretch(1)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addWidget(self.wavePlot)
        mainLayout.setStretch(0, 0)
        mainLayout.setStretch(1, 1)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        screenRect = QApplication.desktop().screenGeometry()
        self.setCentralWidget(mainWidget)
        self.adjustSize()

        # If the screen height has less than 100 pixels to spare at the current size of mainWidget,
        # or if the screen width has less than 100 pixels to spare, put mainWidget inside a QScrollArea

        if screenRect.height() < mainWidget.height() + 100 or screenRect.width() < mainWidget.width() + 100:
            scrollArea = QScrollArea()
            scrollArea.setWidget(mainWidget)
            self.setCentralWidget(scrollArea)

            if screenRect.height() < mainWidget.height() + 100:
                self.setMinimumHeight(screenRect.height() - 100)
            else:
                self.setMinimumHeight(mainWidget.height() + 50)

            if screenRect.width() < mainWidget.width() + 100:
                self.setMinimumWidth(screenRect.width() - 100)
            else:
                self.setMinimumWidth(mainWidget.width() + 50)

        self.wavePlot.setFocus()

    def createActions(self):
        """Create the menu actions"""
        self.loadSettingsAction = QAction("Load Settings", self)
        self.loadSettingsAction.setShortcut("Ctrl+O")
        self.loadSettingsAction.triggered.connect(self.loadSettings)

        self.saveSettingsAction = QAction("Save Settings", self)
        self.saveSettingsAction.setShortcut("Ctrl+S")
        self.saveSettingsAction.triggered.connect(self.saveSettings)

        self.exitAction = QAction("E&xit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.triggered.connect(self.close)

        self.originalOrderAction = QAction(
            "Restore Original Channel Order", self)
        self.originalOrderAction.triggered.connect(
            self.restoreOriginalChannelOrder)

        self.alphaOrderAction = QAction("Order Channels Alphabetically", self)
        self.alphaOrderAction.triggered.connect(self.alphabetizeChannels)

        self.aboutAction = QAction("&About Intan GUI...", self)
        self.aboutAction.triggered.connect(self.about)

        self.keyboardHelpAction = QAction("&Keyboard Shortcuts...", self)
        self.keyboardHelpAction.setShortcut("F1")
        self.keyboardHelpAction.triggered.connect(self.keyboardShortcutsHelp)

        self.intanWebsiteAction = QAction("Visit Intan Website...", self)
        self.intanWebsiteAction.triggered.connect(self.openIntanWebsite)

        self.renameChannelAction = QAction("Rename Channel", self)
        self.renameChannelAction.setShortcut("Ctrl+R")
        self.renameChannelAction.triggered.connect(self.renameChannel)

        self.toggleChannelEnableAction = QAction(
            "Enable/Disable Channel", self)
        self.toggleChannelEnableAction.setShortcut("Space")
        self.toggleChannelEnableAction.triggered.connect(
            self.toggleChannelEnable)

        self.enableAllChannelsAction = QAction(
            "Enable all Channels on Port", self)
        self.enableAllChannelsAction.triggered.connect(self.enableAllChannels)

        self.disableAllChannelsAction = QAction(
            "Disable all Channels on Port", self)
        self.disableAllChannelsAction.triggered.connect(
            self.disableAllChannels)

    def createMenus(self):
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(self.loadSettingsAction)
        fileMenu.addAction(self.saveSettingsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        channelMenu = menuBar.addMenu("&Channels")
        channelMenu.addAction(self.renameChannelAction)
        channelMenu.addAction(self.toggleChannelEnableAction)
        channelMenu.addAction(self.enableAllChannelsAction)
        channelMenu.addAction(self.disableAllChannelsAction)
        channelMenu.addSeparator()
        channelMenu.addAction(self.originalOrderAction)
        channelMenu.addAction(self.alphaOrderAction)

        menuBar.addSeparator()

        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.keyboardHelpAction)
        helpMenu.addSeparator()
        helpMenu.addAction(self.intanWebsiteAction)
        helpMenu.addAction(self.aboutAction)

    def createStatusBar(self):
        self.statusBarLabel = QLabel("")
        statusBar = self.statusBar()
        statusBar.addWidget(self.statusBarLabel, 1)
        statusBar.setSizeGripEnabled(False)

    # Display "About" message box.
    def about(self):
        QMessageBox.about(self, "About Intan Technologies RHD2000 Interface",
                          "<h2>Intan Technologies RHD2000 Interface</h2>"
                          "<p>Version 1.5.2"
                          "<p>Copyright &copy 2013-2017 Intan Technologies"
                          "<p>self biopotential recording application controls the RHD2000 "
                          "USB Interface Board from Intan Technologies.  The C++/Qt source code "
                          "for self application is freely available from Intan Technologies. "
                          "For more information visit <i>http:#www.intantech.com</i>."
                          "<p>self program is free software: you can redistribute it and/or modify "
                          "it under the terms of the GNU Lesser General Public License as published "
                          "by the Free Software Foundation, either version 3 of the License, or "
                          "(at your option) any later version."
                          "<p>self program is distributed in the hope that it will be useful, "
                          "but WITHOUT ANY WARRANTY without even the implied warranty of "
                          "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
                          "GNU Lesser General Public License for more details."
                          "<p>You should have received a copy of the GNU Lesser General Public License "
                          "along with self program.  If not, see <i>http:#www.gnu.org/licenses/</i>.")

    # Display keyboard shortcut window.
    def keyboardShortcutsHelp(self):
        if not self.keyboardShortcutDialog:
            self.keyboardShortcutDialog = KeyboardShortcutDialog(self)
        self.keyboardShortcutDialog.show()
        self.keyboardShortcutDialog.raise_()
        self.keyboardShortcutDialog.activateWindow()
        self.wavePlot.setFocus()

    # Display on-chip filters help menu.
    def chipFiltersHelp(self):
        if not self.helpDialogChipFilters:
            self.helpDialogChipFilters = HelpDialogChipFilters(self)
        self.helpDialogChipFilters.show()
        self.helpDialogChipFilters.raise_()
        self.helpDialogChipFilters.activateWindow()
        self.wavePlot.setFocus()

    # Display comparators help menu.
    def comparatorsHelp(self):
        if not self.helpDialogComparators:
            self.helpDialogComparators = HelpDialogComparators(self)
        self.helpDialogComparators.show()
        self.helpDialogComparators.raise_()
        self.helpDialogComparators.activateWindow()
        self.wavePlot.setFocus()

    # Display DACs help menu.
    def dacsHelp(self):
        if not self.helpDialogDacs:
            self.helpDialogDacs = HelpDialogDacs(self)
        self.helpDialogDacs.show()
        self.helpDialogDacs.raise_()
        self.helpDialogDacs.activateWindow()
        self.wavePlot.setFocus()

    # Display software/DAC high-pass filter help menu.
    def highpassFilterHelp(self):
        if not self.helpDialogHighpassFilter:
            self.helpDialogHighpassFilter = HelpDialogHighpassFilter(self)
        self.helpDialogHighpassFilter.show()
        self.helpDialogHighpassFilter.raise_()
        self.helpDialogHighpassFilter.activateWindow()
        self.wavePlot.setFocus()

    # Display software notch filter help menu.
    def notchFilterHelp(self):
        if not self.helpDialogNotchFilter:
            self.helpDialogNotchFilter = HelpDialogNotchFilter(self)
        self.helpDialogNotchFilter.show()
        self.helpDialogNotchFilter.raise_()
        self.helpDialogNotchFilter.activateWindow()
        self.wavePlot.setFocus()

    # Display fast settle help menu.
    def fastSettleHelp(self):
        if not self.helpDialogFastSettle:
            self.helpDialogFastSettle = HelpDialogFastSettle(self)
        self.helpDialogFastSettle.show()
        self.helpDialogFastSettle.raise_()
        self.helpDialogFastSettle.activateWindow()
        self.wavePlot.setFocus()

    def closeEvent(self, event):
        # Perform any clean-up here before application closes.
        if self.running:
            self.stopInterfaceBoard()  # stop SPI communication before we exit
        event.accept()

    # Change the number of waveform frames displayed on the screen.
    def changeNumFrames(self, index):
        self.wavePlot.setNumFrames(self.numFramesComboBox.currentIndex())
        self.numFramesComboBox.setCurrentIndex(index)
        self.wavePlot.setFocus()

    # Change voltage scale of waveform plots.
    def changeYScale(self, index):
        self.wavePlot.setYScale(self.yScaleList[index])
        self.wavePlot.setFocus()

    # Change time scale of waveform plots.
    def changeTScale(self, index):
        self.wavePlot.setTScale(self.tScaleList[index])
        self.wavePlot.setFocus()

    # Launch amplifier bandwidth selection dialog and set new bandwidth.
    def changeBandwidth(self):
        bandwidthDialog = BandwidthDialog(self.desiredLowerBandwidth, self.desiredUpperBandwidth,
                                          self.desiredDspCutoffFreq, self.dspEnabled, self.boardSampleRate, self)
        if bandwidthDialog.exec():
            self.desiredDspCutoffFreq = float(
                bandwidthDialog.dspFreqLineEdit.text())
            self.desiredLowerBandwidth = float(
                bandwidthDialog.lowFreqLineEdit.text())
            self.desiredUpperBandwidth = float(
                bandwidthDialog.highFreqLineEdit.text())
            self.dspEnabled = bandwidthDialog.dspEnableCheckBox.isChecked()
            # self function sets new amp bandwidth
            self.changeSampleRate(self.sampleRateComboBox.currentIndex())
        self.wavePlot.setFocus()

    # Launch electrode impedance measurement frequency selection dialog.
    def changeImpedanceFrequency(self):
        impedanceFreqDialog = ImpedanceFreqDialog(self.desiredImpedanceFreq, self.actualLowerBandwidth, self.actualUpperBandwidth,
                                                  self.actualDspCutoffFreq, self.dspEnabled, self.boardSampleRate, self)
        if impedanceFreqDialog.exec():
            self.desiredImpedanceFreq = float(
                impedanceFreqDialog.impedanceFreqLineEdit.text())
            self.updateImpedanceFrequency()
        self.wavePlot.setFocus()

    # Update electrode impedance measurement frequency, after checking that
    # requested test frequency lies within acceptable ranges based on the
    # amplifier bandwidth and the sampling rate.  See impedancefreqdialog.cpp
    # for more information.
    def updateImpedanceFrequency(self):
        upperBandwidthLimit = self.actualUpperBandwidth / 1.5
        lowerBandwidthLimit = self.actualLowerBandwidth * 1.5
        if self.dspEnabled:
            if self.actualDspCutoffFreq > self.actualLowerBandwidth:
                lowerBandwidthLimit = self.actualDspCutoffFreq * 1.5

        if self.desiredImpedanceFreq > 0.0:
            self.desiredImpedanceFreqLabel.setText("Desired Impedance Test Frequency: " +
                                                   "%.0f" % self.desiredImpedanceFreq +
                                                   " Hz")
            impedancePeriod = round(
                self.boardSampleRate / self.desiredImpedanceFreq)
            if impedancePeriod >= 4 and impedancePeriod <= 1024 and self.desiredImpedanceFreq >= lowerBandwidthLimit and self.desiredImpedanceFreq <= upperBandwidthLimit:
                actualImpedanceFreq = self.boardSampleRate / impedancePeriod
                self.impedanceFreqValid = True
            else:
                actualImpedanceFreq = 0.0
                self.impedanceFreqValid = False

        else:
            self.desiredImpedanceFreqLabel.setText(
                "Desired Impedance Test Frequency: -")
            actualImpedanceFreq = 0.0
            self.impedanceFreqValid = False
        if self.impedanceFreqValid:
            self.actualImpedanceFreqLabel.setText("Actual Impedance Test Frequency: " +
                                                  "%.1f" % actualImpedanceFreq +
                                                  " Hz")
        else:
            self.actualImpedanceFreqLabel.setText(
                "Actual Impedance Test Frequency: -")
        self.runImpedanceTestButton.setEnabled(self.impedanceFreqValid)

    # Rename selected channel.
    def renameChannel(self):
        renameChannelDialog = RenameChannelDialog(self.wavePlot.getNativeChannelName(),
                                                  self.wavePlot.getChannelName(), self)
        if renameChannelDialog.exec():
            newChannelName = renameChannelDialog.nameLineEdit.text()
            self.wavePlot.setChannelName(newChannelName)
            self.wavePlot.refreshScreen()
        self.wavePlot.setFocus()

    def sortChannelsByName(self):
        self.wavePlot.sortChannelsByName()
        self.wavePlot.refreshScreen()
        self.wavePlot.setFocus()

    def sortChannelsByNumber(self):
        self.wavePlot.sortChannelsByNumber()
        self.wavePlot.refreshScreen()
        self.wavePlot.setFocus()

    def restoreOriginalChannelOrder(self):
        self.wavePlot.sortChannelsByNumber()
        self.wavePlot.refreshScreen()
        self.wavePlot.setFocus()

    def alphabetizeChannels(self):
        self.wavePlot.sortChannelsByName()
        self.wavePlot.refreshScreen()
        self.wavePlot.setFocus()

    def toggleChannelEnable(self):
        self.wavePlot.toggleSelectedChannelEnable()
        self.wavePlot.setFocus()

    def enableAllChannels(self):
        self.wavePlot.enableAllChannels()
        self.wavePlot.setFocus()

    def disableAllChannels(self):
        self.wavePlot.disableAllChannels()
        self.wavePlot.setFocus()

    def changePort(self, port):
        self.wavePlot.setPort(port)
        self.wavePlot.setFocus()

    def changeDacGain(self, index):
        if not self.synthMode:
            self.evalBoard.setDacGain(index)
        self.setDacGainLabel(index)
        self.wavePlot.setFocus()

    def setDacGainLabel(self, gain):
        self.dacGainLabel.setText(str(515 * math.pow(2.0, gain)) + " V/V")

    def changeDacNoiseSuppress(self, index):
        if not self.synthMode:
            self.evalBoard.setAudioNoiseSuppress(index)
        self.setDacNoiseSuppressLabel(index)
        self.wavePlot.setFocus()

    def setDacNoiseSuppressLabel(self, noiseSuppress):
        self.dacNoiseSuppressLabel.setText("+/-" +
                                           "%.0f" % (3.12 * noiseSuppress) +
                                           " " + constants.QSTRING_MU_SYMBOL + "V")

    # Enable or disable DAC on USB interface board.
    def dacEnable(self, enable):
        dacChannel = self.dacButtonGroup.checkedId()
        self.dacEnabled[dacChannel] = enable
        if not self.synthMode:
            self.evalBoard.enableDac(dacChannel, enable)
        if self.dacSelectedChannel[dacChannel]:
            self.setDacChannelLabel(dacChannel, self.dacSelectedChannel[dacChannel].customChannelName,
                                    self.dacSelectedChannel[dacChannel].nativeChannelName)
        else:
            self.setDacChannelLabel(dacChannel, "n/a", "n/a")

        self.wavePlot.setFocus()

    # Route selected amplifier channel to selected DAC.
    def dacSetChannel(self):
        dacChannel = self.dacButtonGroup.checkedId()
        selectedChannel = self.wavePlot.selectedChannel()
        if selectedChannel.signalType == constants.AmplifierSignal:
            # If DAC is not yet enabled, enable it.
            if not self.dacEnabled[dacChannel]:
                self.dacEnableCheckBox.setChecked(True)
                self.dacEnable(True)
            # Set DAC to selected channel and label it accordingly.
            self.dacSelectedChannel[dacChannel] = selectedChannel
            if not self.synthMode:
                self.evalBoard.selectDacDataStream(
                    dacChannel, selectedChannel.boardStream)
                self.evalBoard.selectDacDataChannel(
                    dacChannel, selectedChannel.chipChannel)
            self.setDacChannelLabel(dacChannel, selectedChannel.customChannelName,
                                    selectedChannel.nativeChannelName)

        self.wavePlot.setFocus()

    def dacSelected(self, dacChannel):
        self.dacEnableCheckBox.setChecked(self.dacEnabled[dacChannel])
        self.wavePlot.setFocus()

    # Label DAC selection button in GUI with selected amplifier channel.
    def setDacChannelLabel(self, dacChannel, channel, name):
        text = "DAC " + str(dacChannel + 1)
        if dacChannel == 0:
            text += " (Audio L)"
        if dacChannel == 1:
            text += " (Audio R)"
        text += ": "
        if self.dacEnabled[dacChannel]:
            text += name + " (" + channel + ")"
        else:
            text += "off"

        if dacChannel == 0:
            self.dacButton1.setText(text)
        elif dacChannel == 1:
            self.dacButton2.setText(text)
        elif dacChannel == 2:
            self.dacButton3.setText(text)
        elif dacChannel == 3:
            self.dacButton4.setText(text)
        elif dacChannel == 4:
            self.dacButton5.setText(text)
        elif dacChannel == 5:
            self.dacButton6.setText(text)
        elif dacChannel == 6:
            self.dacButton7.setText(text)
        elif dacChannel == 7:
            self.dacButton8.setText(text)

    # Change notch filter settings.
    def changeNotchFilter(self, notchFilterIndex):
        if notchFilterIndex == 0:
            self.notchFilterEnabled = False
        elif notchFilterIndex == 1:
            self.notchFilterFrequency = 50.0
            self.notchFilterEnabled = True
        elif notchFilterIndex == 2:
            self.notchFilterFrequency = 60.0
            self.notchFilterEnabled = True

        self.signalProcessor.setNotchFilter(
            self.notchFilterFrequency, self.notchFilterBandwidth, self.boardSampleRate)
        self.signalProcessor.setNotchFilterEnabled(self.notchFilterEnabled)
        self.wavePlot.setFocus()

    # Enable/disable software/FPGA high-pass filter.
    def enableHighpassFilter(self, enable):
        self.highpassFilterEnabled = enable
        self.signalProcessor.setHighpassFilterEnabled(enable)
        if not self.synthMode:
            self.evalBoard.enableDacHighpassFilter(enable)
        self.wavePlot.setFocus()

    # Update software/FPGA high-pass filter when LineEdit changes.
    def highpassFilterLineEditChanged(self):
        self.setHighpassFilterCutoff(float(self.highpassFilterLineEdit.text()))

    # Update software/FPGA high-pass filter cutoff frequency.
    def setHighpassFilterCutoff(self, cutoff):
        self.highpassFilterFrequency = cutoff
        self.signalProcessor.setHighpassFilter(cutoff, self.boardSampleRate)
        if not self.synthMode:
            self.evalBoard.setDacHighpassFilter(cutoff)

    def changeSampleRate(self, sampleRateIndex):
        self.sampleRate = Rhd2000EvalBoard.SampleRate1000Hz

        # Note: numUsbBlocksToRead is set to give an approximate frame rate of
        # 30 Hz for most sampling rates.
        if sampleRateIndex == 0:
            self.sampleRate = Rhd2000EvalBoard.SampleRate1000Hz
            self.boardSampleRate = 1000.0
            self.numUsbBlocksToRead = 1
        elif sampleRateIndex == 1:
            self.sampleRate = Rhd2000EvalBoard.SampleRate1250Hz
            self.boardSampleRate = 1250.0
            self.numUsbBlocksToRead = 1
        elif sampleRateIndex == 2:
            self.sampleRate = Rhd2000EvalBoard.SampleRate1500Hz
            self.boardSampleRate = 1500.0
            self.numUsbBlocksToRead = 1
        elif sampleRateIndex == 3:
            self.sampleRate = Rhd2000EvalBoard.SampleRate2000Hz
            self.boardSampleRate = 2000.0
            self.numUsbBlocksToRead = 1
        elif sampleRateIndex == 4:
            self.sampleRate = Rhd2000EvalBoard.SampleRate2500Hz
            self.boardSampleRate = 2500.0
            self.numUsbBlocksToRead = 2
        elif sampleRateIndex == 5:
            self.sampleRate = Rhd2000EvalBoard.SampleRate3000Hz
            self.boardSampleRate = 3000.0
            self.numUsbBlocksToRead = 2
        elif sampleRateIndex == 6:
            self.sampleRate = Rhd2000EvalBoard.SampleRate3333Hz
            self.boardSampleRate = 10000.0 / 3.0
            self.numUsbBlocksToRead = 2
        elif sampleRateIndex == 7:
            self.sampleRate = Rhd2000EvalBoard.SampleRate4000Hz
            self.boardSampleRate = 4000.0
            self.numUsbBlocksToRead = 2
        elif sampleRateIndex == 8:
            self.sampleRate = Rhd2000EvalBoard.SampleRate5000Hz
            self.boardSampleRate = 5000.0
            self.numUsbBlocksToRead = 3
        elif sampleRateIndex == 9:
            self.sampleRate = Rhd2000EvalBoard.SampleRate6250Hz
            self.boardSampleRate = 6250.0
            self.numUsbBlocksToRead = 4
        elif sampleRateIndex == 10:
            self.sampleRate = Rhd2000EvalBoard.SampleRate8000Hz
            self.boardSampleRate = 8000.0
            self.numUsbBlocksToRead = 4
        elif sampleRateIndex == 11:
            self.sampleRate = Rhd2000EvalBoard.SampleRate10000Hz
            self.boardSampleRate = 10000.0
            self.numUsbBlocksToRead = 6
        elif sampleRateIndex == 12:
            self.sampleRate = Rhd2000EvalBoard.SampleRate12500Hz
            self.boardSampleRate = 12500.0
            self.numUsbBlocksToRead = 7
        elif sampleRateIndex == 13:
            self.sampleRate = Rhd2000EvalBoard.SampleRate15000Hz
            self.boardSampleRate = 15000.0
            self.numUsbBlocksToRead = 8
        elif sampleRateIndex == 14:
            self.sampleRate = Rhd2000EvalBoard.SampleRate20000Hz
            self.boardSampleRate = 20000.0
            self.numUsbBlocksToRead = 12
        elif sampleRateIndex == 15:
            self.sampleRate = Rhd2000EvalBoard.SampleRate25000Hz
            self.boardSampleRate = 25000.0
            self.numUsbBlocksToRead = 14
        elif sampleRateIndex == 16:
            self.sampleRate = Rhd2000EvalBoard.SampleRate30000Hz
            self.boardSampleRate = 30000.0
            self.numUsbBlocksToRead = 16

        self.wavePlot.setNumUsbBlocksToPlot(self.numUsbBlocksToRead)

        # Set up an RHD2000 register object using self sample rate to
        # optimize MUX-related register settings.
        chipRegisters = Rhd2000Registers(self.boardSampleRate)

        if not self.synthMode:
            self.evalBoard.setSampleRate(self.sampleRate)

            # Now that we have set our sampling rate, we can set the MISO sampling delay
            # which is dependent on the sample rate.
            if self.manualDelayEnabled[0]:
                self.evalBoard.setCableDelay(
                    Rhd2000EvalBoard.PortA, self.manualDelay[0])
            else:
                self.evalBoard.setCableLengthMeters(
                    Rhd2000EvalBoard.PortA, self.cableLengthPortA)

            if self.manualDelayEnabled[1]:
                self.evalBoard.setCableDelay(
                    Rhd2000EvalBoard.PortB, self.manualDelay[1])
            else:
                self.evalBoard.setCableLengthMeters(
                    Rhd2000EvalBoard.PortB, self.cableLengthPortB)

            if self.manualDelayEnabled[2]:
                self.evalBoard.setCableDelay(
                    Rhd2000EvalBoard.PortC, self.manualDelay[2])
            else:
                self.evalBoard.setCableLengthMeters(
                    Rhd2000EvalBoard.PortC, self.cableLengthPortC)

            if self.manualDelayEnabled[3]:
                self.evalBoard.setCableDelay(
                    Rhd2000EvalBoard.PortD, self.manualDelay[3])
            else:
                self.evalBoard.setCableLengthMeters(
                    Rhd2000EvalBoard.PortD, self.cableLengthPortD)

            # Create command lists to be uploaded to auxiliary command slots.

            # Create a command list for the AuxCmd1 slot.  self command sequence will create a 250 Hz,
            # zero-amplitude sine wave (i.e., a flatline).  We will change self when we want to perform
            # impedance testing.
            # commandSequenceLength = chipRegisters.createCommandListZcheckDac(commandList, 250.0, 0.0)

            # Create a command list for the AuxCmd1 slot.  self command sequence will continuously
            # update Register 3, which controls the auxiliary digital output pin on each RHD2000 chip.
            # In concert with the v1.4 Rhythm FPGA code, self permits real-time control of the digital
            # output pin on chips on each SPI port.
            # Take auxiliary output out of HiZ mode.

            commandList = VectorInt()
            chipRegisters.setDigOutLow()
            commandSequenceLength = chipRegisters.createCommandListUpdateDigOut(
                commandList)
            self.evalBoard.uploadCommandList(
                commandList, Rhd2000EvalBoard.AuxCmd1, 0)
            self.evalBoard.selectAuxCommandLength(
                Rhd2000EvalBoard.AuxCmd1, 0, commandSequenceLength - 1)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd1, 0)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd1, 0)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd1, 0)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd1, 0)

            # Next, we'll create a command list for the AuxCmd2 slot.  self command sequence
            # will sample the temperature sensor and other auxiliary ADC inputs.

            commandSequenceLength = chipRegisters.createCommandListTempSensor(
                commandList)
            self.evalBoard.uploadCommandList(
                commandList, Rhd2000EvalBoard.AuxCmd2, 0)
            self.evalBoard.selectAuxCommandLength(
                Rhd2000EvalBoard.AuxCmd2, 0, commandSequenceLength - 1)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd2, 0)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd2, 0)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd2, 0)
            self.evalBoard.selectAuxCommandBank(
                Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd2, 0)

            # For the AuxCmd3 slot, we will create three command sequences.  All sequences
            # will configure and read back the RHD2000 chip registers, but one sequence will
            # also run ADC calibration.  Another sequence will enable amplifier 'fast settle'.

        # Before generating register configuration command sequences, set amplifier
        # bandwidth paramters.

        self.actualDspCutoffFreq = chipRegisters.setDspCutoffFreq(
            self.desiredDspCutoffFreq)
        self.actualLowerBandwidth = chipRegisters.setLowerBandwidth(
            self.desiredLowerBandwidth)
        self.actualUpperBandwidth = chipRegisters.setUpperBandwidth(
            self.desiredUpperBandwidth)
        chipRegisters.enableDsp(self.dspEnabled)

        if self.dspEnabled:
            self.dspCutoffFreqLabel.setText("Desired/Actual DSP Cutoff: " +
                                            "%.2f" % self.desiredDspCutoffFreq + " Hz / " +
                                            "%.2f" % self.actualDspCutoffFreq + " Hz")
        else:
            self.dspCutoffFreqLabel.setText(
                "Desired/Actual DSP Cutoff: DSP disabled")

        self.lowerBandwidthLabel.setText("Desired/Actual Lower Bandwidth: " +
                                         "%.2f" % self.desiredLowerBandwidth + " Hz / " +
                                         "%.2f" % self.actualLowerBandwidth + " Hz")
        self.upperBandwidthLabel.setText("Desired/Actual Upper Bandwidth: " +
                                         "%.2f" % (self.desiredUpperBandwidth / 1000.0) + " kHz / " +
                                         "%.2f" % (self.actualUpperBandwidth / 1000.0) + " kHz")

        if not self.synthMode:
            chipRegisters.createCommandListRegisterConfig(commandList, True)
            # Upload version with ADC calibration to AuxCmd3 RAM Bank 0.
            self.evalBoard.uploadCommandList(
                commandList, Rhd2000EvalBoard.AuxCmd3, 0)
            self.evalBoard.selectAuxCommandLength(Rhd2000EvalBoard.AuxCmd3, 0,
                                                  commandSequenceLength - 1)

            commandSequenceLength = chipRegisters.createCommandListRegisterConfig(
                commandList, False)
            # Upload version with no ADC calibration to AuxCmd3 RAM Bank 1.
            self.evalBoard.uploadCommandList(
                commandList, Rhd2000EvalBoard.AuxCmd3, 1)
            self.evalBoard.selectAuxCommandLength(Rhd2000EvalBoard.AuxCmd3, 0,
                                                  commandSequenceLength - 1)

            chipRegisters.setFastSettle(True)
            commandSequenceLength = chipRegisters.createCommandListRegisterConfig(
                commandList, False)
            # Upload version with fast settle enabled to AuxCmd3 RAM Bank 2.
            self.evalBoard.uploadCommandList(
                commandList, Rhd2000EvalBoard.AuxCmd3, 2)
            self.evalBoard.selectAuxCommandLength(Rhd2000EvalBoard.AuxCmd3, 0,
                                                  commandSequenceLength - 1)
            chipRegisters.setFastSettle(False)

            if self.fastSettleEnabled:
                fastSE = 2
            else:
                fastSE = 1

            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)

        self.wavePlot.setSampleRate(self.boardSampleRate)

        self.signalProcessor.setNotchFilter(
            self.notchFilterFrequency, self.notchFilterBandwidth, self.boardSampleRate)
        self.signalProcessor.setHighpassFilter(
            self.highpassFilterFrequency, self.boardSampleRate)

        if not self.synthMode:
            self.evalBoard.setDacHighpassFilter(self.highpassFilterFrequency)

        if self.spikeScopeDialog:
            self.spikeScopeDialog.setSampleRate(self.boardSampleRate)

        self.impedanceFreqValid = False
        self.updateImpedanceFrequency()

        self.wavePlot.setFocus()

    def openInterfaceBoard(self):
        self.evalBoard = Rhd2000EvalBoard()

        # Open Opal Kelly XEM6010 board.
        errorCode = self.evalBoard.open()

        # cerr << "In MainWindow.openInterfaceBoard.  errorCode = " << errorCode << "\n"

        if errorCode < 1:
            if errorCode == -1:
                r = QMessageBox.question(self, "Cannot load Opal Kelly FrontPanel DLL",
                                         "Opal Kelly USB drivers not installed.  "
                                         "Click OK to run application with synthesized biopotential data for "
                                         "demonstration purposes."
                                         "<p>To use the RHD2000 Interface, click Cancel, load the correct "
                                         "Opal Kelly drivers, then restart the application."
                                         "<p>Visit http:#www.intantech.com for more information.",
                                         QMessageBox.Ok | QMessageBox.Cancel)
            else:
                r = QMessageBox.question(self, "Intan RHD2000 USB Interface Board Not Found",
                                         "Intan Technologies RHD2000 Interface not found on any USB port.  "
                                         "Click OK to run application with synthesized biopotential data for "
                                         "demonstration purposes."
                                         "<p>To use the RHD2000 Interface, click Cancel, connect the device "
                                         "to a USB port, then restart the application."
                                         "<p>Visit http:#www.intantech.com for more information.",
                                         QMessageBox.Ok | QMessageBox.Cancel)

            if r == QMessageBox.Ok:
                QMessageBox.information(self, "Synthesized Data Mode",
                                        "The software will generate synthetic biopotentials for "
                                        "demonstration purposes."
                                        "<p>If the amplifier sampling rate is set to 5 kS/s or higher, neural "
                                        "spikes will be generated.  If the sampling rate is set lower than 5 kS/s, "
                                        "ECG signals will be generated."
                                        "<p>In demonstration mode, the audio output will not work since self "
                                        "requires the line out signal from the interface board.  Also, electrode "
                                        "impedance testing is disabled in self mode.",
                                        QMessageBox.Ok)
                self.synthMode = True
                self.evalBoard = 0
                return
            else:
                sys.exit(1)  # abort application

        # Load Rhythm FPGA configuration bitfile (provided by Intan Technologies).
        bitfilename = str(QCoreApplication.applicationDirPath() + "/main.bit")

        if not self.evalBoard.uploadFpgaBitfile(bitfilename):
            QMessageBox.critical(self, "FPGA Configuration File Upload Error",
                                 "Cannot upload configuration file to FPGA.  Make sure file main.bit "
                                 "is in the same directory as the executable file.")
            sys.exit(1)  # abort application

        # Initialize interface board.
        self.evalBoard.initialize()

        # Read 4-bit board mode.
        self.evalBoardMode = self.evalBoard.getBoardMode()

        # Set sample rate and upload all auxiliary SPI command sequences.
        self.changeSampleRate(self.sampleRateComboBox.currentIndex())

        # Select RAM Bank 0 for AuxCmd3 initially, so the ADC is calibrated.
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd3, 0)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd3, 0)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd3, 0)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd3, 0)

        # Since our longest command sequence is 60 commands, we run the SPI
        # interface for 60 samples.
        self.evalBoard.setMaxTimeStep(60)
        self.evalBoard.setContinuousRunMode(False)

        # Start SPI interface.
        self.evalBoard.run()

        # Wait for the 60-sample run to complete.
        while self.evalBoard.isRunning():
            qApp.processEvents()

        # Read the resulting single data block from the USB interface.
        dataBlock = Rhd2000DataBlock(self.evalBoard.getNumEnabledDataStreams())
        self.evalBoard.readDataBlock(dataBlock)

        # Now that ADC calibration has been performed, we switch to the command sequence
        # that does not execute ADC calibration.
        if self.fastSettleEnabled:
            fastSE = 2
        else:
            fastSE = 1
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)

        # Set default configuration for all eight DACs on interface board.
        self.evalBoard.enableDac(0, False)
        self.evalBoard.enableDac(1, False)
        self.evalBoard.enableDac(2, False)
        self.evalBoard.enableDac(3, False)
        self.evalBoard.enableDac(4, False)
        self.evalBoard.enableDac(5, False)
        self.evalBoard.enableDac(6, False)
        self.evalBoard.enableDac(7, False)
        # Initially point DACs to DacManual1 input
        self.evalBoard.selectDacDataStream(0, 8)
        self.evalBoard.selectDacDataStream(1, 8)
        self.evalBoard.selectDacDataStream(2, 8)
        self.evalBoard.selectDacDataStream(3, 8)
        self.evalBoard.selectDacDataStream(4, 8)
        self.evalBoard.selectDacDataStream(5, 8)
        self.evalBoard.selectDacDataStream(6, 8)
        self.evalBoard.selectDacDataStream(7, 8)
        self.evalBoard.selectDacDataChannel(0, 0)
        self.evalBoard.selectDacDataChannel(1, 1)
        self.evalBoard.selectDacDataChannel(2, 0)
        self.evalBoard.selectDacDataChannel(3, 0)
        self.evalBoard.selectDacDataChannel(4, 0)
        self.evalBoard.selectDacDataChannel(5, 0)
        self.evalBoard.selectDacDataChannel(6, 0)
        self.evalBoard.selectDacDataChannel(7, 0)
        self.evalBoard.setDacManual(32768)
        self.evalBoard.setDacGain(0)
        self.evalBoard.setAudioNoiseSuppress(0)

        self.evalBoard.setCableLengthMeters(Rhd2000EvalBoard.PortA, 0.0)
        self.evalBoard.setCableLengthMeters(Rhd2000EvalBoard.PortB, 0.0)
        self.evalBoard.setCableLengthMeters(Rhd2000EvalBoard.PortC, 0.0)
        self.evalBoard.setCableLengthMeters(Rhd2000EvalBoard.PortD, 0.0)

    def findConnectedAmplifiers(self):
        numChannelsOnPort = [0, 0, 0, 0]

        portIndex = [-1]*constants.MAX_NUM_DATA_STREAMS
        portIndexOld = [-1]*constants.MAX_NUM_DATA_STREAMS
        chipIdOld = [-1]*constants.MAX_NUM_DATA_STREAMS

        for i in range(len(self.chipId)):
            self.chipId[i] = -1

        initStreamPorts = [
            Rhd2000EvalBoard.PortA1,
            Rhd2000EvalBoard.PortA2,
            Rhd2000EvalBoard.PortB1,
            Rhd2000EvalBoard.PortB2,
            Rhd2000EvalBoard.PortC1,
            Rhd2000EvalBoard.PortC2,
            Rhd2000EvalBoard.PortD1,
            Rhd2000EvalBoard.PortD2]

        initStreamDdrPorts = [
            Rhd2000EvalBoard.PortA1Ddr,
            Rhd2000EvalBoard.PortA2Ddr,
            Rhd2000EvalBoard.PortB1Ddr,
            Rhd2000EvalBoard.PortB2Ddr,
            Rhd2000EvalBoard.PortC1Ddr,
            Rhd2000EvalBoard.PortC2Ddr,
            Rhd2000EvalBoard.PortD1Ddr,
            Rhd2000EvalBoard.PortD2Ddr]

        if not self.synthMode:
            # Set sampling rate to highest value for maximum temporal resolution.
            self.changeSampleRate(self.sampleRateComboBox.count() - 1)

            # Enable all data streams, and set sources to cover one or two chips
            # on Ports A-D.
            self.evalBoard.setDataSource(0, initStreamPorts[0])
            self.evalBoard.setDataSource(1, initStreamPorts[1])
            self.evalBoard.setDataSource(2, initStreamPorts[2])
            self.evalBoard.setDataSource(3, initStreamPorts[3])
            self.evalBoard.setDataSource(4, initStreamPorts[4])
            self.evalBoard.setDataSource(5, initStreamPorts[5])
            self.evalBoard.setDataSource(6, initStreamPorts[6])
            self.evalBoard.setDataSource(7, initStreamPorts[7])

            portIndexOld[0] = 0
            portIndexOld[1] = 0
            portIndexOld[2] = 1
            portIndexOld[3] = 1
            portIndexOld[4] = 2
            portIndexOld[5] = 2
            portIndexOld[6] = 3
            portIndexOld[7] = 3

            self.evalBoard.enableDataStream(0, True)
            self.evalBoard.enableDataStream(1, True)
            self.evalBoard.enableDataStream(2, True)
            self.evalBoard.enableDataStream(3, True)
            self.evalBoard.enableDataStream(4, True)
            self.evalBoard.enableDataStream(5, True)
            self.evalBoard.enableDataStream(6, True)
            self.evalBoard.enableDataStream(7, True)

            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortA,
                                                Rhd2000EvalBoard.AuxCmd3, 0)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortB,
                                                Rhd2000EvalBoard.AuxCmd3, 0)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortC,
                                                Rhd2000EvalBoard.AuxCmd3, 0)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortD,
                                                Rhd2000EvalBoard.AuxCmd3, 0)

            # Since our longest command sequence is 60 commands, we run the SPI
            # interface for 60 samples.
            self.evalBoard.setMaxTimeStep(60)
            self.evalBoard.setContinuousRunMode(False)

            dataBlock = Rhd2000DataBlock(
                self.evalBoard.getNumEnabledDataStreams())
            sumGoodDelays = [0]*constants.MAX_NUM_DATA_STREAMS
            indexFirstGoodDelay = [-1]*constants.MAX_NUM_DATA_STREAMS
            indexSecondGoodDelay = [-1]*constants.MAX_NUM_DATA_STREAMS

            # Run SPI command sequence at all 16 possible FPGA MISO delay settings
            # to find optimum delay for each SPI interface cable.
            for delay in range(16):
                self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortA, delay)
                self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortB, delay)
                self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortC, delay)
                self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortD, delay)

                # Start SPI interface.
                self.evalBoard.run()

                # Wait for the 60-sample run to complete.
                while self.evalBoard.isRunning():
                    qApp.processEvents()

                # Read the resulting single data block from the USB interface.
                self.evalBoard.readDataBlock(dataBlock)

                # Read the Intan chip ID number from each RHD2000 chip found.
                # Record delay settings that yield good communication with the chip.
                for stream in range(constants.MAX_NUM_DATA_STREAMS):
                    did, register59Value = self.deviceId(dataBlock, stream)

                    if (did == constants.CHIP_ID_RHD2132 or did == constants.CHIP_ID_RHD2216 or
                            (did == constants.CHIP_ID_RHD2164 and register59Value == constants.REGISTER_59_MISO_A)):
                        # cout << "Delay: " << delay << " on stream " << stream << " is good." << endl
                        sumGoodDelays[stream] = sumGoodDelays[stream] + 1
                        if indexFirstGoodDelay[stream] == -1:
                            indexFirstGoodDelay[stream] = delay
                            chipIdOld[stream] = did
                        elif indexSecondGoodDelay[stream] == -1:
                            indexSecondGoodDelay[stream] = delay
                            chipIdOld[stream] = did

            # Set cable delay settings that yield good communication with each
            # RHD2000 chip.
            optimumDelay = [0]*constants.MAX_NUM_DATA_STREAMS
            for stream in range(constants.MAX_NUM_DATA_STREAMS):
                if sumGoodDelays[stream] == 1 or sumGoodDelays[stream] == 2:
                    optimumDelay[stream] = indexFirstGoodDelay[stream]
                elif sumGoodDelays[stream] > 2:
                    optimumDelay[stream] = indexSecondGoodDelay[stream]

            self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortA,
                                         max(optimumDelay[0], optimumDelay[1]))
            self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortB,
                                         max(optimumDelay[2], optimumDelay[3]))
            self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortC,
                                         max(optimumDelay[4], optimumDelay[5]))
            self.evalBoard.setCableDelay(Rhd2000EvalBoard.PortD,
                                         max(optimumDelay[6], optimumDelay[7]))

    #        cout << "Port A cable delay: " << qMax(optimumDelay[0], optimumDelay[1]) << endl
    #        cout << "Port B cable delay: " << qMax(optimumDelay[2], optimumDelay[3]) << endl
    #        cout << "Port C cable delay: " << qMax(optimumDelay[4], optimumDelay[5]) << endl
    #        cout << "Port D cable delay: " << qMax(optimumDelay[6], optimumDelay[7]) << endl

            self.cableLengthPortA = self.evalBoard.estimateCableLengthMeters(
                max(optimumDelay[0], optimumDelay[1]))
            self.cableLengthPortB = self.evalBoard.estimateCableLengthMeters(
                max(optimumDelay[2], optimumDelay[3]))
            self.cableLengthPortC = self.evalBoard.estimateCableLengthMeters(
                max(optimumDelay[4], optimumDelay[5]))
            self.cableLengthPortD = self.evalBoard.estimateCableLengthMeters(
                max(optimumDelay[6], optimumDelay[7]))

        else:
            # If we are running with synthetic data (i.e., no interface board), just assume
            # that one RHD2132 is plugged into Port A.
            chipIdOld[0] = constants.CHIP_ID_RHD2132
            portIndexOld[0] = 0

        # Now that we know which RHD2000 amplifier chips are plugged into each SPI port,
        # add up the total number of amplifier channels on each port and calcualate the number
        # of data streams necessary to convey self data over the USB interface.
        numStreamsRequired = 0
        rhd2216ChipPresent = False
        for stream in range(constants.MAX_NUM_DATA_STREAMS):
            if chipIdOld[stream] == constants.CHIP_ID_RHD2216:
                numStreamsRequired += 1
                if numStreamsRequired <= constants.MAX_NUM_DATA_STREAMS:
                    numChannelsOnPort[portIndexOld[stream]] += 16
                rhd2216ChipPresent = True

            if chipIdOld[stream] == constants.CHIP_ID_RHD2132:
                numStreamsRequired += 1
                if numStreamsRequired <= constants.MAX_NUM_DATA_STREAMS:
                    numChannelsOnPort[portIndexOld[stream]] += 32
            if chipIdOld[stream] == constants.CHIP_ID_RHD2164:
                numStreamsRequired += 2
                if numStreamsRequired <= constants.MAX_NUM_DATA_STREAMS:
                    numChannelsOnPort[portIndexOld[stream]] += 64

        # If the user plugs in more chips than the USB interface can support, throw
        # up a warning that not all channels will be displayed.
        if numStreamsRequired > 8:
            if rhd2216ChipPresent:
                QMessageBox.warning(self, "Capacity of USB Interface Exceeded",
                                    "self RHD2000 USB interface board can support 256 only amplifier channels."
                                    "<p>More than 256 total amplifier channels are currently connected.  (Each RHD2216 "
                                    "chip counts as 32 channels for USB interface purposes.)"
                                    "<p>Amplifier chips exceeding self limit will not appear in the GUI.")
            else:
                QMessageBox.warning(self, "Capacity of USB Interface Exceeded",
                                    "self RHD2000 USB interface board can support 256 only amplifier channels."
                                    "<p>More than 256 total amplifier channels are currently connected."
                                    "<p>Amplifier chips exceeding self limit will not appear in the GUI.")

        # Reconfigure USB data streams in consecutive order to accommodate all connected chips.
        stream = 0
        for oldStream in range(constants.MAX_NUM_DATA_STREAMS):
            if (chipIdOld[oldStream] == constants.CHIP_ID_RHD2216) and (stream < constants.MAX_NUM_DATA_STREAMS):
                self.chipId[stream] = constants.CHIP_ID_RHD2216
                portIndex[stream] = portIndexOld[oldStream]
                if not self.synthMode:
                    self.evalBoard.enableDataStream(stream, True)
                    self.evalBoard.setDataSource(
                        stream, initStreamPorts[oldStream])

                stream += 1
            elif (chipIdOld[oldStream] == constants.CHIP_ID_RHD2132) and (stream < constants.MAX_NUM_DATA_STREAMS):
                self.chipId[stream] = constants.CHIP_ID_RHD2132
                portIndex[stream] = portIndexOld[oldStream]
                if not self.synthMode:
                    self.evalBoard.enableDataStream(stream, True)
                    self.evalBoard.setDataSource(
                        stream, initStreamPorts[oldStream])
                stream += 1
            elif (chipIdOld[oldStream] == constants.CHIP_ID_RHD2164) and (stream < constants.MAX_NUM_DATA_STREAMS - 1):
                self.chipId[stream] = constants.CHIP_ID_RHD2164
                self.chipId[stream + 1] = constants.CHIP_ID_RHD2164_B
                portIndex[stream] = portIndexOld[oldStream]
                portIndex[stream + 1] = portIndexOld[oldStream]
                if not self.synthMode:
                    self.evalBoard.enableDataStream(stream, True)
                    self.evalBoard.enableDataStream(stream + 1, True)
                    self.evalBoard.setDataSource(
                        stream, initStreamPorts[oldStream])
                    self.evalBoard.setDataSource(
                        stream + 1, initStreamDdrPorts[oldStream])

                stream += 2

        # Disable unused data streams.
        for stream in range(stream, constants.MAX_NUM_DATA_STREAMS):
            if not self.synthMode:
                self.evalBoard.enableDataStream(stream, False)

        # Add channel descriptions to the SignalSources object to create a list of all waveforms.
        for port in range(4):
            if numChannelsOnPort[port] == 0:
                self.signalSources.signalPort[port].channel.clear()
                self.signalSources.signalPort[port].enabled = False
            elif self.signalSources.signalPort[port].numAmplifierChannels() != numChannelsOnPort[port]:
                # if number of channels on port has changed...
                # ...clear existing channels...
                self.signalSources.signalPort[port].channel.clear()
                # ...and create new ones.
                channel = 0
                # Create amplifier channels for each chip.
                for stream in range(constants.MAX_NUM_DATA_STREAMS):
                    if portIndex[stream] == port:
                        if self.chipId[stream] == constants.CHIP_ID_RHD2216:
                            for i in range(16):
                                self.signalSources.signalPort[port].addAmplifierChannelSpecific(
                                    channel, i, stream)
                                channel += 1
                        elif self.chipId[stream] == constants.CHIP_ID_RHD2132:
                            for i in range(32):
                                self.signalSources.signalPort[port].addAmplifierChannelSpecific(
                                    channel, i, stream)
                                channel += 1
                        elif self.chipId[stream] == constants.CHIP_ID_RHD2164:
                            # 32 channels on MISO A another 32 on MISO B
                            for i in range(32):
                                self.signalSources.signalPort[port].addAmplifierChannelSpecific(
                                    channel, i, stream)
                                channel += 1
                        elif self.chipId[stream] == constants.CHIP_ID_RHD2164_B:
                            # 32 channels on MISO A another 32 on MISO B
                            for i in range(32):
                                self.signalSources.signalPort[port].addAmplifierChannelSpecific(
                                    channel, i, stream)
                                channel += 1

                # Now create auxiliary input channels and supply voltage channels for each chip.
                auxName = 1
                vddName = 1
                for stream in range(constants.MAX_NUM_DATA_STREAMS):
                    if portIndex[stream] == port:
                        if self.chipId[stream] == constants.CHIP_ID_RHD2216 or self.chipId[stream] == constants.CHIP_ID_RHD2132 or self.chipId[stream] == constants.CHIP_ID_RHD2164:
                            self.signalSources.signalPort[port].addAuxInputChannel(
                                channel, 0, auxName, stream)
                            channel += 1
                            auxName += 1
                            self.signalSources.signalPort[port].addAuxInputChannel(
                                channel, 1, auxName, stream)
                            channel += 1
                            auxName += 1
                            self.signalSources.signalPort[port].addAuxInputChannel(
                                channel, 2, auxName, stream)
                            channel += 1
                            auxName += 1
                            self.signalSources.signalPort[port].addSupplyVoltageChannel(
                                channel, 0, vddName, stream)
                            channel += 1
                            vddName += 1
                # If number of channels on port has not changed, don't create new channels (since self
            else:
                # would clear all user-defined channel names.  But we must update the data stream indices
                # on the port.
                channel = 0
                # Update stream indices for amplifier channels.
                for stream in range(constants.MAX_NUM_DATA_STREAMS):
                    if portIndex[stream] == port:
                        if self.chipId[stream] == constants.CHIP_ID_RHD2216:
                            for i in range(channel, channel + 16):
                                self.signalSources.signalPort[port].channel[i].boardStream = stream
                            channel += 16
                        elif self.chipId[stream] == constants.CHIP_ID_RHD2132:
                            for i in range(channel, channel + 32):
                                self.signalSources.signalPort[port].channel[i].boardStream = stream
                            channel += 32
                        elif self.chipId[stream] == constants.CHIP_ID_RHD2164:
                            # 32 channels on MISO A another 32 on MISO B
                            for i in range(channel, channel + 32):
                                self.signalSources.signalPort[port].channel[i].boardStream = stream
                            channel += 32
                        elif self.chipId[stream] == constants.CHIP_ID_RHD2164_B:
                            # 32 channels on MISO A another 32 on MISO B
                            for i in range(channel, channel + 32):
                                self.signalSources.signalPort[port].channel[i].boardStream = stream
                            channel += 32
                # Update stream indices for auxiliary channels and supply voltage channels.
                for stream in range(constants.MAX_NUM_DATA_STREAMS):
                    if portIndex[stream] == port:
                        if self.chipId[stream] == constants.CHIP_ID_RHD2216 or self.chipId[stream] == constants.CHIP_ID_RHD2132 or self.chipId[stream] == constants.CHIP_ID_RHD2164:
                            self.signalSources.signalPort[port].channel[channel].boardStream = stream
                            channel += 1
                            self.signalSources.signalPort[port].channel[channel].boardStream = stream
                            channel += 1
                            self.signalSources.signalPort[port].channel[channel].boardStream = stream
                            channel += 1
                            self.signalSources.signalPort[port].channel[channel].boardStream = stream
                            channel += 1

        # Update Port A-D radio buttons in GUI
        if self.signalSources.signalPort[0].numAmplifierChannels() == 0:
            self.signalSources.signalPort[0].enabled = False
            self.displayPortAButton.setEnabled(False)
            self.displayPortAButton.setText(
                self.signalSources.signalPort[0].name)
        else:
            self.signalSources.signalPort[0].enabled = True
            self.displayPortAButton.setEnabled(True)
            self.displayPortAButton.setText(self.signalSources.signalPort[0].name +
                                            " (" + str(self.signalSources.signalPort[0].numAmplifierChannels()) +
                                            " channels)")

        if self.signalSources.signalPort[1].numAmplifierChannels() == 0:
            self.signalSources.signalPort[1].enabled = False
            self.displayPortBButton.setEnabled(False)
            self.displayPortBButton.setText(
                self.signalSources.signalPort[1].name)
        else:
            self.signalSources.signalPort[1].enabled = True
            self.displayPortBButton.setEnabled(True)
            self.displayPortBButton.setText(self.signalSources.signalPort[1].name +
                                            " (" + str(self.signalSources.signalPort[1].numAmplifierChannels()) +
                                            " channels)")

        if self.signalSources.signalPort[2].numAmplifierChannels() == 0:
            self.signalSources.signalPort[2].enabled = False
            self.displayPortCButton.setEnabled(False)
            self.displayPortCButton.setText(
                self.signalSources.signalPort[2].name)
        else:
            self.signalSources.signalPort[2].enabled = True
            self.displayPortCButton.setEnabled(True)
            self.displayPortCButton.setText(self.signalSources.signalPort[2].name +
                                            " (" + str(self.signalSources.signalPort[2].numAmplifierChannels()) +
                                            " channels)")

        if self.signalSources.signalPort[3].numAmplifierChannels() == 0:
            self.signalSources.signalPort[3].enabled = False
            self.displayPortDButton.setEnabled(False)
            self.displayPortDButton.setText(
                self.signalSources.signalPort[3].name)
        else:
            self.signalSources.signalPort[3].enabled = True
            self.displayPortDButton.setEnabled(True)
            self.displayPortDButton.setText(self.signalSources.signalPort[3].name +
                                            " (" + str(self.signalSources.signalPort[3].numAmplifierChannels()) +
                                            " channels)")

        if self.signalSources.signalPort[0].numAmplifierChannels() > 0:
            self.displayPortAButton.setChecked(True)
        elif self.signalSources.signalPort[1].numAmplifierChannels() > 0:
            self.displayPortBButton.setChecked(True)
        elif self.signalSources.signalPort[2].numAmplifierChannels() > 0:
            self.displayPortCButton.setChecked(True)
        elif self.signalSources.signalPort[3].numAmplifierChannels() > 0:
            self.displayPortDButton.setChecked(True)
        else:
            self.displayAdcButton.setChecked(True)

        # Return sample rate to original user-selected value.
        self.changeSampleRate(self.sampleRateComboBox.currentIndex())

        # signalSources.signalPort[0].print()
        # signalSources.signalPort[1].print()
        # signalSources.signalPort[2].print()
        # signalSources.signalPort[3].print()

    # Return the Intan chip ID stored in ROM register 63.  If the data is invalid
    # (due to a SPI communication channel with the wrong delay or a chip not present)
    # then return -1.  The value of ROM register 59 is also returned.  self register
    # has a value of 0 on RHD2132 and RHD2216 chips, but in RHD2164 chips it is used
    # to align the DDR MISO A/B data from the SPI bus.  (Register 59 has a value of 53
    # on MISO A and a value of 58 on MISO B.)
    def deviceId(self, dataBlock, stream):
        # First, check ROM registers 32-36 to verify that they hold 'INTAN', and
        # the initial chip name ROM registers 24-26 that hold 'RHD'.
        # self is just used to verify that we are getting good data over the SPI
        # communication channel.
        intanChipPresent = (chr(dataBlock.auxiliaryData[stream][2][32]) == 'I' and
                            chr(dataBlock.auxiliaryData[stream][2][33]) == 'N' and
                            chr(dataBlock.auxiliaryData[stream][2][34]) == 'T' and
                            chr(dataBlock.auxiliaryData[stream][2][35]) == 'A' and
                            chr(dataBlock.auxiliaryData[stream][2][36]) == 'N' and
                            chr(dataBlock.auxiliaryData[stream][2][24]) == 'R' and
                            chr(dataBlock.auxiliaryData[stream][2][25]) == 'H' and
                            chr(dataBlock.auxiliaryData[stream][2][26]) == 'D')

        # If the SPI communication is bad, return -1.  Otherwise, return the Intan
        # chip ID number stored in ROM regstier 63.
        if not intanChipPresent:
            register59Value = -1
            return -1, register59Value
        else:
            # Register 59
            register59Value = dataBlock.auxiliaryData[stream][2][23]
            # chip ID (Register 63)
            return dataBlock.auxiliaryData[stream][2][19], register59Value

    # Start recording data from USB interface board to disk.
    def recordInterfaceBoard(self):
        # Create list of enabled channels that will be saved to disk.
        self.signalProcessor.createSaveList(self.signalSources, False, 0)

        self.startNewSaveFile(self.saveFormat)

        # Write save file header information.
        self.writeSaveFileHeader(self.saveStream, self.infoStream,
                                 self.saveFormat, self.signalProcessor.getNumTempSensors())

        # Disable some GUI buttons while recording is in progress.
        self.enableChannelButton.setEnabled(False)
        self.enableAllButton.setEnabled(False)
        self.disableAllButton.setEnabled(False)
        self.sampleRateComboBox.setEnabled(False)
        # recordFileSpinBox.setEnabled(False)
        self.setSaveFormatButton.setEnabled(False)

        self.recording = True
        self.triggerSet = False
        self.triggered = False
        self.runInterfaceBoard()

    # Wait for user-defined trigger to start recording data from USB interface board to disk.
    def triggerRecordInterfaceBoard(self):
        self.triggerRecordDialog = TriggerRecordDialog(
            self.recordTriggerChannel, self.recordTriggerPolarity, self.recordTriggerBuffer, self.postTriggerTime, self.saveTriggerChannel, self)
        if self.triggerRecordDialog.exec():
            self.recordTriggerChannel = self.triggerRecordDialog.digitalInput
            self.recordTriggerPolarity = self.triggerRecordDialog.triggerPolarity
            self.recordTriggerBuffer = self.triggerRecordDialog.recordBuffer
            self.postTriggerTime = self.triggerRecordDialog.postTriggerTime
            self.saveTriggerChannel = (
                self.triggerRecordDialog.saveTriggerChannelCheckBox.checkState() == Qt.Checked)

            # Create list of enabled channels that will be saved to disk.
            self.signalProcessor.createSaveList(
                self.signalSources, self.saveTriggerChannel, self.recordTriggerChannel)

            # Disable some GUI buttons while recording is in progress.
            self.enableChannelButton.setEnabled(False)
            self.enableAllButton.setEnabled(False)
            self.disableAllButton.setEnabled(False)
            self.sampleRateComboBox.setEnabled(False)
            # recordFileSpinBox.setEnabled(False)
            self.setSaveFormatButton.setEnabled(False)

            self.recording = False
            self.triggerSet = True
            self.triggered = False
            self.runInterfaceBoard()

        self.wavePlot.setFocus()

    def writeSaveFileHeader(self, outStream, infoStream, saveFormat, numTempSensors):
        for i in range(16):
            self.signalSources.signalPort[6].channel[i].enabled = self.saveTtlOut

        if saveFormat == constants.SaveFormatIntan:
            outStream.writeUInt32(constants.DATA_FILE_MAGIC_NUMBER)
            outStream.writeInt16(constants.DATA_FILE_MAIN_VERSION_NUMBER)
            outStream.writeInt16(constants.DATA_FILE_SECONDARY_VERSION_NUMBER)

            outStream.writeDouble(self.boardSampleRate)

            outStream.writeInt16(self.dspEnabled)
            outStream.writeDouble(self.actualDspCutoffFreq)
            outStream.writeDouble(self.actualLowerBandwidth)
            outStream.writeDouble(self.actualUpperBandwidth)

            outStream.writeDouble(self.desiredDspCutoffFreq)
            outStream.writeDouble(self.desiredLowerBandwidth)
            outStream.writeDouble(self.desiredUpperBandwidth)

            outStream.writeInt16(self.notchFilterComboBox.currentIndex())

            outStream.writeDouble(self.desiredImpedanceFreq)
            outStream.writeDouble(self.actualImpedanceFreq)

            outStream.writeQString(self.note1LineEdit.text())
            outStream.writeQString(self.note2LineEdit.text())
            outStream.writeQString(self.note3LineEdit.text())

            if self.saveTemp:
                # version 1.1 addition
                outStream.writeInt16(numTempSensors)
            else:
                outStream.writeInt16(0)

            outStream.writeInt16(self.evalBoardMode)  # version 1.3 addition
            self.signalSources.writeToStream(outStream)

        elif saveFormat == constants.SaveFormatFilePerSignalType or saveFormat == constants.SaveFormatFilePerChannel:
            infoStream.writeUInt32(constants.DATA_FILE_MAGIC_NUMBER)
            infoStream.writeInt16(constants.DATA_FILE_MAIN_VERSION_NUMBER)
            infoStream.writeInt16(constants.DATA_FILE_SECONDARY_VERSION_NUMBER)

            infoStream.writeDouble(self.boardSampleRate)

            infoStream.writeInt16(self.dspEnabled)
            infoStream.writeDouble(self.actualDspCutoffFreq)
            infoStream.writeDouble(self.actualLowerBandwidth)
            infoStream.writeDouble(self.actualUpperBandwidth)

            infoStream.writeDouble(self.desiredDspCutoffFreq)
            infoStream.writeDouble(self.desiredLowerBandwidth)
            infoStream.writeDouble(self.desiredUpperBandwidth)

            infoStream.writeInt16(self.notchFilterComboBox.currentIndex())

            infoStream.writeDouble(self.desiredImpedanceFreq)
            infoStream.writeDouble(self.actualImpedanceFreq)

            infoStream.writeQString(self.note1LineEdit.text())
            infoStream.writeQString(self.note2LineEdit.text())
            infoStream.writeQString(self.note3LineEdit.text())

            infoStream.writeInt16(0)

            # version 1.3 addition(bug fix: added here in version 1.41)
            infoStream.writeInt16(self.evalBoardMode)

            self.signalSources.writeToStream(infoStream)

    # Start SPI communication to all connected RHD2000 amplifiers and stream
    # waveform data over USB port.
    def runInterfaceBoard(self):
        timer = QTime()
        bufferQueue = DataQueue()

        extraCycles = 0
        timestampOffset = 0
        preTriggerBufferQueueLength = 0
        fifoNearlyFull = 0
        triggerEndCounter = 0

        triggerEndThreshold = math.ceil(self.postTriggerTime * self.boardSampleRate / (
            self.numUsbBlocksToRead * constants.SAMPLES_PER_DATA_BLOCK)) - 1

        if self.triggerSet:
            preTriggerBufferQueueLength = self.numUsbBlocksToRead * math.ceil(self.recordTriggerBuffer / (
                self.numUsbBlocksToRead * Rhd2000DataBlock.getSamplesPerDataBlock() / self.boardSampleRate)) + 1

        # QSound triggerBeep(QDir.tempPath() + "/triggerbeep.wav")
        # QSound triggerEndBeep(QDir.tempPath() + "/triggerendbeep.wav")

        # Average temperature sensor readings over a ~0.1 second interval.
        self.signalProcessor.tempHistoryReset(self.numUsbBlocksToRead * 3)

        self.running = True
        self.wavePlot.setFocus()

        # Enable stop button on GUI while running
        self.stopButton.setEnabled(True)

        # Disable various buttons on GUI while running
        self.runButton.setEnabled(False)
        self.recordButton.setEnabled(False)
        self.triggerButton.setEnabled(False)

        self.baseFilenameButton.setEnabled(False)
        self.renameChannelButton.setEnabled(False)
        self.changeBandwidthButton.setEnabled(False)
        self.impedanceFreqSelectButton.setEnabled(False)
        self.runImpedanceTestButton.setEnabled(False)
        self.scanButton.setEnabled(False)
        self.setCableDelayButton.setEnabled(False)
        self.digOutButton.setEnabled(False)
        self.setSaveFormatButton.setEnabled(False)

        # Turn LEDs on to indicate that data acquisition is running.
        self.ttlOut[15] = 1
        ledArray = [1, 0, 0, 0, 0, 0, 0, 0]
        ledIndex = 0
        if not self.synthMode:
            self.evalBoard.setLedDisplay(ledArray)
            self.evalBoard.setTtlOut(self.ttlOut)

        if self.synthMode:
            dataBlockSize = Rhd2000DataBlock.calculateDataBlockSizeInWords(1)
        else:
            dataBlockSize = Rhd2000DataBlock.calculateDataBlockSizeInWords(
                self.evalBoard.getNumEnabledDataStreams())

        totalBytesWritten = 0
        totalRecordTimeSeconds = 0.0
        recordTimeIncrementSeconds = self.numUsbBlocksToRead * \
            Rhd2000DataBlock.getSamplesPerDataBlock() / self.boardSampleRate

        # Calculate the number of bytes per minute that we will be saving to disk
        # if recording data (excluding headers).
        bytesPerMinute = Rhd2000DataBlock.getSamplesPerDataBlock() * (self.signalProcessor.bytesPerBlock(self.saveFormat,
                                                                                                         self.saveTemp, self.saveTtlOut) / Rhd2000DataBlock.getSamplesPerDataBlock()) * self.boardSampleRate

        samplePeriod = 1.0 / self.boardSampleRate
        fifoCapacity = Rhd2000EvalBoard.fifoCapacityInWords()

        if self.recording:
            self.setStatusBarRecording(bytesPerMinute)
        elif self.triggerSet:
            self.setStatusBarWaitForTrigger()
        else:
            self.setStatusBarRunning()

        if not self.synthMode:
            self.evalBoard.setContinuousRunMode(True)
            self.evalBoard.run()
        else:
            timer.start()

        while self.running:
            # If we are running in demo mode, use a timer to periodically generate more synthetic
            # data.  If not, wait for a certain amount of data to be ready from the USB interface board.
            if self.synthMode:
                newDataReady = (timer.elapsed() >= (
                    (1000.0 * 60.0 * self.numUsbBlocksToRead / self.boardSampleRate)))
            else:
                # takes about 17 ms at 30 kS/s with 256 amplifiers
                newDataReady = self.evalBoard.readDataBlocks(
                    self.numUsbBlocksToRead, self.dataQueue)

            # If new data is ready, then read it.
            if newDataReady:
                # statusBarLabel.setText("Running.  Extra CPU cycles: " + QString.number(extraCycles))

                if self.synthMode:
                    timer.start()  # restart timer
                    fifoPercentageFull = 0.0

                    # Generate synthetic data
                    totalBytesWritten += self.signalProcessor.loadSyntheticData(
                        self.numUsbBlocksToRead, self.boardSampleRate, self.recording, self.saveStream, self.saveFormat, self.saveTemp, self.saveTtlOut)
                else:
                    # Check the number of words stored in the Opal Kelly USB interface FIFO.
                    wordsInFifo = self.evalBoard.numWordsInFifo()
                    latency = 1000.0 * Rhd2000DataBlock.getSamplesPerDataBlock() * (wordsInFifo /
                                                                                    dataBlockSize) * samplePeriod

                    fifoPercentageFull = 100.0 * wordsInFifo / fifoCapacity

                    # Alert the user if the number of words in the FIFO is getting to be significant
                    # or nearing FIFO capacity.

                    self.fifoLagLabel.setText(("%.0f" % latency) + " ms")
                    if latency > 50.0:
                        self.fifoLagLabel.setStyleSheet("color: red")
                    else:
                        self.fifoLagLabel.setStyleSheet("color: green")

                    self.fifoFullLabel.setText(
                        "(" + ("%.0f" % fifoPercentageFull) + "% full)")
                    if fifoPercentageFull > 75.0:
                        self.fifoFullLabel.setStyleSheet("color: red")
                    else:
                        self.fifoFullLabel.setStyleSheet("color: black")

                    # Read waveform data from USB interface board.
                    if self.triggered:
                        triggerPolarity = (1 - self.recordTriggerPolarity)
                    else:
                        triggerPolarity = self.recordTriggerPolarity
                    totalBytesWrittenTmp, triggerIndex = self.signalProcessor.loadAmplifierData(self.dataQueue, self.numUsbBlocksToRead,
                                                                                                (self.triggerSet |
                                                                                                 self.triggered), self.recordTriggerChannel,
                                                                                                triggerPolarity,
                                                                                                self.triggerSet, bufferQueue,
                                                                                                self.recording, self.saveStream, self.saveFormat, self.saveTemp,
                                                                                                self.saveTtlOut, timestampOffset)

                    totalBytesWritten += totalBytesWrittenTmp

                    while len(bufferQueue) > preTriggerBufferQueueLength:
                        bufferQueue.pop()

                    if self.triggerSet and (triggerIndex != -1):
                        self.triggerSet = False
                        self.triggered = True
                        self.recording = True
                        timestampOffset = triggerIndex

                        # Play trigger sound
                        # triggerBeep.play()

                        self.startNewSaveFile(self.saveFormat)

                        # Write save file header information.
                        self.writeSaveFileHeader(
                            self.saveStream, self.infoStream, self.saveFormat, self.signalProcessor.getNumTempSensors())

                        self.setStatusBarRecording(bytesPerMinute)

                        totalRecordTimeSeconds = len(
                            bufferQueue) * Rhd2000DataBlock.getSamplesPerDataBlock() / self.boardSampleRate

                        # Write contents of pre-trigger buffer to file.
                        totalBytesWritten += self.signalProcessor.saveBufferedData(bufferQueue, self.saveStream, self.saveFormat,
                                                                                   self.saveTemp, self.saveTtlOut, timestampOffset)
                    # New in version 1.5: episodic triggered recording
                    elif self.triggered and (triggerIndex != -1):
                        triggerEndCounter += 1
                        if triggerEndCounter > triggerEndThreshold:
                                                        # Keep recording for the specified number of seconds after the trigger has
                                                        # been de-asserted.
                            triggerEndCounter = 0
                            # Enable trigger again for True episodic recording.
                            self.triggerSet = True
                            self.triggered = False
                            self.recording = False
                            self.closeSaveFile(self.saveFormat)
                            totalRecordTimeSeconds = 0.0

                            self.setStatusBarWaitForTrigger()

                            # Play trigger end sound
                            # triggerEndBeep.play()

                    elif self.triggered:
                        # Ignore brief (< 1 second) trigger-off events.
                        triggerEndCounter = 0

                # Apply notch filter to amplifier data.
                self.signalProcessor.filterData(
                    self.numUsbBlocksToRead, self.channelVisible)

                # Trigger WavePlot widget to display new waveform data.
                self.wavePlot.passFilteredData()

                # Trigger Spike Scope to update with new waveform data.
                if self.spikeScopeDialog:
                    self.spikeScopeDialog.updateWaveform(
                        self.numUsbBlocksToRead)

                # If we are recording in Intan format and our data file has reached its specified
                # maximum length (e.g., 1 minute), close the current data file and open a new one.

                if self.recording:
                    totalRecordTimeSeconds += recordTimeIncrementSeconds

                    if self.saveFormat == constants.SaveFormatIntan:
                        if totalRecordTimeSeconds >= (60 * self.newSaveFilePeriodMinutes):
                            self.closeSaveFile(self.saveFormat)
                            self.startNewSaveFile(self.saveFormat)

                            # Write save file header information.
                            self.writeSaveFileHeader(
                                self.saveStream, self.infoStream, self.saveFormat, self.signalProcessor.getNumTempSensors())

                            self.setStatusBarRecording(bytesPerMinute)

                            totalRecordTimeSeconds = 0.0

                # If the USB interface FIFO (on the FPGA board) exceeds 98% full, halt
                # data acquisition and display a warning message.
                if fifoPercentageFull > 98.0:
                    # We must see the FIFO >98% full three times in a row to eliminate the possiblity
                    fifoNearlyFull += 1
                    # of a USB glitch causing recording to stop.  (Added for version 1.5.)
                    if fifoNearlyFull > 2:
                        self.running = False

                        # Stop data acquisition
                        if not self.synthMode:
                            self.evalBoard.setContinuousRunMode(False)
                            self.evalBoard.setMaxTimeStep(0)

                        if self.recording:
                            self.closeSaveFile(self.saveFormat)
                            self.recording = False
                            self.triggerSet = False
                            self.triggered = False

                        # Turn off LED.
                        for i in range(8):
                            ledArray[i] = 0
                        self.ttlOut[15] = 0
                        if not self.synthMode:
                            self.evalBoard.setLedDisplay(ledArray)
                            self.evalBoard.setTtlOut(self.ttlOut)

                        QMessageBox.critical(self, "USB Buffer Overrun Error",
                                             "Recording was stopped because the USB FIFO buffer on the interface "
                                             "board reached maximum capacity.  This happens when the host computer "
                                             "cannot keep up with the data streaming from the interface board."
                                             "<p>Try lowering the sample rate, disabling the notch filter, or reducing "
                                             "the number of waveforms on the screen to reduce CPU load.")

                else:
                    fifoNearlyFull = 0

                # Advance LED display
                ledArray[ledIndex] = 0
                ledIndex += 1
                if ledIndex == 8:
                    ledIndex = 0
                ledArray[ledIndex] = 1
                if not self.synthMode:
                    self.evalBoard.setLedDisplay(ledArray)

            qApp.processEvents()  # Stay responsive to GUI events during this loop
            extraCycles += 1

        # Stop data acquisition (when running == False)
        if not self.synthMode:
            self.evalBoard.setContinuousRunMode(False)
            self.evalBoard.setMaxTimeStep(0)

            # Flush USB FIFO on XEM6010
            self.evalBoard.flush()

        # If external control of chip auxiliary output pins was enabled, make sure
        # all auxout pins are turned off when acquisition stops.
        if not self.synthMode:
            if self.auxDigOutEnabled[0] or self.auxDigOutEnabled[1] or self.auxDigOutEnabled[2] or self.auxDigOutEnabled[3]:
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortA, False)
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortB, False)
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortC, False)
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortD, False)
                self.evalBoard.setMaxTimeStep(60)
                self.evalBoard.run()
                # Wait for the 60-sample run to complete.
                while self.evalBoard.isRunning():
                    qApp.processEvents()

                self.evalBoard.flush()
                self.evalBoard.setMaxTimeStep(0)
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortA, self.auxDigOutEnabled[0])
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortB, self.auxDigOutEnabled[1])
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortC, self.auxDigOutEnabled[2])
                self.evalBoard.enableExternalDigOut(
                    Rhd2000EvalBoard.PortD, self.auxDigOutEnabled[3])

        # Close save file, if recording.
        if self.recording:
            self.closeSaveFile(self.saveFormat)
            self.recording = False

        # Reset trigger
        self.triggerSet = False
        self.triggered = False

        totalRecordTimeSeconds = 0.0

        # Turn off LED.
        for i in range(8):
            ledArray[i] = 0
        self.ttlOut[15] = 0
        if not self.synthMode:
            self.evalBoard.setLedDisplay(ledArray)
            self.evalBoard.setTtlOut(self.ttlOut)

        self.setStatusBarReady()

        # Enable/disable various GUI buttons.

        self.runButton.setEnabled(True)
        self.recordButton.setEnabled(self.validFilename)
        self.triggerButton.setEnabled(self.validFilename)
        self.stopButton.setEnabled(False)

        self.baseFilenameButton.setEnabled(True)
        self.renameChannelButton.setEnabled(True)
        self.changeBandwidthButton.setEnabled(True)
        self.impedanceFreqSelectButton.setEnabled(True)
        self.runImpedanceTestButton.setEnabled(self.impedanceFreqValid)
        self.scanButton.setEnabled(True)
        self.setCableDelayButton.setEnabled(True)
        self.digOutButton.setEnabled(True)

        self.enableChannelButton.setEnabled(True)
        self.enableAllButton.setEnabled(True)
        self.disableAllButton.setEnabled(True)
        self.sampleRateComboBox.setEnabled(True)
        self.setSaveFormatButton.setEnabled(True)

    # Stop SPI data acquisition.
    def stopInterfaceBoard(self):
        self.running = False
        self.wavePlot.setFocus()

    def selectBaseFilenameSlot(self):
        self.selectBaseFilename(self.saveFormat)

    def selectBaseFilename(self, saveFormat):
        if saveFormat == constants.SaveFormatIntan:
            newFileName, _ = QFileDialog.getSaveFileName(self,
                                                         "Select Base Filename", ".",
                                                         "Intan Data Files (*.rhd)")
        elif saveFormat == constants.SaveFormatFilePerSignalType:
            newFileName, _ = QFileDialog.getSaveFileName(self,
                                                         "Select Base Filename", ".",
                                                         "Intan Data Files (*.rhd)")
        elif saveFormat == constants.SaveFormatFilePerChannel:
            newFileName, _ = QFileDialog.getSaveFileName(self,
                                                         "Select Base Filename", ".",
                                                         "Intan Data Files (*.rhd)")

        if newFileName != "":
            self.saveBaseFileName = newFileName
            newFileInfo = QFileInfo(newFileName)
            self.saveFilenameLineEdit.setText(newFileInfo.baseName())

        validFilename = self.saveBaseFileName != ""
        self.recordButton.setEnabled(validFilename)
        self.triggerButton.setEnabled(validFilename)
        self.wavePlot.setFocus()

    def openIntanWebsite(self):
        QDesktopServices.openUrl(
            QUrl("http://www.intantech.com", QUrl.TolerantMode))

    def setNumWaveformsComboBox(self, index):
        self.numFramesComboBox.setCurrentIndex(index)

    # Open Spike Scope dialog and initialize it.
    def spikeScope(self):
        if not self.spikeScopeDialog:
            self.spikeScopeDialog = SpikeScopeDialog(self.signalProcessor, self.signalSources,
                                                     self.wavePlot.selectedChannel(), self)
            # add any 'connect' statements here

        self.spikeScopeDialog.show()
        self.spikeScopeDialog.raise_()
        self.spikeScopeDialog.activateWindow()
        self.spikeScopeDialog.setYScale(self.yScaleComboBox.currentIndex())
        self.spikeScopeDialog.setSampleRate(self.boardSampleRate)
        self.wavePlot.setFocus()

    # Change selected channel on Spike Scope when user selects a new channel.
    def newSelectedChannel(self, newChannel):
        if self.spikeScopeDialog is not None:
            self.spikeScopeDialog.setNewChannel(newChannel)

        if self.dacLockToSelectedBox.isChecked():
            if newChannel.signalType == constants.AmplifierSignal:
                # Set DAC 1 to selected channel and label it accordingly.
                self.dacSelectedChannel[0] = newChannel
                if not self.synthMode:
                    self.evalBoard.selectDacDataStream(
                        0, newChannel.boardStream)
                    self.evalBoard.selectDacDataChannel(
                        0, newChannel.chipChannel)

                self.setDacChannelLabel(0, newChannel.customChannelName,
                                        newChannel.nativeChannelName)

    # Enable or disable RHD2000 amplifier fast settle function.
    def enableFastSettle(self, enabled):
        self.fastSettleEnabled = not enabled == Qt.Unchecked
        if self.fastSettleEnabled:
            fastSE = 2
        else:
            fastSE = 1

        if not self.synthMode:
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)
            self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd3,
                                                fastSE)

        self.wavePlot.setFocus()

    # Enable or disable external fast settling function.
    def enableExternalFastSettle(self, enabled):
        if not self.synthMode:
            self.evalBoard.enableExternalFastSettle(enabled)

        self.fastSettleCheckBox.setEnabled(not enabled)
        self.wavePlot.setFocus()

    # Select TTL input channel for external fast settle control.
    def setExternalFastSettleChannel(self, channel):
        if not self.synthMode:
            self.evalBoard.setExternalFastSettleChannel(channel)
        self.wavePlot.setFocus()

    # Load application settings from *.isf (Intan Settings File) file.
    def loadSettings(self):
        loadSettingsFileName, _ = QFileDialog.getOpenFileName(self,
                                                              "Select Settings Filename", ".",
                                                              "Intan Settings Files (*.isf)")
        if loadSettingsFileName == "":
            self.wavePlot.setFocus()
            return

        settingsFile = QFile(loadSettingsFileName)
        if not settingsFile.open(QIODevice.ReadOnly):
            print("Can't open settings file " +
                  str(loadSettingsFileName) + "\n")
            self.wavePlot.setFocus()
            return

        # Load settings
        inStream = QDataStream(settingsFile)
        inStream.setVersion(QDataStream.Qt_4_8)
        inStream.setByteOrder(QDataStream.LittleEndian)
        inStream.setFloatingPointPrecision(QDataStream.SinglePrecision)

        tempQuint32 = inStream.readUInt32()
        if tempQuint32 != constants.SETTINGS_FILE_MAGIC_NUMBER:
            QMessageBox.critical(self, "Cannot Parse Settings File",
                                 "Selected file is not a valid settings file.")
            self.wavePlot.setFocus()
            return

        self.statusBar().showMessage("Restoring settings from file...")

        tempQint16 = inStream.readInt16()
        versionMain = tempQint16
        tempQint16 = inStream.readInt16()
        versionSecondary = tempQint16

        # Eventually check version number here for compatibility issues.

        SignalSources.readFromStream(inStream, self.signalSources)

        tempQint16 = inStream.readInt16()
        self.sampleRateComboBox.setCurrentIndex(tempQint16)
        tempQint16 = inStream.readInt16()
        self.yScaleComboBox.setCurrentIndex(tempQint16)
        tempQint16 = inStream.readInt16()
        self.tScaleComboBox.setCurrentIndex(tempQint16)

        self.scanPorts()

        tempQint16 = inStream.readInt16()
        self.notchFilterComboBox.setCurrentIndex(tempQint16)
        self.changeNotchFilter(self.notchFilterComboBox.currentIndex())

        self.saveBaseFileName = inStream.readQString()
        fileInfo = QFileInfo(self.saveBaseFileName)
        validFilename = self.saveBaseFileName != ""
        if validFilename:
            self.saveFilenameLineEdit.setText(fileInfo.baseName())
        self.recordButton.setEnabled(validFilename)
        self.triggerButton.setEnabled(validFilename)

        tempQint16 = inStream.readInt16()
        # recordFileSpinBox.setValue(tempQint16)
        self.newSaveFilePeriodMinutes = tempQint16

        tempQint16 = inStream.readInt16()
        self.dspEnabled = bool(tempQint16)
        self.desiredDspCutoffFreq = inStream.readDouble()
        self.desiredLowerBandwidth = inStream.readDouble()
        self.desiredUpperBandwidth = inStream.readDouble()

        self.desiredImpedanceFreq = inStream.readDouble()
        self.actualImpedanceFreq = inStream.readDouble()
        tempQint16 = inStream.readInt16()
        self.impedanceFreqValid = bool(tempQint16)

        # This will update bandwidth settings on RHD2000 chips and
        # the GUI bandwidth display:
        self.changeSampleRate(self.sampleRateComboBox.currentIndex())

        tempQint16 = inStream.readInt16()
        self.dacGainSlider.setValue(tempQint16)
        self.changeDacGain(tempQint16)

        tempQint16 = inStream.readInt16()
        self.dacNoiseSuppressSlider.setValue(tempQint16)
        self.changeDacNoiseSuppress(tempQint16)

        dacNamesTemp = [""]*8

        for i in range(8):
            tempQint16 = inStream.readInt16()
            self.dacEnabled[i] = bool(tempQint16)
            dacNamesTemp[i] = inStream.readQString()

            self.dacSelectedChannel[i] = self.signalSources.findChannelFromName(
                dacNamesTemp[i])
            if self.dacSelectedChannel[i] == 0:
                self.dacEnabled[i] = False
            if self.dacEnabled[i]:
                self.setDacChannelLabel(i, self.dacSelectedChannel[i].customChannelName,
                                        self.dacSelectedChannel[i].nativeChannelName)
            else:
                self.setDacChannelLabel(i, "n/a", "n/a")

            if not self.synthMode:
                self.evalBoard.enableDac(i, self.dacEnabled[i])
                if self.dacEnabled[i]:
                    self.evalBoard.selectDacDataStream(
                        i, self.dacSelectedChannel[i].boardStream)
                    self.evalBoard.selectDacDataChannel(
                        i, self.dacSelectedChannel[i].chipChannel)
                else:
                    self.evalBoard.selectDacDataStream(i, 0)
                    self.evalBoard.selectDacDataChannel(i, 0)

        self.dacButton1.setChecked(True)
        self.dacEnableCheckBox.setChecked(self.dacEnabled[0])

        tempQint16 = inStream.readInt16()
        self.fastSettleEnabled = bool(tempQint16)
        self.fastSettleCheckBox.setChecked(self.fastSettleEnabled)
        self.enableFastSettle(self.fastSettleCheckBox.checkState())

        tempQint16 = inStream.readInt16()
        self.plotPointsCheckBox.setChecked(bool(tempQint16))
        self.plotPointsMode(bool(tempQint16))

        self.note1LineEdit.setText(inStream.readQString())
        self.note2LineEdit.setText(inStream.readQString())
        self.note3LineEdit.setText(inStream.readQString())

        # Ports are saved in reverse order.
        port = 5
        while port >= 0:
            tempQint16 = inStream.readInt16()
            if self.signalSources.signalPort[port].enabled:
                self.wavePlot.setNumFramesPort(tempQint16, port)
            tempQint16 = inStream.readInt16()
            if self.signalSources.signalPort[port].enabled:
                self.wavePlot.setTopLeftFrame(tempQint16, port)
            port -= 1

        # Version 1.1 additions
        if (versionMain == 1 and versionSecondary >= 1) or (versionMain > 1):
            tempQint16 = inStream.readInt16()
            self.saveTemp = bool(tempQint16)

        # Version 1.2 additions
        if (versionMain == 1 and versionSecondary >= 2) or (versionMain > 1):
            tempQint16 = inStream.readInt16()
            self.recordTriggerChannel = tempQint16
            tempQint16 = inStream.readInt16()
            self.recordTriggerPolarity = tempQint16
            tempQint16 = inStream.readInt16()
            self.recordTriggerBuffer = tempQint16

            tempQint16 = inStream.readInt16()
            self.setSaveFormat(tempQint16)

            tempQint16 = inStream.readInt16()
            self.dacLockToSelectedBox.setChecked(bool(tempQint16))

        # Version 1.3 additions
        if (versionMain == 1 and versionSecondary >= 3) or (versionMain > 1):
            tempQint32 = inStream.readInt32()
            self.dac1ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold1(tempQint32)
            tempQint32 = inStream.readInt32()
            self.dac2ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold2(tempQint32)
            tempQint32 = inStream.readInt32()
            self.dac3ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold3(tempQint32)
            tempQint32 = inStream.readInt32()
            self.dac4ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold4(tempQint32)
            tempQint32 = inStream.readInt32()
            self.dac5ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold5(tempQint32)
            tempQint32 = inStream.readInt32()
            self.dac6ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold6(tempQint32)
            tempQint32 = inStream.readInt32()
            self.dac7ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold7(tempQint32)
            tempQint32 = inStream.readInt32()
            self.dac8ThresholdSpinBox.setValue(tempQint32)
            self.setDacThreshold8(tempQint32)

            tempQint16 = inStream.readInt16()
            self.saveTtlOut = bool(tempQint16)

            tempQint16 = inStream.readInt16()
            self.enableHighpassFilter(bool(tempQint16))
            self.highpassFilterCheckBox.setChecked(self.highpassFilterEnabled)

            self.highpassFilterFrequency = inStream.readDouble()
            self.highpassFilterLineEdit.setText(
                "%.2f" % self.highpassFilterFrequency)
            self.setHighpassFilterCutoff(self.highpassFilterFrequency)

        # Version 1.4 additions
        if (versionMain == 1 and versionSecondary >= 4) or (versionMain > 1):
            tempQint16 = inStream.readInt16()
            self.externalFastSettleCheckBox.setChecked(bool(tempQint16))
            self.enableExternalFastSettle(bool(tempQint16))

            tempQint16 = inStream.readInt16()
            self.externalFastSettleSpinBox.setValue(tempQint16)
            self.setExternalFastSettleChannel(tempQint16)

            tempQint16 = inStream.readInt16()
            self.auxDigOutEnabled[0] = bool(tempQint16)
            tempQint16 = inStream.readInt16()
            self.auxDigOutEnabled[1] = bool(tempQint16)
            tempQint16 = inStream.readInt16()
            self.auxDigOutEnabled[2] = bool(tempQint16)
            tempQint16 = inStream.readInt16()
            self.auxDigOutEnabled[3] = bool(tempQint16)

            tempQint16 = inStream.readInt16()
            self.auxDigOutChannel[0] = int(tempQint16)
            tempQint16 = inStream.readInt16()
            self.auxDigOutChannel[1] = int(tempQint16)
            tempQint16 = inStream.readInt16()
            self.auxDigOutChannel[2] = int(tempQint16)
            tempQint16 = inStream.readInt16()
            self.auxDigOutChannel[3] = int(tempQint16)
            self.updateAuxDigOut()

            tempQint16 = inStream.readInt16()
            self.manualDelayEnabled[0] = bool(tempQint16)
            tempQint16 = inStream.readInt16()
            self.manualDelayEnabled[1] = bool(tempQint16)
            tempQint16 = inStream.readInt16()
            self.manualDelayEnabled[2] = bool(tempQint16)
            tempQint16 = inStream.readInt16()
            self.manualDelayEnabled[3] = bool(tempQint16)

            tempQint16 = inStream.readInt16()
            self.manualDelay[0] = int(tempQint16)
            tempQint16 = inStream.readInt16()
            self.manualDelay[1] = int(tempQint16)
            tempQint16 = inStream.readInt16()
            self.manualDelay[2] = int(tempQint16)
            tempQint16 = inStream.readInt16()
            self.manualDelay[3] = int(tempQint16)

            if not self.synthMode:
                if self.manualDelayEnabled[0]:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortA, self.manualDelay[0])

                if self.manualDelayEnabled[1]:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortB, self.manualDelay[1])

                if self.manualDelayEnabled[2]:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortC, self.manualDelay[2])

                if self.manualDelayEnabled[3]:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortD, self.manualDelay[3])

        # Version 1.5 additions
        if (versionMain == 1 and versionSecondary >= 5) or (versionMain > 1):
            tempQint16 = inStream.readInt16()
            self.postTriggerTime = tempQint16
            tempQint16 = inStream.readInt16()
            self.saveTriggerChannel = bool(tempQint16)

        settingsFile.close()

        self.wavePlot.refreshScreen()
        self.statusBar().clearMessage()
        self.wavePlot.setFocus()

    # Save application settings to *.isf (Intan Settings File) file.
    def saveSettings(self):
        saveSettingsFileName, _ = QFileDialog.getSaveFileName(self,
                                                              "Select Settings Filename", ".",
                                                              "Intan Settings Files (*.isf)")

        if saveSettingsFileName == "":
            self.wavePlot.setFocus()
            return

        settingsFile = QFile(saveSettingsFileName)
        if not settingsFile.open(QIODevice.WriteOnly):
            QMessageBox.critical(self, "Cannot Save Settings File",
                                 "Cannot open new settings file for writing.")
            self.wavePlot.setFocus()
            return

        self.statusBar().showMessage("Saving settings to file...")

        # Save settings
        outStream = QDataStream(settingsFile)
        outStream.setVersion(QDataStream.Qt_4_8)
        outStream.setByteOrder(QDataStream.LittleEndian)
        outStream.setFloatingPointPrecision(QDataStream.SinglePrecision)

        outStream.writeUInt32(constants.SETTINGS_FILE_MAGIC_NUMBER)
        outStream.writeInt16(constants.SETTINGS_FILE_MAIN_VERSION_NUMBER)
        outStream.writeInt16(constants.SETTINGS_FILE_SECONDARY_VERSION_NUMBER)

        self.signalSources.writeToStream(outStream)

        outStream.writeInt16(self.sampleRateComboBox.currentIndex())
        outStream.writeInt16(self.yScaleComboBox.currentIndex())
        outStream.writeInt16(self.tScaleComboBox.currentIndex())
        outStream.writeInt16(self.notchFilterComboBox.currentIndex())
        if self.saveBaseFileName == "":
            outStream.writeQString(None)
        else:
            outStream.writeQString(self.saveBaseFileName)
        outStream.writeInt16(self.newSaveFilePeriodMinutes)
        outStream.writeInt16(self.dspEnabled)
        outStream.writeFloat(self.desiredDspCutoffFreq)
        outStream.writeFloat(self.desiredLowerBandwidth)
        outStream.writeFloat(self.desiredUpperBandwidth)
        outStream.writeFloat(self.desiredImpedanceFreq)
        outStream.writeFloat(self.actualImpedanceFreq)
        outStream.writeInt16(self.impedanceFreqValid)
        outStream.writeInt16(self.dacGainSlider.value())
        outStream.writeInt16(self.dacNoiseSuppressSlider.value())
        for i in range(8):
            outStream.writeInt16(self.dacEnabled[i])
            if self.dacSelectedChannel[i]:
                outStream.writeQString(
                    self.dacSelectedChannel[i].nativeChannelName)
            else:
                outStream.writeQString("")

        outStream.writeInt16(self.fastSettleEnabled)
        outStream.writeInt16(self.plotPointsCheckBox.isChecked())
        outStream.writeQString(self.note1LineEdit.text())
        outStream.writeQString(self.note2LineEdit.text())
        outStream.writeQString(self.note3LineEdit.text())

        # We need to save the ports in reverse order to make things
        # work out correctly when we load them again.
        port = 5
        while port >= 0:
            outStream.writeInt16(self.wavePlot.getNumFramesIndex(port))
            outStream.writeInt16(self.wavePlot.getTopLeftFrame(port))
            port -= 1

        outStream.writeInt16(self.saveTemp)     # version 1.1 addition

        # version 1.2 additions
        outStream.writeInt16(self.recordTriggerChannel)
        outStream.writeInt16(self.recordTriggerPolarity)
        outStream.writeInt16(self.recordTriggerBuffer)

        outStream.writeInt16(self.saveFormat)
        outStream.writeInt16(self.dacLockToSelectedBox.isChecked())

        # version 1.3 additions
        outStream.writeInt32(self.dac1ThresholdSpinBox.value())
        outStream.writeInt32(self.dac2ThresholdSpinBox.value())
        outStream.writeInt32(self.dac3ThresholdSpinBox.value())
        outStream.writeInt32(self.dac4ThresholdSpinBox.value())
        outStream.writeInt32(self.dac5ThresholdSpinBox.value())
        outStream.writeInt32(self.dac6ThresholdSpinBox.value())
        outStream.writeInt32(self.dac7ThresholdSpinBox.value())
        outStream.writeInt32(self.dac8ThresholdSpinBox.value())

        outStream.writeInt16(self.saveTtlOut)

        outStream.writeInt16(self.highpassFilterEnabled)
        outStream.writeDouble(self.highpassFilterFrequency)

        # version 1.4 additions
        outStream.writeInt16(self.externalFastSettleCheckBox.isChecked())
        outStream.writeInt16(self.externalFastSettleSpinBox.value())

        outStream.writeInt16(self.auxDigOutEnabled[0])
        outStream.writeInt16(self.auxDigOutEnabled[1])
        outStream.writeInt16(self.auxDigOutEnabled[2])
        outStream.writeInt16(self.auxDigOutEnabled[3])

        outStream.writeInt16(self.auxDigOutChannel[0])
        outStream.writeInt16(self.auxDigOutChannel[1])
        outStream.writeInt16(self.auxDigOutChannel[2])
        outStream.writeInt16(self.auxDigOutChannel[3])

        outStream.writeInt16(self.manualDelayEnabled[0])
        outStream.writeInt16(self.manualDelayEnabled[1])
        outStream.writeInt16(self.manualDelayEnabled[2])
        outStream.writeInt16(self.manualDelayEnabled[3])

        outStream.writeInt16(self.manualDelay[0])
        outStream.writeInt16(self.manualDelay[1])
        outStream.writeInt16(self.manualDelay[2])
        outStream.writeInt16(self.manualDelay[3])

        # version 1.5 additions
        outStream.writeInt16(self.postTriggerTime)
        outStream.writeInt16(self.saveTriggerChannel)

        settingsFile.close()

        self.statusBar().clearMessage()
        self.wavePlot.setFocus()

    # Enable or disable the display of electrode impedances.
    def showImpedances(self, enabled):
        self.wavePlot.setImpedanceLabels(enabled)
        self.wavePlot.setFocus()

    # Execute an electrode impedance measurement procedure.
    def runImpedanceMeasurement(self):
        # We can't really measure impedances in demo mode, so just return.
        if self.synthMode:
            self.showImpedanceCheckBox.setChecked(True)
            self.showImpedances(True)
            self.wavePlot.setFocus()
            return

        commandList = VectorInt()
        bufferQueue = None  # Dummy variable
        chipRegisters = Rhd2000Registers(self.boardSampleRate)

        rhd2164ChipPresent = False
        for stream in range(constants.MAX_NUM_DATA_STREAMS):
            if self.chipId[stream] == constants.CHIP_ID_RHD2164_B:
                rhd2164ChipPresent = True

        # Disable external fast settling, since this interferes with DAC commands in AuxCmd1.
        self.evalBoard.enableExternalFastSettle(False)

        # Disable auxiliary digital output control during impedance measurements.
        self.evalBoard.enableExternalDigOut(Rhd2000EvalBoard.PortA, False)
        self.evalBoard.enableExternalDigOut(Rhd2000EvalBoard.PortB, False)
        self.evalBoard.enableExternalDigOut(Rhd2000EvalBoard.PortC, False)
        self.evalBoard.enableExternalDigOut(Rhd2000EvalBoard.PortD, False)

        # Turn LEDs on to indicate that data acquisition is running.
        self.ttlOut[15] = 1
        ledArray = [1, 0, 0, 0, 0, 0, 0, 0]
        ledIndex = 0
        self.evalBoard.setLedDisplay(ledArray)
        self.evalBoard.setTtlOut(self.ttlOut)

        self.statusBar().showMessage("Measuring electrode impedances...")

        # Create a progress bar to let user know how long this will take.
        progress = QProgressDialog(
            "Measuring Electrode Impedances", "Abort", 0, 98, self)
        progress.setWindowTitle("Progress")
        progress.setMinimumDuration(0)
        progress.setModal(True)
        progress.setValue(0)

        # Create a command list for the AuxCmd1 slot.
        commandSequenceLength = chipRegisters.createCommandListZcheckDac(
            commandList, self.actualImpedanceFreq, 128.0)
        self.evalBoard.uploadCommandList(
            commandList, Rhd2000EvalBoard.AuxCmd1, 1)
        self.evalBoard.selectAuxCommandLength(Rhd2000EvalBoard.AuxCmd1,
                                              0, commandSequenceLength - 1)

        progress.setValue(1)

        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortA,
                                            Rhd2000EvalBoard.AuxCmd1, 1)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortB,
                                            Rhd2000EvalBoard.AuxCmd1, 1)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortC,
                                            Rhd2000EvalBoard.AuxCmd1, 1)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortD,
                                            Rhd2000EvalBoard.AuxCmd1, 1)

        # Select number of periods to measure impedance over
        # Test each channel for at least 20 msec...
        numPeriods = round(0.020 * self.actualImpedanceFreq)
        if numPeriods < 5:
            numPeriods = 5  # ...but always measure across no fewer than 5 complete periods

        period = self.boardSampleRate / self.actualImpedanceFreq
        # + 2 periods to give time to settle initially
        numBlocks = math.ceil((numPeriods + 2.0) * period / 60.0)
        if numBlocks < 2:
            # need first block for command to switch channels to take effect.
            numBlocks = 2

        self.actualDspCutoffFreq = chipRegisters.setDspCutoffFreq(
            self.desiredDspCutoffFreq)
        self.actualLowerBandwidth = chipRegisters.setLowerBandwidth(
            self.desiredLowerBandwidth)
        self.actualUpperBandwidth = chipRegisters.setUpperBandwidth(
            self.desiredUpperBandwidth)
        chipRegisters.enableDsp(self.dspEnabled)
        chipRegisters.enableZcheck(True)
        commandSequenceLength = chipRegisters.createCommandListRegisterConfig(
            commandList, False)

        # Upload version with no ADC calibration to AuxCmd3 RAM Bank 1.
        self.evalBoard.uploadCommandList(
            commandList, Rhd2000EvalBoard.AuxCmd3, 3)
        self.evalBoard.selectAuxCommandLength(
            Rhd2000EvalBoard.AuxCmd3, 0, commandSequenceLength - 1)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd3, 3)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd3, 3)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd3, 3)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd3, 3)

        self.evalBoard.setContinuousRunMode(False)
        self.evalBoard.setMaxTimeStep(
            constants.SAMPLES_PER_DATA_BLOCK * numBlocks)

        # Create matrices of doubles of size (numStreams x 32 x 3) to store complex amplitudes
        # of all amplifier channels (32 on each data stream) at three different Cseries values.
        measuredMagnitude = [0]*self.evalBoard.getNumEnabledDataStreams()
        measuredPhase = [0]*self.evalBoard.getNumEnabledDataStreams()

        for i in range(self.evalBoard.getNumEnabledDataStreams()):
            measuredMagnitude[i] = [0]*32
            measuredPhase[i] = [0]*32
            for j in range(32):
                measuredMagnitude[i][j] = [0]*3
                measuredPhase[i][j] = [0]*3

        # We execute three complete electrode impedance measurements: one each with
        # Cseries set to 0.1 pF, 1 pF, and 10 pF.  Then we select the best measurement
        # for each channel so that we achieve a wide impedance measurement range.
        for capRange in range(3):
            if capRange == 0:
                chipRegisters.setZcheckScale(Rhd2000Registers.ZcheckCs100fF)
                cSeries = 0.1e-12
            elif capRange == 1:
                chipRegisters.setZcheckScale(Rhd2000Registers.ZcheckCs1pF)
                cSeries = 1.0e-12
            elif capRange == 2:
                chipRegisters.setZcheckScale(Rhd2000Registers.ZcheckCs10pF)
                cSeries = 10.0e-12

            # Check all 32 channels across all active data streams.
            for channel in range(32):
                progress.setValue(32 * capRange + channel + 2)
                if progress.wasCanceled():
                    self.evalBoard.setContinuousRunMode(False)
                    self.evalBoard.setMaxTimeStep(0)
                    self.evalBoard.flush()
                    for i in range(8):
                        ledArray[i] = 0
                    self.ttlOut[15] = 0
                    self.evalBoard.setLedDisplay(ledArray)
                    self.evalBoard.setTtlOut(self.ttlOut)
                    self.statusBar().clearMessage()
                    self.wavePlot.setFocus()
                    return

                chipRegisters.setZcheckChannel(channel)
                commandSequenceLength = chipRegisters.createCommandListRegisterConfig(
                    commandList, False)
                # Upload version with no ADC calibration to AuxCmd3 RAM Bank 1.
                self.evalBoard.uploadCommandList(
                    commandList, Rhd2000EvalBoard.AuxCmd3, 3)

                self.evalBoard.run()
                while self.evalBoard.isRunning():
                    qApp.processEvents()

                self.evalBoard.readDataBlocks(numBlocks, self.dataQueue)
                _, triggerIndex = self.signalProcessor.loadAmplifierData(self.dataQueue, numBlocks, False, 0, 0, False, bufferQueue,
                                                                         False, self.saveStream, self.saveFormat, False, False, 0)
                for stream in range(self.evalBoard.getNumEnabledDataStreams()):
                    if self.chipId[stream] != constants.CHIP_ID_RHD2164_B:
                        self.signalProcessor.measureComplexAmplitude(measuredMagnitude, measuredPhase,
                                                                     capRange, stream, channel, numBlocks, self.boardSampleRate,
                                                                     self.actualImpedanceFreq, numPeriods)

                # If an RHD2164 chip is plugged in, we have to set the Zcheck select register to channels 32-63
                # and repeat the previous steps.
                if rhd2164ChipPresent:
                    chipRegisters.setZcheckChannel(
                        channel + 32)  # address channels 32-63
                    commandSequenceLength = chipRegisters.createCommandListRegisterConfig(
                        commandList, False)
                    # Upload version with no ADC calibration to AuxCmd3 RAM Bank 1.
                    self.evalBoard.uploadCommandList(
                        commandList, Rhd2000EvalBoard.AuxCmd3, 3)

                    self.evalBoard.run()
                    while self.evalBoard.isRunning():
                        qApp.processEvents()

                    self.evalBoard.readDataBlocks(numBlocks, self.dataQueue)
                    _, triggerIndex = self.signalProcessor.loadAmplifierData(self.dataQueue, numBlocks, False, 0, 0, False, bufferQueue,
                                                                             False, self.saveStream, self.saveFormat, False, False, 0)
                    for stream in range(self.evalBoard.getNumEnabledDataStreams()):
                        if self.chipId[stream] == constants.CHIP_ID_RHD2164_B:
                            self.signalProcessor.measureComplexAmplitude(measuredMagnitude, measuredPhase,
                                                                         capRange, stream, channel,  numBlocks, self.boardSampleRate,
                                                                         self.actualImpedanceFreq, numPeriods)

                # Advance LED display
                ledArray[ledIndex] = 0
                ledIndex += 1
                if ledIndex == 8:
                    ledIndex = 0
                ledArray[ledIndex] = 1
                self.evalBoard.setLedDisplay(ledArray)

        # we favor voltage readings that are closest to 250 uV: not too large,
        bestAmplitude = 250.0
        # and not too small.
        # this assumes the DAC amplitude was set to 128
        dacVoltageAmplitude = 128 * (1.225 / 256)
        # 10 pF: an estimate of on-chip parasitic capacitance.
        parasiticCapacitance = 10.0e-12
        relativeFreq = self.actualImpedanceFreq / self.boardSampleRate

        bestAmplitudeIndex = 0
        for stream in range(self.evalBoard.getNumEnabledDataStreams()):
            for channel in range(32):
                signalChannel = self.signalSources.findAmplifierChannel(
                    stream, channel)
                if signalChannel:
                    minDistance = 9.9e99  # ridiculously large number
                    for capRange in range(3):
                        # Find the measured amplitude that is closest to bestAmplitude on a logarithmic scale
                        distance = abs(
                            math.log(measuredMagnitude[stream][channel][capRange] / bestAmplitude))
                        if distance < minDistance:
                            bestAmplitudeIndex = capRange
                            minDistance = distance

                    if bestAmplitudeIndex == 0:
                        Cseries = 0.1e-12
                    elif bestAmplitudeIndex == 1:
                        Cseries = 1.0e-12
                    elif bestAmplitudeIndex == 2:
                        Cseries = 10.0e-12

                    # Calculate current amplitude produced by on-chip voltage DAC
                    current = 2.0 * math.pi * self.actualImpedanceFreq * dacVoltageAmplitude * Cseries

                    # Calculate impedance magnitude from calculated current and measured voltage.
                    impedanceMagnitude = 1.0e-6 * \
                        (measuredMagnitude[stream][channel][bestAmplitudeIndex] /
                         current) * (18.0 * relativeFreq * relativeFreq + 1.0)

                    # Calculate impedance phase, with small correction factor accounting for the
                    # 3-command SPI pipeline delay.
                    impedancePhase = measuredPhase[stream][channel][bestAmplitudeIndex] + (
                        360.0 * (3.0 / period))

                    # Factor out on-chip parasitic capacitance from impedance measurement.
                    self.factorOutParallelCapacitance(impedanceMagnitude, impedancePhase, self.actualImpedanceFreq,
                                                      parasiticCapacitance)

                    # Perform empirical resistance correction to improve accuarcy at sample rates below
                    # 15 kS/s.
                    self.empiricalResistanceCorrection(impedanceMagnitude, impedancePhase,
                                                       self.boardSampleRate)

                    signalChannel.electrodeImpedanceMagnitude = impedanceMagnitude
                    signalChannel.electrodeImpedancePhase = impedancePhase

        self.evalBoard.setContinuousRunMode(False)
        self.evalBoard.setMaxTimeStep(0)
        self.evalBoard.flush()

        # Switch back to flatline
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd1, 0)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd1, 0)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd1, 0)
        self.evalBoard.selectAuxCommandBank(
            Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd1, 0)
        self.evalBoard.selectAuxCommandLength(Rhd2000EvalBoard.AuxCmd1, 0, 59)

        if self.fastSettleEnabled:
            fastSE = 2
        else:
            fastSE = 1
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortA, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortB, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortC, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)
        self.evalBoard.selectAuxCommandBank(Rhd2000EvalBoard.PortD, Rhd2000EvalBoard.AuxCmd3,
                                            fastSE)

        progress.setValue(progress.maximum())

        # Turn off LED.
        for i in range(8):
            ledArray[i] = 0
        self.ttlOut[15] = 0
        self.evalBoard.setLedDisplay(ledArray)
        self.evalBoard.setTtlOut(self.ttlOut)

        # Re-enable external fast settling, if selected.
        self.evalBoard.enableExternalFastSettle(
            self.externalFastSettleCheckBox.isChecked())

        # Re-enable auxiliary digital output control, if selected.
        self.evalBoard.enableExternalDigOut(
            Rhd2000EvalBoard.PortA, self.auxDigOutEnabled[0])
        self.evalBoard.enableExternalDigOut(
            Rhd2000EvalBoard.PortB, self.auxDigOutEnabled[1])
        self.evalBoard.enableExternalDigOut(
            Rhd2000EvalBoard.PortC, self.auxDigOutEnabled[2])
        self.evalBoard.enableExternalDigOut(
            Rhd2000EvalBoard.PortD, self.auxDigOutEnabled[3])

        self.saveImpedancesButton.setEnabled(True)
        self.statusBar().clearMessage()
        self.showImpedanceCheckBox.setChecked(True)
        self.showImpedances(True)
        self.wavePlot.setFocus()

    # Given a measured complex impedance that is the result of an electrode impedance in parallel
    # with a parasitic capacitance (i.e., due to the amplifier input capacitance and other
    # capacitances associated with the chip bondpads), self function factors out the effect of the
    # parasitic capacitance to return the acutal electrode impedance.
    def factorOutParallelCapacitance(self, impedanceMagnitude, impedancePhase, frequency, parasiticCapacitance):
        # First, convert from polar coordinates to rectangular coordinates.
        measuredR = impedanceMagnitude * \
            math.cos(constants.DEGREES_TO_RADIANS * impedancePhase)
        measuredX = impedanceMagnitude * \
            math.sin(constants.DEGREES_TO_RADIANS * impedancePhase)

        capTerm = 2.0 * math.pi * frequency * parasiticCapacitance
        xTerm = capTerm * (measuredR * measuredR + measuredX * measuredX)
        denominator = capTerm * xTerm + 2 * capTerm * measuredX + 1
        TrueR = measuredR / denominator
        TrueX = (measuredX + xTerm) / denominator

        # Now, convert from rectangular coordinates back to polar coordinates.
        impedanceMagnitude = math.sqrt(TrueR * TrueR + TrueX * TrueX)
        impedancePhase = constants.RADIANS_TO_DEGREES * \
            math.atan2(TrueX, TrueR)
        return impedanceMagnitude, impedancePhase

    # This is a purely empirical function to correct observed errors in the real component
    # of measured electrode impedances at sampling rates below 15 kS/s.  At low sampling rates,
    # it is difficult to approximate a smooth sine wave with the on-chip voltage DAC and 10 kHz
    # 2-pole lowpass filter. This function attempts to somewhat correct for this, but a better
    # solution is to always run impedance measurements at 20 kS/s, where they seem to be most
    # accurate.
    def empiricalResistanceCorrection(self, impedanceMagnitude, impedancePhase, boardSampleRate):
        # First, convert from polar coordinates to rectangular coordinates.
        impedanceR = impedanceMagnitude * \
            math.cos(constants.DEGREES_TO_RADIANS * impedancePhase)
        impedanceX = impedanceMagnitude * \
            math.sin(constants.DEGREES_TO_RADIANS * impedancePhase)

        # Emprically derived correction factor (i.e., no physical basis for this equation).
        impedanceR /= 10.0 * math.exp(-boardSampleRate / 2500.0) * \
            math.cos(2.0 * math.pi * boardSampleRate / 15000.0) + 1.0

        # Now, convert from rectangular coordinates back to polar coordinates.
        impedanceMagnitude = math.sqrt(
            impedanceR * impedanceR + impedanceX * impedanceX)
        impedancePhase = constants.RADIANS_TO_DEGREES * \
            math.atan2(impedanceX, impedanceR)
        return impedanceMagnitude, impedancePhase

    # UNTESTED
    # Save measured electrode impedances in CSV (Comma Separated Values) text file.
    def saveImpedances(self):
        csvFileName, _ = QFileDialog.getSaveFileName(
            self, "Save Impedance Data As", ".", "CSV (Comma delimited) (*.csv)")

        if csvFileName != "":
            csvFile = QFile(csvFileName)

            if not csvFile.open(QIODevice.WriteOnly | QIODevice.Text):
                print("Cannot open CSV file for writing: " +
                      str(csvFile.errorString()) + "\n")
            out = QTextStream(csvFile)

            out.writeString("Channel Number,Channel Name,Port,Enabled,")
            out.writeString("Impedance Magnitude at ")
            out.writeDouble(self.actualImpedanceFreq)
            out.writeString(" Hz (ohms),")
            out.writeString("Impedance Phase at ")
            out.writeDouble(self.actualImpedanceFreq)
            out.writeString(" Hz (degrees),")
            out.writeString("Series RC equivalent R (Ohms),")
            out.writeString("Series RC equivalent C (Farads)")
            out.writeString("\n")

            for stream in range(self.evalBoard.getNumEnabledDataStreams()):
                for channel in range(32):
                    signalChannel = self.signalSources.findAmplifierChannel(
                        stream, channel)
                    if signalChannel != 0:
                        equivalentR = signalChannel.electrodeImpedanceMagnitude * \
                            math.cos(constants.DEGREES_TO_RADIANS *
                                     signalChannel.electrodeImpedancePhase)
                        equivalentC = 1.0 / (2.0 * math.pi * self.actualImpedanceFreq * signalChannel.electrodeImpedanceMagnitude * -
                                             1.0 * math.sin(constants.DEGREES_TO_RADIANS * signalChannel.electrodeImpedancePhase))

                        out.setRealNumberNotation(
                            QTextStream.ScientificNotation)
                        out.setRealNumberPrecision(2)

                        out.writeQString(signalChannel.nativeChannelName)
                        out.writeString(",")
                        out.writeQString(signalChannel.customChannelName)
                        out.writeString(",")
                        out.writeQString(signalChannel.signalGroup.name)
                        out.writeString(",")
                        out.write(signalChannel.enabled)  # TODO: Check this
                        out.writeString(",")
                        out.writeDouble(
                            signalChannel.electrodeImpedanceMagnitude)
                        out.writeString(",")

                        out.setRealNumberNotation(QTextStream.FixedNotation)
                        out.setRealNumberPrecision(0)

                        out.writeDouble(signalChannel.electrodeImpedancePhase)
                        out.writeString(",")

                        out.setRealNumberNotation(
                            QTextStream.ScientificNotation)
                        out.setRealNumberPrecision(2)

                        out.writeDouble(equivalentR)
                        out.writeString(",")
                        out.writeDouble(equivalentC)
                        out.writeString(",")
                        out.writeString("\n")

            csvFile.close()

        self.wavePlot.setFocus()

    def plotPointsMode(self, enabled):
        self.wavePlot.setPointPlotMode(enabled)
        self.wavePlot.setFocus()

    def setStatusBarReady(self):
        if not self.synthMode:
            self.statusBarLabel.setText("Ready.")
        else:
            self.statusBarLabel.setText(
                "No USB board connected.  Ready to run with synthesized data.")

    def setStatusBarRunning(self):
        if not self.synthMode:
            self.statusBarLabel.setText("Running.")
        else:
            self.statusBarLabel.setText("Running with synthesized data.")

    def setStatusBarRecording(self, bytesPerMinute):
        if not self.synthMode:
            self.statusBarLabel.setText("Saving data to file " + self.saveFileName + ".  (" +
                                        "%.1f" % (bytesPerMinute / (1024.0 * 1024.0)) +
                                        " MB/minute.  File size may be reduced by disabling unused inputs.)")
        else:
            self.statusBarLabel.setText("Saving synthesized data to file " + self.saveFileName + ".  (" +
                                        "%.1f" % (bytesPerMinute / (1024.0 * 1024.0)) +
                                        " MB/minute.  File size may be reduced by disabling unused inputs.)")

    def setStatusBarWaitForTrigger(self):
        if self.recordTriggerPolarity == 0:
            self.statusBarLabel.setText(
                "Waiting for logic high trigger on digital input " + str(self.recordTriggerChannel) + "...")
        else:
            self.statusBarLabel.setText(
                "Waiting for logic low trigger on digital input " + str(self.recordTriggerChannel) + "...")

    # Set the format of the saved data file.
    def setSaveFormat(self, saveFormat):
        self.saveFormat = saveFormat

    # Create and open a new save file for data (saveFile), and create a new
    # data stream (saveStream) for writing to the file.
    def startNewSaveFile(self, saveFormat):
        fileInfo = QFileInfo(self.saveBaseFileName)
        dateTime = QDateTime.currentDateTime()

        if saveFormat == constants.SaveFormatIntan:
            # Add time and date stamp to base filename.
            self.saveFileName = fileInfo.path()
            self.saveFileName += "/"
            self.saveFileName += fileInfo.baseName()
            self.saveFileName += "_"
            self.saveFileName += dateTime.toString("yyMMdd")    # date stamp
            self.saveFileName += "_"
            self.saveFileName += dateTime.toString("HHmmss")    # time stamp
            self.saveFileName += ".rhd"

            saveFile = QFile(self.saveFileName)

            if not saveFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(saveFile.errorString()) + "\n")

            self.saveStream = QDataStream(saveFile)
            self.saveStream.setVersion(QDataStream.Qt_4_8)

            # Set to little endian mode for compatibilty with MATLAB,
            # which is little endian on all platforms
            self.saveStream.setByteOrder(QDataStream.LittleEndian)

            # Write 4-byte floating-point numbers (instead of the default 8-byte numbers)
            # to save disk space.
            self.saveStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

        elif saveFormat == constants.SaveFormatFilePerSignalType:
            # Create 'save file' name for status bar display.
            self.saveFileName = fileInfo.path()
            self.saveFileName += "/"
            self.saveFileName += fileInfo.baseName()
            self.saveFileName += "_"
            self.saveFileName += dateTime.toString("yyMMdd")    # date stamp
            self.saveFileName += "_"
            self.saveFileName += dateTime.toString("HHmmss")    # time stamp

            # Create subdirectory for data, timestamp, and info files.
            subdirName = fileInfo.baseName()
            subdirName += "_"
            subdirName += dateTime.toString("yyMMdd")    # date stamp
            subdirName += "_"
            subdirName += dateTime.toString("HHmmss")    # time stamp

            qdir = QDir(fileInfo.path())
            qdir.mkdir(subdirName)

            subdir = QDir(fileInfo.path() + "/" + subdirName)

            self.infoFileName = subdir.path() + "/" + "info.rhd"

            self.signalProcessor.createTimestampFilename(subdir.path())
            self.signalProcessor.openTimestampFile()

            self.signalProcessor.createSignalTypeFilenames(subdir.path())
            self.signalProcessor.openSignalTypeFiles(self.saveTtlOut)

            self.infoFile = QFile(self.infoFileName)

            if not self.infoFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(self.infoFile.errorString()) + "\n")

            self.infoStream = QDataStream(self.infoFile)
            self.infoStream.setVersion(QDataStream.Qt_4_8)

            # Set to little endian mode for compatibilty with MATLAB,
            # which is little endian on all platforms
            self.infoStream.setByteOrder(QDataStream.LittleEndian)

            # Write 4-byte floating-point numbers (instead of the default 8-byte numbers)
            # to save disk space.
            self.infoStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

        elif saveFormat == constants.SaveFormatFilePerChannel:
            # Create 'save file' name for status bar display.
            self.saveFileName = fileInfo.path()
            self.saveFileName += "/"
            self.saveFileName += fileInfo.baseName()
            self.saveFileName += "_"
            self.saveFileName += dateTime.toString("yyMMdd")    # date stamp
            self.saveFileName += "_"
            self.saveFileName += dateTime.toString("HHmmss")    # time stamp

            # Create subdirectory for individual channel data files.
            subdirName = fileInfo.baseName()
            subdirName += "_"
            subdirName += dateTime.toString("yyMMdd")    # date stamp
            subdirName += "_"
            subdirName += dateTime.toString("HHmmss")    # time stamp

            qdir = QDir(fileInfo.path())
            qdir.mkdir(subdirName)

            subdir = QDir(fileInfo.path() + "/" + subdirName)

            # Create filename for each channel.
            self.signalProcessor.createTimestampFilename(subdir.path())
            self.signalProcessor.createFilenames(
                self.signalSources, subdir.path())

            # Open save files and output streams.
            self.signalProcessor.openTimestampFile()
            self.signalProcessor.openSaveFiles(self.signalSources)

            # Create info file.
            self.infoFileName = subdir.path() + "/" + "info.rhd"

            self.infoFile = QFile(self.infoFileName)

            if not self.infoFile.open(QIODevice.WriteOnly):
                print("Cannot open file for writing: " +
                      str(self.infoFile.errorString()) + "\n")

            self.infoStream = QDataStream(self.infoFile)
            self.infoStream.setVersion(QDataStream.Qt_4_8)

            # Set to little endian mode for compatibilty with MATLAB,
            # which is little endian on all platforms
            self.infoStream.setByteOrder(QDataStream.LittleEndian)

            # Write 4-byte floating-point numbers (instead of the default 8-byte numbers)
            # to save disk space.
            self.infoStream.setFloatingPointPrecision(
                QDataStream.SinglePrecision)

    def closeSaveFile(self, saveFormat):
        if saveFormat == constants.SaveFormatIntan:
            self.saveFile.close()
        elif saveFormat == constants.SaveFormatFilePerSignalType:
            self.signalProcessor.closeTimestampFile()
            self.signalProcessor.closeSignalTypeFiles()
            self.infoFile.close()
        elif saveFormat == constants.SaveFormatFilePerChannel:
            self.signalProcessor.closeTimestampFile()
            self.signalProcessor.closeSaveFiles(self.signalSources)
            self.infoFile.close()

    # Launch save file format selection dialog.
    def setSaveFormatDialog(self):
        saveFormatDialog = SetSaveFormatDialog(
            self.saveFormat, self.saveTemp, self.saveTtlOut, self.newSaveFilePeriodMinutes, self)

        if saveFormatDialog.exec():
            self.saveFormat = saveFormatDialog.buttonGroup.checkedId()
            self.saveTemp = (
                saveFormatDialog.saveTemperatureCheckBox.checkState() == Qt.Checked)
            self.saveTtlOut = (
                saveFormatDialog.saveTtlOutCheckBox.checkState() == Qt.Checked)
            self.newSaveFilePeriodMinutes = saveFormatDialog.recordTimeSpinBox.value()

            self.setSaveFormat(self.saveFormat)

        self.wavePlot.setFocus()

    def setDacThreshold1(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(0, threshLevel, threshold >= 0)

    def setDacThreshold2(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(1, threshLevel, threshold >= 0)

    def setDacThreshold3(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(2, threshLevel, threshold >= 0)

    def setDacThreshold4(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(3, threshLevel, threshold >= 0)

    def setDacThreshold5(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(4, threshLevel, threshold >= 0)

    def setDacThreshold6(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(5, threshLevel, threshold >= 0)

    def setDacThreshold7(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(6, threshLevel, threshold >= 0)

    def setDacThreshold8(self, threshold):
        threshLevel = round(threshold / 0.195) + 32768
        if not self.synthMode:
            self.evalBoard.setDacThreshold(7, threshLevel, threshold >= 0)

    def getEvalBoardMode(self):
        return self.evalBoardMode

    # Launch auxiliary digital output control configuration dialog.
    def configDigOutControl(self):
        self.auxDigOutConfigDialog = AuxDigOutConfigDialog(
            self.auxDigOutEnabled, self.auxDigOutChannel, self)
        if self.auxDigOutConfigDialog.exec():
            for port in range(4):
                self.auxDigOutEnabled[port] = self.auxDigOutConfigDialog.enabled(
                    port)
                self.auxDigOutChannel[port] = self.auxDigOutConfigDialog.channel(
                    port)

            self.updateAuxDigOut()

        self.wavePlot.setFocus()

    def updateAuxDigOut(self):
        if not self.synthMode:
            self.evalBoard.enableExternalDigOut(
                Rhd2000EvalBoard.PortA, self.auxDigOutEnabled[0])
            self.evalBoard.enableExternalDigOut(
                Rhd2000EvalBoard.PortB, self.auxDigOutEnabled[1])
            self.evalBoard.enableExternalDigOut(
                Rhd2000EvalBoard.PortC, self.auxDigOutEnabled[2])
            self.evalBoard.enableExternalDigOut(
                Rhd2000EvalBoard.PortD, self.auxDigOutEnabled[3])
            self.evalBoard.setExternalDigOutChannel(
                Rhd2000EvalBoard.PortA, self.auxDigOutChannel[0])
            self.evalBoard.setExternalDigOutChannel(
                Rhd2000EvalBoard.PortB, self.auxDigOutChannel[1])
            self.evalBoard.setExternalDigOutChannel(
                Rhd2000EvalBoard.PortC, self.auxDigOutChannel[2])
            self.evalBoard.setExternalDigOutChannel(
                Rhd2000EvalBoard.PortD, self.auxDigOutChannel[3])

    # Launch manual cable delay configuration dialog.
    def manualCableDelayControl(self):
        currentDelays = [0]*4
        if not self.synthMode:
            self.evalBoardgetCableDelay(currentDelays)

        manualCableDelayDialog = CableDelayDialog(
            self.manualDelayEnabled, currentDelays, self)
        if manualCableDelayDialog.exec():
            self.manualDelayEnabled[0] = manualCableDelayDialog.manualPortACheckBox.isChecked(
            )
            self.manualDelayEnabled[1] = manualCableDelayDialog.manualPortBCheckBox.isChecked(
            )
            self.manualDelayEnabled[2] = manualCableDelayDialog.manualPortCCheckBox.isChecked(
            )
            self.manualDelayEnabled[3] = manualCableDelayDialog.manualPortDCheckBox.isChecked(
            )
            if self.manualDelayEnabled[0]:
                self.manualDelay[0] = manualCableDelayDialog.delayPortASpinBox.value(
                )
                if not self.synthMode:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortA, self.manualDelay[0])

            if self.manualDelayEnabled[1]:
                self.manualDelay[1] = manualCableDelayDialog.delayPortBSpinBox.value(
                )
                if not self.synthMode:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortB, self.manualDelay[1])

            if self.manualDelayEnabled[2]:
                self.manualDelay[2] = manualCableDelayDialog.delayPortCSpinBox.value(
                )
                if not self.synthMode:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortC, self.manualDelay[2])

            if self.manualDelayEnabled[3]:
                self.manualDelay[3] = manualCableDelayDialog.delayPortDSpinBox.value(
                )
                if not self.synthMode:
                    self.evalBoard.setCableDelay(
                        Rhd2000EvalBoard.PortD, self.manualDelay[3])

        self.scanPorts()
        self.wavePlot.setFocus()

    def isRecording(self):
        return self.recording
