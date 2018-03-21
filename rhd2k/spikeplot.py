import math
from copy import copy

from PyQt5.QtWidgets import QWidget, QSizePolicy, QStylePainter
from PyQt5.QtCore import Qt, QRect, QSize, QPointF
from PyQt5.QtGui import QPalette, QPainter, QPixmap, QPolygonF

import constants

# The SpikePlot widget displays a triggered neural spike plot in the
# Spike Scope dialog.  Multiple spikes are plotted on top of one another
# so users may compare their shapes.  The RMS value of the waveform is
# displayed in the plot.  Users may select a new threshold value by clicking
# on the plot.  Keypresses are used to change the voltage scale of the plot.


class SpikePlot(QWidget):
    def __init__(self, inSignalProcessor, initialChannel, inSpikeScopeDialog, parent):
        super().__init__(parent)
        self.signalProcessor = inSignalProcessor
        self.spikeScopeDialog = inSpikeScopeDialog

        self.selectedChannel = initialChannel
        self.startingNewChannel = True
        self.rmsDisplayPeriod = 0
        self.savedRms = 0.0

        self.spikeWaveformIndex = 0
        self.numSpikeWaveforms = 0
        self.maxNumSpikeWaveforms = 20
        self.voltageTriggerMode = True
        self.voltageThreshold = 0
        self.digitalTriggerChannel = 0
        self.digitalEdgePolarity = True

        self.setBackgroundRole(QPalette.Window)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setFocusPolicy(Qt.StrongFocus)

        # We can plot up to 30 superimposed spike waveforms on the scope.
        self.spikeWaveform = []
        for i in range(30):
            self.spikeWaveform.append([0.0]*91)
            # Each waveform is 3 ms in duration.  We need 91 time steps for a 3 ms
            # waveform with the sample rate is set to its maximum value of 30 kS/s.

        # Buffers to hold recent history of spike waveform and digital input,
        # used to find trigger events.
        self.spikeWaveformBuffer = [0.0]*10000
        self.digitalInputBuffer = [0]*10000

        # Set up vectors of varying plot colors so that older waveforms
        # are plotted in low-contrast gray and new waveforms are plotted
        # in high-contrast blue.  Older signals fade away, like phosphor
        # traces on old-school CRT oscilloscopes.
        self.scopeColors = []
        self.scopeColors.append([0]*10)
        self.scopeColors.append([0]*20)
        self.scopeColors.append([0]*30)

        for i in range(6, 10):
            self.scopeColors[0][i] = Qt.blue
        for i in range(3, 6):
            self.scopeColors[0][i] = Qt.darkGray
        for i in range(3):
            self.scopeColors[0][i] = Qt.lightGray

        for i in range(12, 20):
            self.scopeColors[1][i] = Qt.blue
        for i in range(6, 12):
            self.scopeColors[1][i] = Qt.darkGray
        for i in range(6):
            self.scopeColors[1][i] = Qt.lightGray

        for i in range(18, 30):
            self.scopeColors[2][i] = Qt.blue
        for i in range(9, 18):
            self.scopeColors[2][i] = Qt.darkGray
        for i in range(9):
            self.scopeColors[2][i] = Qt.lightGray

        # Default values that may be overwritten.
        self.yScale = 5000
        self.setSampleRate(30000.0)

        self.pixmap = None
        self.frame = self.rect()

    # Set voltage scale.
    def setYScale(self, newYScale):
        self.yScale = newYScale
        self.initializeDisplay()

    # Set waveform sample rate.
    def setSampleRate(self, newSampleRate):
        # Calculate time step, in msec.
        self.tStepMsec = 1000.0 / newSampleRate

        # Calculate number of time steps in 3 msec sample.
        self.totalTSteps = math.ceil(3.0 / self.tStepMsec) + 1

        # Calculate number of time steps in the 1 msec pre-trigger
        # display interval.
        self.preTriggerTSteps = math.ceil(1.0 / self.tStepMsec)

        # Clear old waveforms since the sample rate has changed.
        self.numSpikeWaveforms = 0
        self.startingNewChannel = True

    # Draw axis lines on display.
    def drawAxisLines(self):
        if self.pixmap is None:
            painter = QPainter()
        else:
            painter = QPainter(self.pixmap)

        painter.eraseRect(self.frame)
        painter.setPen(Qt.darkGray)

        # Draw box outline.
        painter.drawRect(self.frame)

        # Draw horizonal zero voltage line.
        painter.drawLine(self.frame.left(), self.frame.center().y(),
                         self.frame.right(), self.frame.center().y())

        # Draw vertical lines at 0 ms and 1 ms.
        painter.drawLine(self.frame.left() + (1.0/3.0) * (self.frame.right() - self.frame.left()) + 1, self.frame.top(),
                         self.frame.left() + (1.0/3.0) * (self.frame.right() - self.frame.left()) + 1, self.frame.bottom())
        painter.drawLine(self.frame.left() + (2.0/3.0) * (self.frame.right() - self.frame.left()) + 1, self.frame.top(),
                         self.frame.left() + (2.0/3.0) * (self.frame.right() - self.frame.left()) + 1, self.frame.bottom())

        self.update()

    # Draw text around axes.
    def drawAxisText(self):
        if self.pixmap is None:
            painter = QPainter()
        else:
            painter = QPainter(self.pixmap)

        textBoxWidth = painter.fontMetrics().width(
            "+" + str(self.yScale) + " " + constants.QSTRING_MU_SYMBOL + "V")
        textBoxHeight = painter.fontMetrics().height()

        # Clear entire Widget display area.
        painter.eraseRect(self.rect())

        # Draw border around Widget display area.
        painter.setPen(Qt.darkGray)
        rect = QRect(0, 0, self.width() - 1, self.height() - 1)
        painter.drawRect(rect)

        # If the selected channel is an amplifier channel, then write the channel name and number,
        # otherwise remind the user than non-amplifier channels cannot be displayed in Spike Scope.
        if self.selectedChannel:
            if self.selectedChannel.signalType == constants.AmplifierSignal:
                painter.drawText(self.frame.right() - textBoxWidth - 1, self.frame.top() - textBoxHeight - 1,
                                 textBoxWidth, textBoxHeight,
                                 Qt.AlignRight | Qt.AlignBottom, self.selectedChannel.nativeChannelName)
                painter.drawText(self.frame.left() + 3, self.frame.top() - textBoxHeight - 1,
                                 textBoxWidth, textBoxHeight,
                                 Qt.AlignLeft | Qt.AlignBottom, self.selectedChannel.customChannelName)
            else:
                painter.drawText(self.frame.right() - 2 * textBoxWidth - 1, self.frame.top() - textBoxHeight - 1,
                                 2 * textBoxWidth, textBoxHeight,
                                 Qt.AlignRight | Qt.AlignBottom, "ONLY AMPLIFIER CHANNELS CAN BE DISPLAYED")

        # Label the voltage axis.
        painter.drawText(self.frame.left() - textBoxWidth - 2, self.frame.top() - 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignRight | Qt.AlignTop,
                         "+" + str(self.yScale) + " " + constants.QSTRING_MU_SYMBOL + "V")
        painter.drawText(self.frame.left() - textBoxWidth - 2, self.frame.center().y() - textBoxHeight / 2,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignRight | Qt.AlignVCenter, "0")
        painter.drawText(self.frame.left() - textBoxWidth - 2, self.frame.bottom() - textBoxHeight + 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignRight | Qt.AlignBottom,
                         "-" + str(self.yScale) + " " + constants.QSTRING_MU_SYMBOL + "V")

        # Label the time axis.
        painter.drawText(self.frame.left() - textBoxWidth / 2, self.frame.bottom() + 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignHCenter | Qt.AlignTop, "-1")
        painter.drawText(self.frame.left() + (1.0/3.0) * (self.frame.right() - self.frame.left()) + 1 - textBoxWidth / 2, self.frame.bottom() + 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignHCenter | Qt.AlignTop, "0")
        painter.drawText(self.frame.left() + (2.0/3.0) * (self.frame.right() - self.frame.left()) + 1 - textBoxWidth / 2, self.frame.bottom() + 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignHCenter | Qt.AlignTop, "1")
        painter.drawText(self.frame.right() - textBoxWidth + 1, self.frame.bottom() + 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignRight | Qt.AlignTop, "2 ms")

        self.update()

    # This function loads waveform data for the selected channel from the signal processor object,
    # looks for trigger events, captures 3-ms snippets of the waveform after trigger events,
    # measures the rms level of the waveform, and updates the display.
    def updateWaveform(self, numBlocks):
        # Make sure the selected channel is a valid amplifier channel
        if not self.selectedChannel:
            return
        if self.selectedChannel.signalType != constants.AmplifierSignal:
            return

        stream = self.selectedChannel.boardStream
        channel = self.selectedChannel.chipChannel

        # Load recent waveform data and digital input data into our buffers.  Also, calculate
        # waveform RMS value.
        rms = 0.0
        for i in range(constants.SAMPLES_PER_DATA_BLOCK * numBlocks):
            self.spikeWaveformBuffer[i + self.totalTSteps -
                                     1] = self.signalProcessor.amplifierPostFilter[stream][channel][i]
            rms += (self.signalProcessor.amplifierPostFilter[stream][channel][i]
                    * self.signalProcessor.amplifierPostFilter[stream][channel][i])
            self.digitalInputBuffer[i + self.totalTSteps -
                                    1] = self.signalProcessor.boardDigIn[self.digitalTriggerChannel][i]

        rms = math.sqrt(rms / (constants.SAMPLES_PER_DATA_BLOCK * numBlocks))

        # Find trigger events, and then copy waveform snippets to spikeWaveform vector.
        if self.startingNewChannel:
            index = self.preTriggerTSteps + self.totalTSteps
        else:
            index = self.preTriggerTSteps

        while index <= constants.SAMPLES_PER_DATA_BLOCK * numBlocks + self.totalTSteps - 1 - (self.totalTSteps - self.preTriggerTSteps):
            triggered = False
            if self.voltageTriggerMode:
                if self.voltageThreshold >= 0:
                    # Positive voltage threshold trigger
                    if self.spikeWaveformBuffer[index - 1] < self.voltageThreshold and self.spikeWaveformBuffer[index] >= self.voltageThreshold:
                        triggered = True
                else:
                    # Negative voltage threshold trigger
                    if self.spikeWaveformBuffer[index - 1] > self.voltageThreshold and self.spikeWaveformBuffer[index] <= self.voltageThreshold:
                        triggered = True
            else:
                if self.digitalEdgePolarity:
                    # Digital rising edge trigger
                    if self.digitalInputBuffer[index - 1] == 0 and self.digitalInputBuffer[index] == 1:
                        triggered = True
                else:
                    # Digital falling edge trigger
                    if self.digitalInputBuffer[index - 1] == 1 and self.digitalInputBuffer[index] == 0:
                        triggered = True

            # If we found a trigger event, grab waveform snippet.
            if triggered:
                index2 = 0
                for i in range(index - self.preTriggerTSteps, index + self.totalTSteps - self.preTriggerTSteps):
                    self.spikeWaveform[self.spikeWaveformIndex][index2] = self.spikeWaveformBuffer[i]
                    index2 += 1

                self.spikeWaveformIndex += 1
                if self.spikeWaveformIndex == len(self.spikeWaveform):
                    self.spikeWaveformIndex = 0

                self.numSpikeWaveforms += 1
                if self.numSpikeWaveforms > self.maxNumSpikeWaveforms:
                    self.numSpikeWaveforms = self.maxNumSpikeWaveforms

                index += self.totalTSteps - self.preTriggerTSteps
            else:
                index += 1

        # Copy tail end of waveform to beginning of spike waveform buffer, in case there is a spike
        # at the seam between two data blocks.
        index = 0
        for i in range(constants.SAMPLES_PER_DATA_BLOCK * numBlocks - self.totalTSteps + 1, constants.SAMPLES_PER_DATA_BLOCK * numBlocks):
            self.spikeWaveformBuffer[index] = self.signalProcessor.amplifierPostFilter[stream][channel][i]
            index = + 1

            if self.startingNewChannel:
                self.startingNewChannel = False

            # Update plot.
            self.updateSpikePlot(rms)

            # Plots spike waveforms and writes RMS value to display.
    def updateSpikePlot(self, rms):
        tScale = 3.0  # time scale = 3.0 ms

        colorIndex = 2
        if self.maxNumSpikeWaveforms == 10:
            colorIndex = 0
        elif self.maxNumSpikeWaveforms == 20:
            colorIndex = 1
        elif self.maxNumSpikeWaveforms == 30:
            colorIndex = 2

        self.drawAxisLines()

        if self.pixmap is None:
            painter = QPainter()
        else:
            painter = QPainter(self.pixmap)

        # Vector for waveform plot points
        polyline = [0]*self.totalTSteps

        yAxisLength = (self.frame.height() - 2) / 2.0
        tAxisLength = self.frame.width() - 1

        xOffset = self.frame.left() + 1

        # Set clipping region for plotting.
        adjustedFrame = copy(self.frame)
        adjustedFrame.adjust(0, 1, 0, 0)
        painter.setClipRect(adjustedFrame)

        xScaleFactor = tAxisLength * self.tStepMsec / tScale
        yScaleFactor = -yAxisLength / self.yScale
        yOffset = self.frame.center().y()

        index = self.maxNumSpikeWaveforms - self.numSpikeWaveforms
        for j in range(self.spikeWaveformIndex - self.numSpikeWaveforms, self.spikeWaveformIndex):
            # Build waveform
            for i in range(self.totalTSteps):
                polyline[i] = QPointF(xScaleFactor * i + xOffset, yScaleFactor *
                                      self.spikeWaveform[(j + 30) % len(self.spikeWaveform)][i] + yOffset)

            # Draw waveform
            painter.setPen(self.scopeColors[colorIndex][index])
            index += 1
            painter.drawPolyline(QPolygonF(polyline))

        # If using a voltage threshold trigger, plot a line at the threshold level.
        if self.voltageTriggerMode:
            painter.setPen(Qt.red)
            painter.drawLine(xOffset, yScaleFactor * self.voltageThreshold + yOffset,
                             xScaleFactor * (self.totalTSteps - 1) + xOffset, yScaleFactor * self.voltageThreshold + yOffset)

        painter.setClipping(False)

        # Don't update the RMS value display every time, or it will change so fast that it
        # will be hard to read.  Only update once every few times we execute this function.
        if self.rmsDisplayPeriod == 0:
            self.rmsDisplayPeriod = 5
            self.savedRms = rms
        else:
            self.rmsDisplayPeriod -= 1

        # Write RMS value to display.
        textBoxWidth = 180
        textBoxHeight = painter.fontMetrics().height()
        painter.setPen(Qt.darkGreen)

        if self.savedRms < 10.0:
            precision = "1"
        else:
            precision = "0"

        painter.drawText(self.frame.left() + 6, self.frame.top() + 5,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignLeft | Qt.AlignTop,
                         "RMS:" + ("%." + precision + "f") % self.savedRms +
                         " " + constants.QSTRING_MU_SYMBOL + "V")

        self.update()

    # If user clicks inside display, set voltage threshold to that level.
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.frame.contains(event.pos()):
                yMouse = event.pos().y()
                newThreshold = self.yScale * \
                    (self.frame.center().y() - yMouse) // (self.frame.height() // 2)
                self.setVoltageThreshold(newThreshold)
                self.spikeScopeDialog.setVoltageThresholdDisplay(newThreshold)
                self.updateSpikePlot(0.0)
        else:
            QWidget.mousePressEvent(event)

    # If user spins mouse wheel, change voltage scale.
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.spikeScopeDialog.contractYScale()
        else:
            self.spikeScopeDialog.expandYScale()

    # Keypresses to change voltage scale.
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Minus or event.key() == Qt.Key_Underscore:
            self.spikeScopeDialog.contractYScale()
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.spikeScopeDialog.expandYScale()
        else:
            super().keyPressEvent(event)

    def minimumSizeHint(self):
        return QSize(constants.SPIKEPLOT_X_SIZE, constants.SPIKEPLOT_Y_SIZE)

    def sizeHint(self):
        return QSize(constants.SPIKEPLOT_X_SIZE, constants.SPIKEPLOT_Y_SIZE)

    def paintEvent(self, event):
        stylePainter = QStylePainter(self)
        stylePainter.drawPixmap(0, 0, self.pixmap)

    def closeEvent(self, event):
        # Perform any clean-up here before application closes.
        event.accept()

    # Set the number of spikes that are plotted, superimposed, on the
    # display.
    def setMaxNumSpikeWaveforms(self, num):
        self.maxNumSpikeWaveforms = num
        self.numSpikeWaveforms = 0

    # Clear spike display.
    def clearScope(self):
        self.numSpikeWaveforms = 0
        self.drawAxisLines()

    # Select voltage threshold trigger mode if voltageMode == True, otherwise
    # select digital input trigger mode.
    def setVoltageTriggerMode(self, voltageMode):
        self.voltageTriggerMode = voltageMode
        if self.selectedChannel.signalType == constants.AmplifierSignal:
            self.selectedChannel.voltageTriggerMode = voltageMode

        self.updateSpikePlot(0.0)

    # Set voltage threshold trigger level.  We use integer threshold
    # levels (in microvolts) since there is no point going to fractional
    # microvolt accuracy.
    def setVoltageThreshold(self, threshold):
        self.voltageThreshold = threshold
        if self.selectedChannel.signalType == constants.AmplifierSignal:
            self.selectedChannel.voltageThreshold = threshold

    # Select digital input channel for digital input trigger.
    def setDigitalTriggerChannel(self, channel):
        self.digitalTriggerChannel = channel
        if self.selectedChannel.signalType == constants.AmplifierSignal:
            self.selectedChannel.digitalTriggerChannel = channel

    # Set digitial trigger edge polarity to rising or falling edge.
    def setDigitalEdgePolarity(self, risingEdge):
        self.digitalEdgePolarity = risingEdge
        if self.selectedChannel.signalType == constants.AmplifierSignal:
            self.selectedChannel.digitalEdgePolarity = risingEdge

    # Change to a new signal channel.
    def setNewChannel(self, newChannel):
        self.selectedChannel = newChannel
        self.numSpikeWaveforms = 0
        self.startingNewChannel = True
        self.rmsDisplayPeriod = 0

        self.voltageTriggerMode = self.selectedChannel.voltageTriggerMode
        self.voltageThreshold = self.selectedChannel.voltageThreshold
        self.digitalTriggerChannel = self.selectedChannel.digitalTriggerChannel
        self.digitalEdgePolarity = self.selectedChannel.digitalEdgePolarity

        self.initializeDisplay()

    def resizeEvent(self, event):
        # Pixel map used for double buffering.
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill()
        self.initializeDisplay()

    def initializeDisplay(self):
        textBoxWidth = self.fontMetrics().width(
            "+" + str(self.yScale) + " " + constants.QSTRING_MU_SYMBOL + "V")
        textBoxHeight = self.fontMetrics().height()
        self.frame = self.rect()
        self.frame.adjust(textBoxWidth + 5, textBoxHeight +
                          10, -8, -textBoxHeight - 10)

        # Initialize display.
        self.drawAxisText()
        self.drawAxisLines()
