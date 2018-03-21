from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap

# Software notch filter help dialog.


class HelpDialogNotchFilter(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Software Notch Filter")

        image = QPixmap(":/images/help_diagram_notch_filter.png", "PNG")
        imageLabel = QLabel()
        imageLabel.setPixmap(image)

        label1 = QLabel("An optional 50 Hz or 60 Hz software notch filter can be enabled to help "
                        "remove mains interference.  The notch filter is used only for displaying data "
                        "raw data without the notch filter applied is saved to disk.  However, each data "
                        "file contains a parameter in its header noting the notch filter setting.  The "
                        "MATLAB function provided by Intan Technologies reads this parameter and, if the "
                        "notch filter was applied during recording, applies the identical notch filter "
                        "to the data extracted in MATLAB.")
        label1.setWordWrap(True)

        label2 = QLabel("The diagram below shows a simplified signal path from the SPI interface cable "
                        "through the RHD2000 USB interface board to the host computer running this "
                        "software.")
        label2.setWordWrap(True)

        label3 = QLabel("Many users find that most 50/60 Hz interference disappears when the RHD2000 "
                        "chip is placed in close proximity to the recording electrodes.  In many "
                        "applications the notch filter may not be necessary.")
        label3.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(imageLabel)

        self.setLayout(mainLayout)
