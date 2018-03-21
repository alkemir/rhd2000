from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap

# Low-latency DAC help dialog.


class HelpDialogDacs(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Low-Latency Digital-to-Analog Converters")

        image = QPixmap(":/images/help_diagram_DACs.png", "PNG")
        imageLabel = QLabel()
        imageLabel.setPixmap(image)

        label1 = QLabel("Up to eight selected amplifier channels may be routed to the eight "
                        "digital-to-analog converters (DACs) on the RHD2000 USB interface board.  "
                        "This provides compatibility with legacy analog-input data acquisition "
                        "systems.  DAC channels 1 and 2 are also connected to the left and right "
                        "channels of the 'audio line out' jack on the USB interface board.  Any "
                        "signals assigned to DACs 1 and 2 will be audible if the board is connected "
                        "to an audio amplifier using a standard 3.5-mm stereo cable.")
        label1.setWordWrap(True)

        label2 = QLabel("The selected amplifier waveforms are routed directly through the FPGA on the "
                        "USB interface board to avoid delays associated with the USB interface and software.  "
                        "The typical latency from amplifier input to DAC output is less than 200 microseconds. "
                        )
        label2.setWordWrap(True)

        label3 = QLabel("The diagram below shows a simplified signal path from the SPI interface cable "
                        "to the DACs.")
        label3.setWordWrap(True)

        label4 = QLabel("The FPGA also includes optional 'noise slicer' signal processing that can be used "
                        "to enhance the audibility of low-amplitude neural spikes in a noisy waveform.  "
                        "The operation of the noise slicer algorithm is described in the 'Analog Waveform "
                        "Reconstruction and Audio Output' section of the <b>RHD2000 evaluation "
                        "system datasheet</b> found on the Downloads page of the Intan Technologies website."
                        )
        label4.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(imageLabel)
        mainLayout.addWidget(label4)

        self.setLayout(mainLayout)
