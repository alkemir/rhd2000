from PyQt5.QtWidgets import QDialog, QRadioButton, QButtonGroup, QSpinBox, QCheckBox, QDialogButtonBox
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QGroupBox, QHBoxLayout
import constants
# Save file format selection dialog.
# Allows users to select a save file format, along with various options.


class SetSaveFormatDialog(QDialog):
    def __init__(self, initSaveFormat, initSaveTemperature, initSaveTtlOut, initNewSaveFilePeriodMinutes, parent):
        super().__init__(parent)
        self.setWindowTitle("Select Saved Data File Format")

        saveFormatIntanButton = QRadioButton("Traditional Intan File Format")
        saveFormatNeuroScopeButton = QRadioButton(
            "\"One File Per Signal Type\" Format")
        saveFormatOpenEphysButton = QRadioButton(
            "\"One File Per Channel\" Format")

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(saveFormatIntanButton)
        self.buttonGroup.addButton(saveFormatNeuroScopeButton)
        self.buttonGroup.addButton(saveFormatOpenEphysButton)
        self.buttonGroup.setId(saveFormatIntanButton,
                               constants.SaveFormatIntan)
        self.buttonGroup.setId(saveFormatNeuroScopeButton,
                               constants.SaveFormatFilePerSignalType)
        self.buttonGroup.setId(saveFormatOpenEphysButton,
                               constants.SaveFormatFilePerChannel)

        if initSaveFormat == constants.SaveFormatIntan:
            saveFormatIntanButton.setChecked(True)
        elif initSaveFormat == constants.SaveFormatFilePerSignalType:
            saveFormatNeuroScopeButton.setChecked(True)
        elif initSaveFormat == constants.SaveFormatFilePerChannel:
            saveFormatOpenEphysButton.setChecked(True)

        self.recordTimeSpinBox = QSpinBox()
        self.recordTimeSpinBox.setRange(1, 999)
        self.recordTimeSpinBox.setValue(initNewSaveFilePeriodMinutes)

        self.saveTemperatureCheckBox = QCheckBox(
            "Save On-Chip Temperature Sensor Readings")
        self.saveTemperatureCheckBox.setChecked(initSaveTemperature)

        self.saveTtlOutCheckBox = QCheckBox("Save Digital Outputs")
        self.saveTtlOutCheckBox.setChecked(initSaveTtlOut)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        newFileTimeLayout = QHBoxLayout()
        newFileTimeLayout.addWidget(QLabel("Start file every"))
        newFileTimeLayout.addWidget(self.recordTimeSpinBox)
        newFileTimeLayout.addWidget(QLabel("minutes"))
        newFileTimeLayout.addStretch(1)

        label1 = QLabel("This option saves all waveforms in one file, along with records "
                        "of sampling rate, amplifier bandwidth, channel names, etc.  To keep "
                        "individual file size reasonable, a file is created every N minutes.  "
                        "These *.rhd data files may be read into MATLAB using "
                        "read_Intan_RHD2000_file.m, provided on the Intan web site.")
        label1.setWordWrap(True)

        label2 = QLabel("This option creates a subdirectory and saves raw data files for each "
                        "signal type: amplifiers, auxiliary inputs, supply voltages, board "
                        "ADC inputs, and board digital inputs.  For example, the amplifier.dat "
                        "file contains waveform data from all enabled amplifier channels.  The "
                        "time.dat file contains the timestamp vector, and an info.rhd file contains "
                        "records of sampling rate, amplifier bandwidth, channel names, etc.")
        label2.setWordWrap(True)

        label2b = QLabel(
            "These raw data files are compatible with the NeuroScope software package.")
        label2b.setWordWrap(True)

        label3 = QLabel("This option creates a subdirectory and saves each enabled waveform "
                        "in its own *.dat raw data file.  The subdirectory also contains a time.dat "
                        "file containing a timestamp vector, and an info.rhd file containing "
                        "records of sampling rate, amplifier bandwidth, channel names, etc.")
        label3.setWordWrap(True)

        boxLayout1 = QVBoxLayout()
        boxLayout1.addWidget(saveFormatIntanButton)
        boxLayout1.addWidget(label1)
        boxLayout1.addLayout(newFileTimeLayout)
        boxLayout1.addWidget(self.saveTemperatureCheckBox)

        boxLayout2 = QVBoxLayout()
        boxLayout2.addWidget(saveFormatNeuroScopeButton)
        boxLayout2.addWidget(label2)
        boxLayout2.addWidget(label2b)

        boxLayout3 = QVBoxLayout()
        boxLayout3.addWidget(saveFormatOpenEphysButton)
        boxLayout3.addWidget(label3)

        mainGroupBox1 = QGroupBox()
        mainGroupBox1.setLayout(boxLayout1)
        mainGroupBox2 = QGroupBox()
        mainGroupBox2.setLayout(boxLayout2)
        mainGroupBox3 = QGroupBox()
        mainGroupBox3.setLayout(boxLayout3)

        label4 = QLabel("To minimize the disk space required for data files, remember to "
                        "disable all unused channels, including auxiliary input and supply "
                        "voltage channels, which may be found by scrolling down below "
                        "amplifier channels in the multi-waveform display.")

        label4.setWordWrap(True)

        label5 = QLabel("For detailed information on file formats, see the "
                        "<b>RHD2000 Application note: Data file formats</b>, "
                        "available at <i>http://www.intantech.com/downloads.html</i>")

        label5.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(mainGroupBox1)
        mainLayout.addWidget(mainGroupBox2)
        mainLayout.addWidget(mainGroupBox3)
        mainLayout.addWidget(self.saveTtlOutCheckBox)
        mainLayout.addWidget(label4)
        mainLayout.addWidget(label5)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
