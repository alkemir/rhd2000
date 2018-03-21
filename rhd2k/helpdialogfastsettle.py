from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout


# Fast settle (blanking) help dialog.


class HelpDialogFastSettle(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Amplifier Fast Settle (Blanking)")

        label1 = QLabel("All RHD2000 chips have a hardware 'fast settle' function that rapidly "
                        "resets the analog signal path of each amplifier channel to zero to prevent "
                        "(or recover from) saturation caused by large transient input signals such as those "
                        "due to nearby stimulation.  Recovery from amplifier saturation can be slow when "
                        "the lower bandwidth is set to a low frequency (e.g., 1 Hz).")
        label1.setWordWrap(True)

        label2 = QLabel("This fast settle or 'blanking' function may be enabled manually by clicking the "
                        "<b>Manual</b> check box.  The amplifier signals will be held at zero until the box "
                        "is unchecked.")
        label2.setWordWrap(True)

        label3 = QLabel("Real-time control of the fast settle function is enabled by checking the <b>Realtime "
                        "Settle Control</b> box and selecting a digital input on the USB interface board that will "
                        "be used to activate blanking.  If this box is checked, a logic high signal on the selected "
                        "digital input will enable amplifier fast settling with a latency of 4-5 amplifier sampling "
                        "periods.  For example, if the sampling frequency is 20 kS/s, the control latency will be "
                        "200-250 microseconds.")
        label3.setWordWrap(True)

        label4 = QLabel("By applying a digital pulse coincident with (or slightly overlapping) nearby stimulation "
                        "pulses, amplifier saturation and the resulting slow amplifier recovery can be mitigated.")
        label4.setWordWrap(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label1)
        mainLayout.addWidget(label2)
        mainLayout.addWidget(label3)
        mainLayout.addWidget(label4)

        self.setLayout(mainLayout)
