
from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout
from PyQt5.QtGui import QPixmap


class HelpDialogChipFilters(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("RHD2000 On-Chip Filters")

        image = QPixmap()
        image.load(":/images/help_diagram_chip_filters.png", "PNG")
        imageLabel = QLabel()
        imageLabel.setPixmap(image)

        label1 = QLabel("Each amplifier on an RHD2000 chip has a pass band defined by analog circuitry "
                        "that includes a high-pass filter and a low-pass filter.  The lower end of the pass "
                        "band has a first-order high-pass characteristic.  The upper end of the pass "
                        "band is set by a third-order Butterworth low-pass filter.")
        label1.setWordWrap(True)

        label2 = QLabel("Each RHD2000 includes an on-chip module that performs digital signal processing "
                        "(DSP) to implement an additional first-order high-pass filter on each digitized amplifier "
                        "waveform.   This feature is used to remove the residual DC offset voltages associated "
                        "with the analog amplifiers.")
        label2.setWordWrap(True)

        label3 = QLabel("The diagram below shows a simplified functional diagram of one channel in an "
                        "RHD2000 chip.  For more information, consult the <b>RHD2000 series digital "
                        "physiology interface chip datasheet</b>, "
                        "which can be found on the Downloads page of the Intan Technologies website.")
        label3.setWordWrap(True)

        label4 = QLabel("The general recommendation for best linearity is to set the DSP cutoff frequency to "
                        "the desired low-frequency cutoff and to set the amplifier lower bandwidth 2x to 10x "
                        "lower than this frequency.  Note that the DSP cutoff frequency has a limited frequency "
                        "resolution (stepping in powers of two), so if a precise value of low-frequency cutoff "
                        "is required, the amplifier lower bandwidth could be used to define this and the DSP "
                        "cutoff frequency set 2x to 10x below this point.  If both the DSP cutoff frequency and "
                        "the amplifier lower bandwidth are set to the same (or similar) frequencies, the actual "
                        "3-dB cutoff frequency will be higher than either frequency due to the combined effect of "
                        "the two filters.")
        label4.setWordWrap(True)

        label5 = QLabel("For a detailed mathematical description of all three on-chip filters, visit the "
                        "Downloads page on the Intan Technologies website and consult the document <b>FAQ: "
                        "RHD2000 amplifier filter characteristics</b>."
                        )
        label5.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(imageLabel)
        mainLayout.addWidget(label4)
        mainLayout.addWidget(label5)

        self.setLayout(mainLayout)
