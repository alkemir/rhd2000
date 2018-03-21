from PyQt5.QtWidgets import QDialog, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QSpinBox, QDialogButtonBox


# Triggered recording dialog.
# Allows users to select a digital input channel for a triggered
# recording session.


class TriggerRecordDialog(QDialog):
    def __init__(self, initialTriggerChannel, initialTriggerPolarity, initialTriggerBuffer, initialPostTrigger, initialSaveTriggerChannel, parent):
        super().__init__(parent)

        self.setWindowTitle("Episodic Triggered Recording Control")

        label1 = QLabel(
            "Digital or analog inputs lines may be used to trigger recording.  If an analog input line is selected, the threshold between logic high and logic low is 1.65 V.")
        label1.setWordWrap(True)

        digitalInputComboBox = QComboBox()
        digitalInputComboBox.addItem("Digital Input 0")
        digitalInputComboBox.addItem("Digital Input 1")
        digitalInputComboBox.addItem("Digital Input 2")
        digitalInputComboBox.addItem("Digital Input 3")
        digitalInputComboBox.addItem("Digital Input 4")
        digitalInputComboBox.addItem("Digital Input 5")
        digitalInputComboBox.addItem("Digital Input 6")
        digitalInputComboBox.addItem("Digital Input 7")
        digitalInputComboBox.addItem("Digital Input 8")
        digitalInputComboBox.addItem("Digital Input 9")
        digitalInputComboBox.addItem("Digital Input 10")
        digitalInputComboBox.addItem("Digital Input 11")
        digitalInputComboBox.addItem("Digital Input 12")
        digitalInputComboBox.addItem("Digital Input 13")
        digitalInputComboBox.addItem("Digital Input 14")
        digitalInputComboBox.addItem("Digital Input 15")
        digitalInputComboBox.addItem("Analog Input 1")
        digitalInputComboBox.addItem("Analog Input 2")
        digitalInputComboBox.addItem("Analog Input 3")
        digitalInputComboBox.addItem("Analog Input 4")
        digitalInputComboBox.addItem("Analog Input 5")
        digitalInputComboBox.addItem("Analog Input 6")
        digitalInputComboBox.addItem("Analog Input 7")
        digitalInputComboBox.addItem("Analog Input 8")
        digitalInputComboBox.setCurrentIndex(initialTriggerChannel)

        digitalInputComboBox.currentIndexChanged.connect(self.setDigitalInput)

        triggerPolarityComboBox = QComboBox()
        triggerPolarityComboBox.addItem("Trigger on Logic High")
        triggerPolarityComboBox.addItem("Trigger on Logic Low")
        triggerPolarityComboBox.setCurrentIndex(initialTriggerPolarity)

        triggerPolarityComboBox.currentIndexChanged.connect(
            self.setTriggerPolarity)

        self.saveTriggerChannelCheckBox = QCheckBox(
            "Automatically Save Trigger Channel")
        self.saveTriggerChannelCheckBox.setChecked(initialSaveTriggerChannel)

        triggerControls = QVBoxLayout()
        triggerControls.addWidget(digitalInputComboBox)
        triggerControls.addWidget(triggerPolarityComboBox)
        triggerControls.addWidget(self.saveTriggerChannelCheckBox)

        triggerHBox = QHBoxLayout()
        triggerHBox.addLayout(triggerControls)
        triggerHBox.addStretch(1)

        triggerLayout = QVBoxLayout()
        triggerLayout.addWidget(label1)
        triggerLayout.addLayout(triggerHBox)

        triggerGroupBox = QGroupBox("Trigger Source")
        triggerGroupBox.setLayout(triggerLayout)

        triggerHLayout = QHBoxLayout()
        triggerHLayout.addWidget(triggerGroupBox)

        recordBufferSpinBox = QSpinBox()
        recordBufferSpinBox.setRange(1, 30)
        recordBufferSpinBox.setValue(initialTriggerBuffer)

        recordBufferSpinBox.valueChanged.connect(self.recordBufferSeconds)

        bufferSpinBoxLayout = QHBoxLayout()
        bufferSpinBoxLayout.addWidget(recordBufferSpinBox)
        bufferSpinBoxLayout.addWidget(QLabel("seconds"))
        bufferSpinBoxLayout.addStretch(1)

        label2 = QLabel("If a pretrigger buffer size of N seconds is selected, "
                        "slightly more than N seconds of pretrigger data will be "
                        "saved to disk when a trigger is detected, assuming that "
                        "data acquisition has been running for at least N seconds.")
        label2.setWordWrap(True)

        bufferSelectLayout = QVBoxLayout()
        bufferSelectLayout.addWidget(
            QLabel("Pretrigger data saved (range: 1-30 seconds):"))
        bufferSelectLayout.addLayout(bufferSpinBoxLayout)
        bufferSelectLayout.addWidget(label2)

        bufferGroupBox = QGroupBox("Pretrigger Buffer")
        bufferGroupBox.setLayout(bufferSelectLayout)

        bufferHLayout = QHBoxLayout()
        bufferHLayout.addWidget(bufferGroupBox)
    #    bufferHLayout.addStretch(1)

        postTriggerSpinBox = QSpinBox()
        postTriggerSpinBox.setRange(1, 9999)
        postTriggerSpinBox.setValue(initialPostTrigger)

        postTriggerSpinBox.valueChanged.connect(self.postTriggerSeconds)

        postTriggerSpinBoxLayout = QHBoxLayout()
        postTriggerSpinBoxLayout.addWidget(postTriggerSpinBox)
        postTriggerSpinBoxLayout.addWidget(QLabel("seconds"))
        postTriggerSpinBoxLayout.addStretch(1)

        label4 = QLabel("If a posttrigger time of M seconds is selected, "
                        "slightly more than M seconds of data will be "
                        "saved to disk after the trigger is de-asserted.")
        label4.setWordWrap(True)

        postTriggerSelectLayout = QVBoxLayout()
        postTriggerSelectLayout.addWidget(
            QLabel("Posttrigger data saved (range: 1-9999 seconds):"))
        postTriggerSelectLayout.addLayout(postTriggerSpinBoxLayout)
        postTriggerSelectLayout.addWidget(label4)

        postTriggerGroupBox = QGroupBox("Posttrigger Buffer")
        postTriggerGroupBox.setLayout(postTriggerSelectLayout)

        postTriggerHLayout = QHBoxLayout()
        postTriggerHLayout.addWidget(postTriggerGroupBox)
    #    postTriggerHLayout.addStretch(1)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        label3 = QLabel("Press OK to start triggered recording with selected settings.  "
                        "Waveforms will be displayed in real time, but recording will "
                        "not start until the trigger is detected.  A tone will indicate "
                        "when the trigger has been detected.  A different tone indicates "
                        "that recording has stopped after a trigger has been de-asserted.  "
                        "Successive trigger events will create saved data files.  "
                        "Press the Stop button to exit triggered recording mode.")
        label3.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(triggerHLayout)
        mainLayout.addLayout(bufferHLayout)
        mainLayout.addLayout(postTriggerHLayout)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

        self.setDigitalInput(digitalInputComboBox.currentIndex())
        self.setTriggerPolarity(triggerPolarityComboBox.currentIndex())
        self.recordBufferSeconds(recordBufferSpinBox.value())
        self.postTriggerSeconds(postTriggerSpinBox.value())

    def setDigitalInput(self, index):
        self.digitalInput = index

    def setTriggerPolarity(self, index):
        self.triggerPolarity = index

    def recordBufferSeconds(self, value):
        self.recordBuffer = value
        self.buttonBox.setFocus()

    def postTriggerSeconds(self, value):
        self.postTriggerTime = value
        self.buttonBox.setFocus()
