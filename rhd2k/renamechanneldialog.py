from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDialogButtonBox
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

# Rename Channel dialog.
# This dialog allows users to enter a name for the selected channel.
# A regular expression validator is used to enforce a 16-character limit
# so that the channel name appears correctly with limited screen space.


class RenameChannelDialog(QDialog):
    def __init__(self, channel, oldName, parent):
        super().__init__(parent)

        mainLayout = QVBoxLayout()
        oldNameLayout = QHBoxLayout()
        newNameLayout = QHBoxLayout()

        oldNameLayout.addWidget(
            QLabel("Old channel name: " + oldName))

        self.nameLineEdit = QLineEdit()

        # name must be 1-16 non-whitespace characters
        regExp = QRegExp("[\\S]{1,16}")
        self.nameLineEdit.setValidator(QRegExpValidator(regExp, self))

        self.nameLineEdit.textChanged.connect(self.onLineEditTextChanged)

        newNameLayout.addWidget(QLabel("channel name:"))
        newNameLayout.addWidget(self.nameLineEdit)
        newNameLayout.addWidget(QLabel("(16 characters max)"))
        newNameLayout.addStretch()

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout.addLayout(oldNameLayout)
        mainLayout.addLayout(newNameLayout)
        mainLayout.addWidget(self.buttonBox)
        # mainLayout.addStretch()

        self.setLayout(mainLayout)

        self.setWindowTitle("Rename Channel " + channel)

    # Enable OK button on valid name.
    def onLineEditTextChanged(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            self.nameLineEdit.hasAcceptableInput())
