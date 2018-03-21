from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap

# Low-latency comparator help dialog.


class HelpDialogComparators(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Low-Latency Threshold Comparators")

        image = QPixmap(":/images/help_diagram_comparators.png", "PNG")
        imageLabel = QLabel()
        imageLabel.setPixmap(image)

        label1 = QLabel("The FPGA on the RHD2000 USB interface board implements eight low-latency "
                        "threshold comparators that generate digital signals on Digital Output Lines "
                        "0-7 when the amplifier channels routed to the DACs exceed user-specified "
                        "threshold levels.  These comparators have total latencies less than 200 "
                        "microseconds, and may be used for real-time triggering of other devices "
                        "based on the detection of neural spikes.")
        label1.setWordWrap(True)

        label2 = QLabel("The diagram below shows a simplified signal path from the SPI interface cable "
                        "to the DACs and threshold comparators")
        label2.setWordWrap(True)

        label3 = QLabel("If spike detection is to be performed on wideband neural signals that also "
                        "include low-frequency local field potentials (LFPs), the optional software/DAC "
                        "high-pass filter can be enabled to pass only spikes.  Go to the <b>Bandwidth</b> "
                        "tab to enable this filter."
                        )
        label3.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(imageLabel)
        mainLayout.addWidget(label3)

        self.setLayout(mainLayout)
