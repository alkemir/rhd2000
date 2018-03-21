
from PyQt5.QtWidgets import QDialog, QCheckBox, QLabel, QComboBox, QDialogButtonBox, QGroupBox, QHBoxLayout, QVBoxLayout


# Auxiliary digital output configuration dialog.
# This dialog allows users to configure real-time control of the auxiliary digital
# output pin (auxout) on each RHD2000 chip using selected digital input signals
# on the USB interface board.

class AuxDigOutConfigDialog(QDialog):
    def __init__(self, auxOutEnabledIn, auxOutChannelIn, parent):
        super().__init__(parent)

        self.auxOutEnabled = [0]*4
        self.auxOutChannel = [0]*4

        for port in range(4):
            self.auxOutEnabled[port] = auxOutEnabledIn[port]
            self.auxOutChannel[port] = auxOutChannelIn[port]

        enablePortACheckBox = QCheckBox(
            "Control auxiliary digital output on Port A from")
        enablePortACheckBox.toggled.connect(self.enablePortAChanged)
        enablePortACheckBox.setChecked(self.auxOutEnabled[0])

        enablePortBCheckBox = QCheckBox(
            "Control auxiliary digital output on Port B from")
        enablePortBCheckBox.toggled.connect(self.enablePortBChanged)
        enablePortBCheckBox.setChecked(self.auxOutEnabled[1])

        enablePortCCheckBox = QCheckBox(
            "Control auxiliary digital output on Port C from")
        enablePortCCheckBox.toggled.connect(self.enablePortCChanged)
        enablePortCCheckBox.setChecked(self.auxOutEnabled[2])

        enablePortDCheckBox = QCheckBox(
            "Control auxiliary digital output on Port D from")
        enablePortDCheckBox.toggled.connect(self.enablePortDChanged)
        enablePortDCheckBox.setChecked(self.auxOutEnabled[3])

        channelPortAComboBox = QComboBox()
        channelPortAComboBox.addItem("Digital Input 0")
        channelPortAComboBox.addItem("Digital Input 1")
        channelPortAComboBox.addItem("Digital Input 2")
        channelPortAComboBox.addItem("Digital Input 3")
        channelPortAComboBox.addItem("Digital Input 4")
        channelPortAComboBox.addItem("Digital Input 5")
        channelPortAComboBox.addItem("Digital Input 6")
        channelPortAComboBox.addItem("Digital Input 7")
        channelPortAComboBox.addItem("Digital Input 8")
        channelPortAComboBox.addItem("Digital Input 9")
        channelPortAComboBox.addItem("Digital Input 10")
        channelPortAComboBox.addItem("Digital Input 11")
        channelPortAComboBox.addItem("Digital Input 12")
        channelPortAComboBox.addItem("Digital Input 13")
        channelPortAComboBox.addItem("Digital Input 14")
        channelPortAComboBox.addItem("Digital Input 15")
        channelPortAComboBox.currentIndexChanged.connect(
            self.channelPortAChanged)
        channelPortAComboBox.setCurrentIndex(self.auxOutChannel[0])

        channelPortBComboBox = QComboBox()
        channelPortBComboBox.addItem("Digital Input 0")
        channelPortBComboBox.addItem("Digital Input 1")
        channelPortBComboBox.addItem("Digital Input 2")
        channelPortBComboBox.addItem("Digital Input 3")
        channelPortBComboBox.addItem("Digital Input 4")
        channelPortBComboBox.addItem("Digital Input 5")
        channelPortBComboBox.addItem("Digital Input 6")
        channelPortBComboBox.addItem("Digital Input 7")
        channelPortBComboBox.addItem("Digital Input 8")
        channelPortBComboBox.addItem("Digital Input 9")
        channelPortBComboBox.addItem("Digital Input 10")
        channelPortBComboBox.addItem("Digital Input 11")
        channelPortBComboBox.addItem("Digital Input 12")
        channelPortBComboBox.addItem("Digital Input 13")
        channelPortBComboBox.addItem("Digital Input 14")
        channelPortBComboBox.addItem("Digital Input 15")
        channelPortBComboBox.currentIndexChanged.connect(
            self.channelPortBChanged)
        channelPortBComboBox.setCurrentIndex(self.auxOutChannel[1])

        channelPortCComboBox = QComboBox()
        channelPortCComboBox.addItem("Digital Input 0")
        channelPortCComboBox.addItem("Digital Input 1")
        channelPortCComboBox.addItem("Digital Input 2")
        channelPortCComboBox.addItem("Digital Input 3")
        channelPortCComboBox.addItem("Digital Input 4")
        channelPortCComboBox.addItem("Digital Input 5")
        channelPortCComboBox.addItem("Digital Input 6")
        channelPortCComboBox.addItem("Digital Input 7")
        channelPortCComboBox.addItem("Digital Input 8")
        channelPortCComboBox.addItem("Digital Input 9")
        channelPortCComboBox.addItem("Digital Input 10")
        channelPortCComboBox.addItem("Digital Input 11")
        channelPortCComboBox.addItem("Digital Input 12")
        channelPortCComboBox.addItem("Digital Input 13")
        channelPortCComboBox.addItem("Digital Input 14")
        channelPortCComboBox.addItem("Digital Input 15")
        channelPortCComboBox.currentIndexChanged.connect(
            self.channelPortCChanged)
        channelPortCComboBox.setCurrentIndex(self.auxOutChannel[2])

        channelPortDComboBox = QComboBox()
        channelPortDComboBox.addItem("Digital Input 0")
        channelPortDComboBox.addItem("Digital Input 1")
        channelPortDComboBox.addItem("Digital Input 2")
        channelPortDComboBox.addItem("Digital Input 3")
        channelPortDComboBox.addItem("Digital Input 4")
        channelPortDComboBox.addItem("Digital Input 5")
        channelPortDComboBox.addItem("Digital Input 6")
        channelPortDComboBox.addItem("Digital Input 7")
        channelPortDComboBox.addItem("Digital Input 8")
        channelPortDComboBox.addItem("Digital Input 9")
        channelPortDComboBox.addItem("Digital Input 10")
        channelPortDComboBox.addItem("Digital Input 11")
        channelPortDComboBox.addItem("Digital Input 12")
        channelPortDComboBox.addItem("Digital Input 13")
        channelPortDComboBox.addItem("Digital Input 14")
        channelPortDComboBox.addItem("Digital Input 15")
        channelPortDComboBox.currentIndexChanged.connect(
            self.channelPortDChanged)
        channelPortDComboBox.setCurrentIndex(self.auxOutChannel[3])

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        portALayout = QHBoxLayout()
        portALayout.addWidget(enablePortACheckBox)
        portALayout.addWidget(channelPortAComboBox)
        portALayout.addStretch(1)

        portBLayout = QHBoxLayout()
        portBLayout.addWidget(enablePortBCheckBox)
        portBLayout.addWidget(channelPortBComboBox)
        portBLayout.addStretch(1)

        portCLayout = QHBoxLayout()
        portCLayout.addWidget(enablePortCCheckBox)
        portCLayout.addWidget(channelPortCComboBox)
        portCLayout.addStretch(1)

        portDLayout = QHBoxLayout()
        portDLayout.addWidget(enablePortDCheckBox)
        portDLayout.addWidget(channelPortDComboBox)
        portDLayout.addStretch(1)

        label1 = QLabel(
            "All RHD2000 chips have an auxiliary digital output pin <b>auxout</b> that "
            "can be controlled via the SPI interface.  This pin is brought out to a solder "
            "point <b>DO</b> on some RHD2000 amplifier boards.  This dialog enables real-time "
            "control of this pin from a user-selected digital input on the USB interface board.  "
            "A logic signal on the selected digital input will control the selected <b>auxout</b> "
            "pin with a latency of 4-5 amplifier sampling periods.  For example, if the sampling "
            "frequency is 20 kS/s, the control latency will be 200-250 microseconds.")
        label1.setWordWrap(True)

        label2 = QLabel(
            "Note that the auxiliary output pin will only be controlled while data "
            "acquisition is running, and will be pulled to ground when acquisition stops.")
        label2.setWordWrap(True)

        label3 = QLabel(
            "The <b>auxout</b> pin is capable of driving up to 2 mA of current from the 3.3V "
            "supply.  An external transistor can be added for additional current drive or voltage "
            "range.")
        label3.setWordWrap(True)

        controlLayout = QVBoxLayout()
        controlLayout.addLayout(portALayout)
        controlLayout.addLayout(portBLayout)
        controlLayout.addLayout(portCLayout)
        controlLayout.addLayout(portDLayout)

        controlBox = QGroupBox()
        controlBox.setLayout(controlLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(controlBox)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)

        self.setWindowTitle("Configure Auxiliary Digital Output Control")

    def enablePortAChanged(self, enable):
        self.auxOutEnabled[0] = enable

    def enablePortBChanged(self, enable):
        self.auxOutEnabled[1] = enable

    def enablePortCChanged(self, enable):
        self.auxOutEnabled[2] = enable

    def enablePortDChanged(self, enable):
        self.auxOutEnabled[3] = enable

    def channelPortAChanged(self, channel):
        self.auxOutChannel[0] = channel

    def channelPortBChanged(self, channel):
        self.auxOutChannel[1] = channel

    def channelPortCChanged(self, channel):
        self.auxOutChannel[2] = channel

    def channelPortDChanged(self, channel):
        self.auxOutChannel[3] = channel

    def enabled(self, port):
        return self.auxOutEnabled[port]

    def channel(self, port):
        return self.auxOutChannel[port]
