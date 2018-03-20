
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtGui import QDoubleValidator


# Bandwidth selection dialog.
# This dialog allows users to select desired values for upper and lower amplifier
# bandwidth, and DSP offset-removal cutoff frequency.  Frequency constraints
# are enforced.

class BandwidthDialog(QDialog):
    def __init__(self, lowerBandwidth, upperBandwidth, dspCutoffFreq, dspEnabled, sampleRate, parent):
        super().__init__(parent)
        dspFreqGroupBox = QGroupBox("DSP Offset Removal Cutoff Frequency")
        lowFreqGroupBox = QGroupBox("Low Frequency Bandwidth")
        highFreqGroupBox = QGroupBox("High Frequency Bandwidth")

        dspFreqLayout = QVBoxLayout()
        lowFreqLayout = QVBoxLayout()
        highFreqLayout = QVBoxLayout()

        dspFreqSelectLayout = QHBoxLayout()
        lowFreqSelectLayout = QHBoxLayout()
        highFreqSelectLayout = QHBoxLayout()
        dspEnableLayout = QHBoxLayout()

        self.dspEnableCheckBox = QCheckBox()
        self.dspEnableCheckBox.toggled.connect(self.onDspCheckBoxChanged)

        dspRangeText = "DSP Cutoff Range at "
        dspRangeText += "%.2f" % (sampleRate / 1000.0)
        dspRangeText += " kS/s: "
        dspRangeText += "%.3f" % (0.000004857 * sampleRate)
        dspRangeText += " Hz to "
        dspRangeText += "%.0f" % (0.1103 * sampleRate)
        dspRangeText += " Hz."

        self.dspRangeLabel = QLabel(dspRangeText)
        self.lowRangeLabel = QLabel("Lower Bandwidth Range: 0.1 Hz to 500 Hz.")
        self.highRangeLabel = QLabel(
            "Upper Bandwidth Range: 100 Hz to 20 kHz.")

        self.dspFreqLineEdit = QLineEdit("%.2f" % dspCutoffFreq)
        self.dspFreqLineEdit.setValidator(
            QDoubleValidator(0.001, 9999.999, 3, self))
        self.dspFreqLineEdit.textChanged.connect(self.onLineEditTextChanged)

        self.lowFreqLineEdit = QLineEdit("%.2f" % lowerBandwidth)
        self.lowFreqLineEdit.setValidator(
            QDoubleValidator(0.1, 500.0, 3, self))
        self.lowFreqLineEdit.textChanged.connect(self.onLineEditTextChanged)

        self.highFreqLineEdit = QLineEdit("%.0f" % upperBandwidth)
        self.highFreqLineEdit.setValidator(
            QDoubleValidator(100.0, 20000.0, 0, self))
        self.highFreqLineEdit.textChanged.connect(self.onLineEditTextChanged)

        dspFreqSelectLayout.addWidget(QLabel("DSP Cutoff Frequency"))
        dspFreqSelectLayout.addWidget(self.dspFreqLineEdit)
        dspFreqSelectLayout.addWidget(QLabel("Hz"))
        dspFreqSelectLayout.addStretch()

        lowFreqSelectLayout.addWidget(QLabel("Amplifier Lower Bandwidth"))
        lowFreqSelectLayout.addWidget(self.lowFreqLineEdit)
        lowFreqSelectLayout.addWidget(QLabel("Hz"))
        lowFreqSelectLayout.addStretch()

        highFreqSelectLayout.addWidget(QLabel("Amplifier Upper Bandwidth"))
        highFreqSelectLayout.addWidget(self.highFreqLineEdit)
        highFreqSelectLayout.addWidget(QLabel("Hz"))
        highFreqSelectLayout.addStretch()

        dspEnableLayout.addWidget(self.dspEnableCheckBox)
        dspEnableLayout.addWidget(
            QLabel("Enable On-Chip DSP Offset Removal Filter"))
        dspEnableLayout.addStretch()

        lowFreqLayout.addLayout(lowFreqSelectLayout)
        lowFreqLayout.addWidget(self.lowRangeLabel)

        dspFreqLayout.addLayout(dspEnableLayout)
        dspFreqLayout.addLayout(dspFreqSelectLayout)
        dspFreqLayout.addWidget(self.dspRangeLabel)

        highFreqLayout.addLayout(highFreqSelectLayout)
        highFreqLayout.addWidget(self.highRangeLabel)

        dspFreqGroupBox.setLayout(dspFreqLayout)
        lowFreqGroupBox.setLayout(lowFreqLayout)
        highFreqGroupBox.setLayout(highFreqLayout)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(dspFreqGroupBox)
        mainLayout.addWidget(lowFreqGroupBox)
        mainLayout.addWidget(highFreqGroupBox)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

        self.setWindowTitle("Select Amplifier Bandwidth")

        self.onLineEditTextChanged()
        self.dspEnableCheckBox.setChecked(dspEnabled)
        self.onDspCheckBoxChanged(dspEnabled)

    # Check the validity of requested frequencies.
    def onLineEditTextChanged(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            (self.dspFreqLineEdit.hasAcceptableInput() or not self.dspEnableCheckBox.isChecked()) and
            self.lowFreqLineEdit.hasAcceptableInput() and
            self.highFreqLineEdit.hasAcceptableInput())

        if not self.dspFreqLineEdit.hasAcceptableInput() and self.dspEnableCheckBox.isChecked():
            self.dspRangeLabel.setStyleSheet("color: red")
        else:
            self.dspRangeLabel.setStyleSheet("")

        if not self.lowFreqLineEdit.hasAcceptableInput():
            self.lowRangeLabel.setStyleSheet("color: red")
        else:
            self.lowRangeLabel.setStyleSheet("")

        if not self.highFreqLineEdit.hasAcceptableInput():
            self.highRangeLabel.setStyleSheet("color: red")
        else:
            self.highRangeLabel.setStyleSheet("")

    def onDspCheckBoxChanged(self, enable):
        self.dspFreqLineEdit.setEnabled(enable)
        self.onLineEditTextChanged()
