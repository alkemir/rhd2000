from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QSpinBox, QDialogButtonBox, QHBoxLayout, QVBoxLayout, QGroupBox

# Manual SPI cable delay configuration dialog.
# This dialog allows users to select fixed values that the FPGA uses to compensate
# for signal propagation delays in the SPI interface cables.


class CableDelayDialog(QDialog):
    def __init__(self, manualDelayEnabled, currentDelay, parent):
        super().__init__(parent)
        label1 = QLabel(
            "The RHD2000 USB interface board can compensate for the nanosecond-scale time delays "
            "resulting from finite signal velocities on the SPI interface cables.  "
            "Each time the interface software is opened or the <b>Rescan Ports A-D</b> button is "
            "clicked, the software attempts to determine the optimum delay settings for each SPI "
            "port.  Sometimes this delay-setting algorithm fails, particularly when using RHD2164 "
            "chips which use a double-data-rate SPI protocol.")
        label1.setWordWrap(True)

        label2 = QLabel(
            "This dialog box allows users to override this algorithm and set delays manually.  "
            "If a particular SPI port is returning noisy signals with large discontinuities, "
            "try checking the manual delay box for that port and adjust the delay setting up or "
            "down by one.")
        label2.setWordWrap(True)

        label3 = QLabel(
            "Note that the optimum delay setting for a particular SPI cable length will change if the "
            "amplifier sampling rate is changed.")
        label3.setWordWrap(True)

        self.manualPortACheckBox = QCheckBox("Set manual delay for Port A")
        self.manualPortBCheckBox = QCheckBox("Set manual delay for Port B")
        self.manualPortCCheckBox = QCheckBox("Set manual delay for Port C")
        self.manualPortDCheckBox = QCheckBox("Set manual delay for Port D")

        self.manualPortACheckBox.setChecked(manualDelayEnabled[0])
        self.manualPortBCheckBox.setChecked(manualDelayEnabled[1])
        self.manualPortCCheckBox.setChecked(manualDelayEnabled[2])
        self.manualPortDCheckBox.setChecked(manualDelayEnabled[3])

        self.delayPortASpinBox = QSpinBox()
        self.delayPortASpinBox.setRange(0, 15)
        self.delayPortASpinBox.setValue(currentDelay[0])

        self.delayPortBSpinBox = QSpinBox()
        self.delayPortBSpinBox.setRange(0, 15)
        self.delayPortBSpinBox.setValue(currentDelay[1])

        self.delayPortCSpinBox = QSpinBox()
        self.delayPortCSpinBox.setRange(0, 15)
        self.delayPortCSpinBox.setValue(currentDelay[2])

        self.delayPortDSpinBox = QSpinBox()
        self.delayPortDSpinBox.setRange(0, 15)
        self.delayPortDSpinBox.setValue(currentDelay[3])

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        portARow = QHBoxLayout()
        portARow.addWidget(self.manualPortACheckBox)
        portARow.addStretch(1)
        portARow.addWidget(QLabel("Current delay:"))
        portARow.addWidget(self.delayPortASpinBox)

        portBRow = QHBoxLayout()
        portBRow.addWidget(self.manualPortBCheckBox)
        portBRow.addStretch(1)
        portBRow.addWidget(QLabel("Current delay:"))
        portBRow.addWidget(self.delayPortBSpinBox)

        portCRow = QHBoxLayout()
        portCRow.addWidget(self.manualPortCCheckBox)
        portCRow.addStretch(1)
        portCRow.addWidget(QLabel("Current delay:"))
        portCRow.addWidget(self.delayPortCSpinBox)

        portDRow = QHBoxLayout()
        portDRow.addWidget(self.manualPortDCheckBox)
        portDRow.addStretch(1)
        portDRow.addWidget(QLabel("Current delay:"))
        portDRow.addWidget(self.delayPortDSpinBox)

        controlLayout = QVBoxLayout()
        controlLayout.addLayout(portARow)
        controlLayout.addLayout(portBRow)
        controlLayout.addLayout(portCRow)
        controlLayout.addLayout(portDRow)

        controlBox = QGroupBox()
        controlBox.setLayout(controlLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(controlBox)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)

        self.setWindowTitle("Manual SPI Cable Delay Configuration")
