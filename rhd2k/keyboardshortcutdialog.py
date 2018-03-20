from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QLabel


# Keyboard shortcut dialog.
# Displays a window listing keyboard shortcuts.


class KeyboardShortcutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")

        mainWindowLayout = QVBoxLayout
        mainWindowLayout.addWidget(
            QLabel("<b>&lt/, Key:</b> Zoom in on time scale"))
        mainWindowLayout.addWidget(
            QLabel("<b>&gt/. Key:</b> Zoom out on time scale"))
        mainWindowLayout.addWidget(
            QLabel("<b>+/= Key:</b> Zoom in on voltage scale"))
        mainWindowLayout.addWidget(
            QLabel("<b>-/_ Key:</b> Zoom  on voltage scale"))
        mainWindowLayout.addWidget(
            QLabel("<b>[ Key:</b> Increase number of waveforms on screen"))
        mainWindowLayout.addWidget(
            QLabel("<b>] Key:</b> Decrease number of waveforms on screen"))
        mainWindowLayout.addWidget(
            QLabel("<b>Space Bar:</b> Enable/disable selected channel"))
        mainWindowLayout.addWidget(
            QLabel("<b>Ctrl+R:</b> Rename selected channel"))
        mainWindowLayout.addWidget(
            QLabel("<b>Cursor Keys:</b> Navigate through channels"))
        mainWindowLayout.addWidget(
            QLabel("<b>Page Up/Down Keys:</b> Navigate through channel"))
        mainWindowLayout.addWidget(
            QLabel("<b>Mouse Click:</b> Select channel"))
        mainWindowLayout.addWidget(QLabel("<b>Mouse Drag:</b> Move channel"))
        mainWindowLayout.addWidget(
            QLabel("<b>Mouse Wheel:</b> Navigate through channels"))
        mainWindowLayout.addStretch(1)

        mainWindowGroupBox = QGroupBox("Main Window")
        mainWindowGroupBox.setLayout(mainWindowLayout)

        spikeScopeLayout = QVBoxLayout()
        spikeScopeLayout.addWidget(
            QLabel("<b>+/= Key:</b> Zoom in on voltage scale"))
        spikeScopeLayout.addWidget(
            QLabel("<b>-/_ Key:</b> Zoom out on voltage scale"))
        spikeScopeLayout.addWidget(
            QLabel("<b>Mouse Click:</b> Set voltage threshold level"))
        spikeScopeLayout.addWidget(
            QLabel("<b>Mouse Wheel:</b> Change voltage scale"))
        spikeScopeLayout.addStretch(1)

        spikeScopeGroupBox = QGroupBox("Spike Scope")
        spikeScopeGroupBox.setLayout(spikeScopeLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(mainWindowGroupBox)
        mainLayout.addWidget(spikeScopeGroupBox)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
