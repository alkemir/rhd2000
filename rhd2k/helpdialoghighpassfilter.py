from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap

# Software/DAC high-pass filter help dialog.


class HelpDialogHighpassFilter(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Software/DAC High-Pass Filter")

        image = QPixmap(":/images/help_diagram_software_HPFs.png", "PNG")
        imageLabel = QLabel()
        imageLabel.setPixmap(image)

        label1 = QLabel("In many neural recording applications, users may wish to record wideband "
                        "electrode waveforms (i.e., both low-frequency local field potentials and "
                        "high-frequency spikes) but view only spikes in the GUI display.  An optional "
                        "software-implemented high-pass filter is provided here for this purpose.  "
                        "When enabled, a first-order high-pass filter at the user-specified cutoff "
                        "frequency is applied to data displayed on the screen, but is not applied to "
                        "data saved to disk.")
        label1.setWordWrap(True)

        label2 = QLabel("The diagram below shows a simplified signal path from the SPI interface cable "
                        "through the RHD2000 USB interface board to the host computer running this "
                        "software.")
        label2.setWordWrap(True)

        label3 = QLabel("When the software high-pass filters are enabled, identical high-pass filters "
                        "implemented in the Spartan-6 FPGA on the RHD2000 USB interface board are also "
                        "enabled.  These filters act on up to eight amplifier signals routed "
                        "to the eight digital-to-analog converters (DACs) used for low-latency analog "
                        "signal reconstruction."
                        )
        label3.setWordWrap(True)

        label4 = QLabel("This is particularly useful when the low-latency threshold comparators (also "
                        "implemented in the FPGA) are used to detect neural spikes in the presence of "
                        "large low-frequency LFPs.  Click on the <b>DAC/Audio</b> tab to configure the "
                        "DACs and comparators.")
        label4.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(imageLabel)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(label4)

        self.setLayout(mainLayout)
