#!/usr/bin/python3
# -*- coding: utf-8 -*-

from copy import copy

from PyQt5.QtWidgets import QWidget, QSizePolicy, QStylePainter
from PyQt5.QtGui import QPalette, QPainter, QPixmap, QPen, QColor, QPolygonF
from PyQt5.QtCore import Qt, QSize, QRect, QPointF, pyqtSignal

import constants

from signalchannel import SignalChannel
from rhd2000datablock import Rhd2000DataBlock


class WavePlot(QWidget):
    """
    The WavePlot widget displays multiple waveform plots in the Main Window.
    Five types of waveforms may be displayed: amplifier, auxiliary input, supply
    voltage, ADC input, and digital input waveforms.  Users may navigate through
    the displays using cursor keys, and may drag and drop displays with the mouse.
    Other keypresses are used to change the voltage and time scales of the plots.
    """

    # Emit signal.
    selectedChannelChanged = pyqtSignal(SignalChannel)

    def __init__(self, inSignalProcessor, inSignalSources, inMainWindow, parent):
        super().__init__(parent)
        self.setBackgroundRole(QPalette.Window)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setFocusPolicy(Qt.StrongFocus)

        self.signalProcessor = inSignalProcessor
        self.signalSources = inSignalSources
        self.mainWindow = inMainWindow

        self.dragging = False
        self.dragToIndex = -1

        self.impedanceLabels = False
        self.pointPlotMode = False

        self.pixmap = None
        self.selectedPort = 0
        self.plotDataOld = []
        self.tPosition = 0.0
        self.selectedFrame = []
        self.topLeftFrame = []
        self.numFramesIndex = 0
        self.yScale = 0
        self.tScale = 0
        self.sampleRate = 0
        self.frameList = []
        self.frameNumColumns = 0
        self.numUsbBlocksToPlot = 0

    def initialize(self, startingPort):
        self.selectedPort = startingPort

        # This only needs to be as large as the maximum number of frames ever
        # displayed on one port, but let's make it so big we never need to worry
        # about increasing its size.
        self.plotDataOld = [0.0]*2400

        self.tPosition = 0.0

        # Vectors to store the currently selected from (plot window) and the frame
        # in the top left of the screen for all six ports (SPI Ports A-D, ADC inputs,
        # and digital inputs).
        self.selectedFrame = [0]*6
        self.topLeftFrame = [0]*6

        self.createAllFrames()

        # Set default number of frames per screen for each port.
        self.numFramesIndex = [0]*6
        for port in range(len(self.numFramesIndex)):
            self.numFramesIndex[port] = len(self.frameList) - 1
            if self.signalSources.signalPort[port].enabled:
                while len(self.frameList[self.numFramesIndex[port]]) > self.signalSources.signalPort[port].numChannels():
                    self.numFramesIndex[port] = self.numFramesIndex[port] - 1

        self.setNumFrames(self.numFramesIndex[self.selectedPort])

    def createFrames(self, frameIndex, maxX, maxY):
        self.frameNumColumns[frameIndex] = maxX

        xSize = (self.width() - 10 - 6 * (maxX - 1)) / maxX
        xOffset = xSize + 6

        textBoxHeight = self.fontMetrics().height()

        if maxY == 8:
            ySpacing = 2 * textBoxHeight + 1
        else:
            ySpacing = 2 * textBoxHeight + 3
        yOffset = (self.height() - 4) / maxY
        ySize = yOffset - ySpacing

        self.frameList[frameIndex] = [0]*((maxY * maxX))
        frames = self.frameList[frameIndex]
        index = 0
        for y in range(maxY):
            for x in range(maxX):
                frames[index] = QRect(
                    5 + xOffset * x, 2 + textBoxHeight + yOffset * y, xSize, ySize)
                index += 1

    def setNumFrames(self, index):
        """ Change the number of waveforms visible on the screen.
            Returns the index to the new number of waveforms.
        """
        return self.setNumFramesPort(index, self.selectedPort)

    def setNumFramesPort(self, index, port):
        """ Change the number of waveforms visible on the screen.
            Returns the index to the new number of waveforms.
        """
        if index < 0 or index >= len(self.frameList):
            return self.numFramesIndex[port]

        # Make sure we don't show more frames than the number of channels
        # on the port.
        indexLargestFrameAllowed = index
        while len(self.frameList[indexLargestFrameAllowed]) > self.signalSources.signalPort[port].numChannels():
            indexLargestFrameAllowed -= 1

        self.numFramesIndex[port] = indexLargestFrameAllowed

        # We may need to adjust which frame appears in the top left corner
        # of the display once we go to a new number of frames.
        if self.topLeftFrame[port] + len(self.frameList[self.numFramesIndex[port]]) > self.signalSources.signalPort[port].numChannels():
            self.topLeftFrame[port] = self.signalSources.signalPort[port].numChannels(
            ) - len(self.frameList[self.numFramesIndex[port]])

        if self.selectedFrame[port] < self.topLeftFrame[port]:
            self.selectedFrame[port] = self.topLeftFrame[port]
        else:
            while self.selectedFrame[port] >= self.topLeftFrame[port] + len(self.frameList[self.numFramesIndex[port]]):
                self.topLeftFrame[port] += self.frameNumColumns[self.numFramesIndex[port]]

        self.dragToIndex = -1
        self.refreshScreen()
        self.mainWindow.setNumWaveformsComboBox(index)

        return indexLargestFrameAllowed

    def setTopLeftFrame(self, newTopLeftFrame, port):
        """ Select the frame that appears in the top left corner of the display.
            Returns the new top left frame index.
        """
        if newTopLeftFrame >= self.signalSources.signalPort[port].numChannels() - len(self.frameList[self.numFramesIndex[port]]):
            self.topLeftFrame[port] = self.signalSources.signalPort[port].numChannels(
            ) - len(self.frameList[self.numFramesIndex[port]])
        else:
            self.topLeftFrame[port] = newTopLeftFrame

        self.refreshPixmap()
        self.highlightFrame(self.topLeftFrame[port], False)

        return self.topLeftFrame[port]

    def getTopLeftFrame(self, port):
        return self.topLeftFrame[port]

    def getNumFramesIndex(self, port):
        return self.numFramesIndex[port]

    def setYScale(self, newYScale):
        self.yScale = newYScale
        self.refreshScreen()

    def expandYScale(self):
        """ Expand voltage axis on amplifier plots."""
        index = self.mainWindow.yScaleComboBox.currentIndex()
        if index > 0:
            self.mainWindow.yScaleComboBox.setCurrentIndex(index - 1)
            self.setYScale(self.mainWindow.yScaleList[index - 1])

    def contractYScale(self):
        """ Contract voltage axis on amplifier plots."""
        index = self.mainWindow.yScaleComboBox.currentIndex()
        if index < self.mainWindow.yScaleComboBox.count() - 1:
            self.mainWindow.yScaleComboBox.setCurrentIndex(index + 1)
            self.setYScale(self.mainWindow.yScaleList[index + 1])

    def setTScale(self, newTScale):
        self.tScale = newTScale
        self.refreshScreen()

    def expandTScale(self):
        """ Expand time scale on all plots."""
        index = self.mainWindow.tScaleComboBox.currentIndex()
        if index < self.mainWindow.tScaleComboBox.count() - 1:
            self.mainWindow.tScaleComboBox.setCurrentIndex(index + 1)
            self.setTScale(self.mainWindow.tScaleList[index + 1])

    def contractTScale(self):
        """ Contract time scale on all plots."""
        index = self.mainWindow.tScaleComboBox.currentIndex()
        if index > 0:
            self.mainWindow.tScaleComboBox.setCurrentIndex(index - 1)
            self.setTScale(self.mainWindow.tScaleList[index - 1])

    def setSampleRate(self, newSampleRate):
        """ Set sampleRate variable.  (Does not change amplifier sample rate.)"""
        self.sampleRate = newSampleRate

    def minimumSizeHint(self):
        return QSize(860, 690)

    def sizeHint(self):
        return QSize(860, 690)

    def paintEvent(self, event):
        stylePainter = QStylePainter(self)
        stylePainter.drawPixmap(0, 0, self.pixmap)

    def findClosestFrame(self, p):
        """ Returns the index of the closest waveform frame to a point on the screen.
            (Used for mouse selections.)
        """
        distance2 = 0
        smallestDistance2 = 0
        closestFrameIndex = -1
        for i in range(len(self.frameList[self.numFramesIndex[self.selectedPort]])):
            distance2 = distanceSquared(
                p, self.frameList[self.numFramesIndex[self.selectedPort]][i].center())
            if distance2 < smallestDistance2 or i == 0:
                smallestDistance2 = distance2
                closestFrameIndex = i
        return closestFrameIndex

    def mousePressEvent(self, event):
        """ Select a frame when the left mouse button is clicked."""
        if event.button() == Qt.LeftButton:
            self.highlightFrame(self.findClosestFrame(event.pos()) +
                                self.topLeftFrame[self.selectedPort], True)
        else:
            QWidget.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ If we are dragging a frame, release it in the appropriate place,
           reordering the channels on the currently selected port.
        """
        if event.button() == Qt.LeftButton:
            if self.dragging:
                self.dragging = False
                if self.dragToIndex >= 0:
                    self.drawDragIndicator(self.dragToIndex, True)
                # Move selected frame
                if self.dragToIndex + self.topLeftFrame[self.selectedPort] == self.selectedFrame[self.selectedPort]:
                    return
                if self.dragToIndex + self.topLeftFrame[self.selectedPort] > self.selectedFrame[self.selectedPort]:
                    # Move selected frame forward
                    self.signalSources.signalPort[self.selectedPort].channelByIndex(
                        self.selectedFrame[self.selectedPort]).userOrder = -10000
                    for i in range(self.selectedFrame[self.selectedPort] + 1, self.dragToIndex + self.topLeftFrame[self.selectedPort] + 1):
                        self.signalSources.signalPort[self.selectedPort].channelByIndex(
                            i).userOrder = i - 1
                    self.signalSources.signalPort[self.selectedPort].channelByIndex(
                        -10000).userOrder = i - 1
                else:
                    # Move selected frame backwards
                    self.signalSources.signalPort[self.selectedPort].channelByIndex(
                        self.selectedFrame[self.selectedPort]).userOrder = -10000
                    i = self.selectedFrame[self.selectedPort] - 1
                    while i >= self.dragToIndex + self.topLeftFrame[self.selectedPort]:
                        self.signalSources.signalPort[self.selectedPort].channelByIndex(
                            i).userOrder = i + 1
                        i -= 1

                    self.signalSources.signalPort[self.selectedPort].channelByIndex(
                        -10000).userOrder = i + 1
                self.changeSelectedFrame(
                    self.dragToIndex + self.topLeftFrame[self.selectedPort], False)
                self.refreshScreen()
        else:
            QWidget.mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """ Drag a selected frame when the mouse is moved."""
        if event.buttons() & Qt.LeftButton:
            self.dragging = True
            frameIndex = self.findClosestFrame(event.pos())
            if frameIndex != self.dragToIndex:
                if self.dragToIndex >= 0:
                    # Erase old drag target indicator
                    self.drawDragIndicator(self.dragToIndex, True)

                # Draw new drag target indicator
                self.drawDragIndicator(frameIndex, False)
                self.dragToIndex = frameIndex

    def drawDragIndicator(self, frameIndex, erase):
        """ Draw vertical line to indicate mouse drag location."""
        painter = QPainter(self.pixmap)
        frame = self.frameList[self.numFramesIndex[self.selectedPort]][frameIndex]
        if erase:
            painter.setPen(self.palette().window().color())
        else:
            painter.setPen(Qt.darkRed)
        painter.drawLine(frame.center().x() - (frame.width() / 2 + 3) + 1, frame.top() - 5,
                         frame.center().x() - (frame.width() / 2 + 3) + 1, frame.bottom() + 7)
        self.update()

    def wheelEvent(self, event):
        """ If mouse wheel is turned, move selection cursor up or down on
            the screen.
        """
        if event.angleDelta().y() < 0:
            newSelectedFrame = self.selectedFrame[self.selectedPort] + \
                self.frameNumColumns[self.numFramesIndex[self.selectedPort]]
            self.changeSelectedFrame(newSelectedFrame, False)
        else:
            newSelectedFrame = self.selectedFrame[self.selectedPort] - \
                self.frameNumColumns[self.numFramesIndex[self.selectedPort]]
            self.changeSelectedFrame(newSelectedFrame, False)

    # Parse keypress commands.
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            self.changeSelectedFrame(
                self.selectedFrame[self.selectedPort] - self.frameNumColumns[self.numFramesIndex[self.selectedPort]], False)
        elif key == Qt.Key_Down:
            self.changeSelectedFrame(
                self.selectedFrame[self.selectedPort] + self.frameNumColumns[self.numFramesIndex[self.selectedPort]], False)
        elif key == Qt.Key_Left:
            self.changeSelectedFrame(
                self.selectedFrame[self.selectedPort] - 1, False)
        elif key == Qt.Key_Right:
            self.changeSelectedFrame(
                self.selectedFrame[self.selectedPort] + 1, False)
        elif key == Qt.Key_PageUp:
            self.changeSelectedFrame(
                self.selectedFrame[self.selectedPort] - len(self.frameList[self.numFramesIndex[self.selectedPort]]), True)
        elif key == Qt.Key_PageDown:
            self.changeSelectedFrame(
                self.selectedFrame[self.selectedPort] + len(self.frameList[self.numFramesIndex[self.selectedPort]]), True)
        elif key == Qt.Key_BracketRight:
            self.setNumFrames(self.numFramesIndex[self.selectedPort] - 1)
        elif key == Qt.Key_BracketLeft:
            self.setNumFrames(self.numFramesIndex[self.selectedPort] + 1)
        elif key == Qt.Key_Comma or key == Qt.Key_Less:
            self.contractTScale()
        elif key == Qt.Key_Period or key == Qt.Key_Greater:
            self.expandTScale()
        elif key == Qt.Key_Minus or key == Qt.Key_Underscore:
            self.contractYScale()
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.expandYScale()
        elif key == Qt.Key_Space:
            self.toggleSelectedChannelEnable()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        # Perform any clean-up here before application closes.
        event.accept()

    # Change the selected frame in response to a mouse click, cursor
    # keys, or PageUp/Down keys.
    def changeSelectedFrame(self, newSelectedFrame, pageUpDown):
        if (newSelectedFrame >= self.topLeftFrame[self.selectedPort] and newSelectedFrame < self.topLeftFrame[self.selectedPort] + len(self.frameList[self.numFramesIndex[self.selectedPort]])):
            self.highlightFrame(newSelectedFrame, True)
        elif (newSelectedFrame >= 0 and newSelectedFrame < self.topLeftFrame[self.selectedPort]):
            if not pageUpDown:
                newTopLeftFrame = self.topLeftFrame[self.selectedPort] - \
                    self.frameNumColumns[self.numFramesIndex[self.selectedPort]]
            else:
                newTopLeftFrame = self.topLeftFrame[self.selectedPort] - \
                    len(self.frameList[self.numFramesIndex[self.selectedPort]])

            if newTopLeftFrame < 0:
                newTopLeftFrame = 0
            self.topLeftFrame[self.selectedPort] = newTopLeftFrame
            self.refreshPixmap()
            self.highlightFrame(newSelectedFrame, False)
        elif (newSelectedFrame < self.signalSources.signalPort[self.selectedPort].numChannels() and newSelectedFrame >= self.topLeftFrame[self.selectedPort]):
            if not pageUpDown:
                newTopLeftFrame = self.topLeftFrame[self.selectedPort] + \
                    self.frameNumColumns[self.numFramesIndex[self.selectedPort]]
            else:
                newTopLeftFrame = self.topLeftFrame[self.selectedPort] + \
                    len(self.frameList[self.numFramesIndex[self.selectedPort]])

            if newTopLeftFrame >= self.signalSources.signalPort[self.selectedPort].numChannels() - len(self.frameList[self.numFramesIndex[self.selectedPort]]):
                newTopLeftFrame = self.signalSources.signalPort[self.selectedPort].numChannels(
                ) - len(self.frameList[self.numFramesIndex[self.selectedPort]])

            self.topLeftFrame[self.selectedPort] = newTopLeftFrame
            self.refreshPixmap()
            self.highlightFrame(newSelectedFrame, False)
        else:
            if pageUpDown:
                if newSelectedFrame >= self.signalSources.signalPort[self.selectedPort].numChannels():
                    newTopLeftFrame = self.signalSources.signalPort[self.selectedPort].numChannels(
                    ) - len(self.frameList[self.numFramesIndex[self.selectedPort]])
                    self.topLeftFrame[self.selectedPort] = newTopLeftFrame
                    while newSelectedFrame >= self.signalSources.signalPort[self.selectedPort].numChannels():
                        newSelectedFrame -= self.frameNumColumns[self.numFramesIndex[self.selectedPort]]
                    self.refreshPixmap()
                    self.highlightFrame(newSelectedFrame, False)
                elif newSelectedFrame < 0:
                    newTopLeftFrame = 0
                    self.topLeftFrame[self.selectedPort] = newTopLeftFrame
                    while newSelectedFrame < 0:
                        newSelectedFrame += self.frameNumColumns[self.numFramesIndex[self.selectedPort]]
                    self.refreshPixmap()
                    self.highlightFrame(newSelectedFrame, False)

    # Highlight the selected frame and (optionally) clear the highlight
    # around a previously highlighted frame.  Then emit a signal indicating
    # that the selected channel changed, and update the list of channels that
    # are currently visible on the screen.
    def highlightFrame(self, frameIndex, eraseOldFrame):
        painter = QPainter(self.pixmap)
        painter.setPen(Qt.darkGray)

        if eraseOldFrame:
            frame = copy(self.frameList[self.numFramesIndex[self.selectedPort]][self.selectedFrame[self.selectedPort] -
                                                                                self.topLeftFrame[self.selectedPort]])
            painter.drawRect(frame)
            painter.setPen(self.palette().window().color())
            frame.adjust(-1, -1, 1, 1)
            painter.drawRect(frame)

        self.selectedFrame[self.selectedPort] = frameIndex

        painter.setPen(Qt.darkRed)
        frame = copy(self.frameList[self.numFramesIndex[self.selectedPort]][self.selectedFrame[self.selectedPort] -
                                                                            self.topLeftFrame[self.selectedPort]])
        painter.drawRect(frame)
        frame.adjust(-1, -1, 1, 1)
        painter.drawRect(frame)

        self.update()

        # Emit signal
        self.selectedChannelChanged.emit(self.selectedChannel())

        # Update list of visible channels.
        for i in range(8):
            for j in range(len(self.mainWindow.channelVisible[i])):
                self.mainWindow.channelVisible[i][j] = False
        for i in range(self.topLeftFrame[self.selectedPort], self.topLeftFrame[self.selectedPort] + len(self.frameList[self.numFramesIndex[self.selectedPort]])):
            self.mainWindow.channelVisible[self.selectedChannelIndex(
                i).boardStream][self.selectedChannelIndex(i).chipChannel] = True

    # Refresh pixel map used in double buffered graphics.
    def refreshPixmap(self):
        # Pixel map used for double buffering.
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill()

        painter = QPainter(self.pixmap)

        # Clear old display.
        painter.eraseRect(self.rect())

        # Draw box around entire display.
        painter.setPen(Qt.darkGray)
        r = QRect(self.rect())
        r.adjust(0, 0, -1, -1)
        painter.drawRect(r)

        # Plot all frames.
        for i in range(len(self.frameList[self.numFramesIndex[self.selectedPort]])):
            self.drawAxes(painter, i)

        self.tPosition = 0
        self.update()

    def createAllFrames(self):
        # Create lists of frame (plot window) dimensions for different numbers
        # of frames per screen.
        self.frameList = []
        for i in range(6):
            self.frameList.append([])
        self.frameNumColumns = [0]*6
        self.createFrames(0, 1, 1)
        self.createFrames(1, 1, 2)
        self.createFrames(2, 1, 4)
        self.createFrames(3, 2, 4)
        self.createFrames(4, 4, 4)
        self.createFrames(5, 4, 8)

    def resizeEvent(self, event):
        self.createAllFrames()
        self.refreshPixmap()

    # Plot a particular frame.
    def drawAxes(self, painter, frameNumber):
        frame = self.frameList[self.numFramesIndex[self.selectedPort]][frameNumber]

        painter.setPen(Qt.darkGray)

        painter.drawRect(frame)
        self.drawAxisLines(painter, frameNumber)
        self.drawAxisText(painter, frameNumber)

    # Return a pointer to the current selected channel.
    def selectedChannel(self):
        return self.selectedChannelIndex(self.selectedFrame[self.selectedPort])

    # Return a pointer to a particular channel on the currently selected port.
    def selectedChannelIndex(self, index):
        return self.signalSources.signalPort[self.selectedPort].channelByIndex(index)

    # Draw axis lines inside a frame.
    def drawAxisLines(self, painter, frameNumber):
        frame = self.frameList[self.numFramesIndex[self.selectedPort]][frameNumber]
        painter.setPen(Qt.darkGray)

        stype = self.selectedChannelIndex(
            frameNumber + self.topLeftFrame[self.selectedPort]).signalType
        if self.selectedChannelIndex(frameNumber + self.topLeftFrame[self.selectedPort]).enabled:
            if stype == constants.AmplifierSignal:
                # Draw V = 0V axis line.
                painter.drawLine(frame.left(), frame.center().y(),
                                 frame.right(), frame.center().y())
            elif stype == constants.SupplyVoltageSignal:
                # Draw V = 3.6V axis line.
                painter.drawLine(frame.left(), frame.top() - 0.266667 * (frame.top() - frame.bottom()) + 1,
                                 frame.right(), frame.top() - 0.266667 * (frame.top() - frame.bottom()) + 1)
                # Draw V = 3.2V axis line.
                painter.drawLine(frame.left(), frame.top() - 0.533333 * (frame.top() - frame.bottom()) + 1,
                                 frame.right(), frame.top() - 0.533333 * (frame.top() - frame.bottom()) + 1)
                # Draw V = 2.9V axis line.
                painter.drawLine(frame.left(), frame.top() - 0.733333 * (frame.top() - frame.bottom()) + 1,
                                 frame.right(), frame.top() - 0.733333 * (frame.top() - frame.bottom()) + 1)
        else:
            # Draw X showing channel is disabled.
            painter.drawLine(frame.left(), frame.top(),
                             frame.right(), frame.bottom())
            painter.drawLine(frame.left(), frame.bottom(),
                             frame.right(), frame.top())

# Draw text labels around axes of a frame.
    def drawAxisText(self, painter, frameNumber):
        textBoxWidth = 180
        textBoxHeight = painter.fontMetrics().height()

        frame = self.frameList[self.numFramesIndex[self.selectedPort]][frameNumber]

        channel = self.selectedChannelIndex(
            frameNumber + self.topLeftFrame[self.selectedPort]).nativeChannelName
        name = self.selectedChannelIndex(
            frameNumber + self.topLeftFrame[self.selectedPort]).customChannelName
        stype = self.selectedChannelIndex(
            frameNumber + self.topLeftFrame[self.selectedPort]).signalType
        enabled = self.selectedChannelIndex(
            frameNumber + self.topLeftFrame[self.selectedPort]).enabled
        electrodeImpedanceMagnitude = self.selectedChannelIndex(
            frameNumber + self.topLeftFrame[self.selectedPort]).electrodeImpedanceMagnitude
        electrodeImpedancePhase = self.selectedChannelIndex(
            frameNumber + self.topLeftFrame[self.selectedPort]).electrodeImpedancePhase
        painter.setPen(Qt.darkGray)

        # Draw vertical axis scale label.
        if stype == constants.AmplifierSignal:
            painter.drawText(frame.left() + 3, frame.top() - textBoxHeight - 1,
                             textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignBottom,
                             str(self.yScale) + " " + constants.QSTRING_MU_SYMBOL + "V")
        elif stype == constants.AuxInputSignal:
            painter.drawText(frame.left() + 3, frame.top() - textBoxHeight - 1,
                             textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignBottom,
                             "+2.5V")
        elif stype == constants.SupplyVoltageSignal:
            painter.drawText(frame.left() + 3, frame.top() - textBoxHeight - 1,
                             textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignBottom,
                             "SUPPLY")
        elif stype == constants.BoardAdcSignal:
            if self.mainWindow.getEvalBoardMode() == 1:
                painter.drawText(frame.left() + 3, frame.top() - textBoxHeight - 1,
                                 textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignBottom,
                                 constants.QSTRING_PLUSMINUS_SYMBOL + "5.0V")
            else:
                painter.drawText(frame.left() + 3, frame.top() - textBoxHeight - 1,
                                 textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignBottom,
                                 "+3.3V")
        elif stype == constants.BoardDigInSignal:
            painter.drawText(frame.left() + 3, frame.top() - textBoxHeight - 1,
                             textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignBottom,
                             "LOGIC")

        # Draw channel name and number.
        painter.drawText(frame.right() - textBoxWidth - 2, frame.top() - textBoxHeight - 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignRight | Qt.AlignBottom, name)
        painter.drawText(frame.right() - textBoxWidth - 2, frame.bottom() + 1,
                         textBoxWidth, textBoxHeight,
                         Qt.AlignRight | Qt.AlignTop, channel)

        # Draw time axis label.
        if enabled:
            painter.drawText(frame.left() + 3, frame.bottom() + 1,
                             textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignTop,
                             str(self.tScale) + " ms")
        else:
            painter.drawText(frame.left() + 3, frame.bottom() + 1,
                             textBoxWidth, textBoxHeight, Qt.AlignLeft | Qt.AlignTop,
                             "DISABLED")

        # Draw electrode impedance label (magnitude and phase).
        if (stype == constants.AmplifierSignal and self.impedanceLabels):
            if electrodeImpedanceMagnitude >= 1.0e6:
                scale = 1.0e6
                unitPrefix = "M"
            else:
                scale = 1.0e3
                unitPrefix = "k"

            if electrodeImpedanceMagnitude >= 100.0e6:
                precision = 0
            elif electrodeImpedanceMagnitude >= 10.0e6:
                precision = 1
            elif electrodeImpedanceMagnitude >= 1.0e6:
                precision = 2
            elif electrodeImpedanceMagnitude >= 100.0e3:
                precision = 0
            elif electrodeImpedanceMagnitude >= 10.0e3:
                precision = 1
            else:
                precision = 2

            painter.drawText(frame.center().x() - textBoxWidth / 2, frame.bottom() + 1,
                             textBoxWidth, textBoxHeight, Qt.AlignHCenter | Qt.AlignTop,
                             str(("%."+str(precision)+"f") % (electrodeImpedanceMagnitude / scale)) +
                             " " + unitPrefix + constants.QSTRING_OMEGA_SYMBOL +
                             "  " + constants.QSTRING_ANGLE_SYMBOL +
                             str("%.0f" % electrodeImpedancePhase) +
                             constants.QSTRING_DEGREE_SYMBOL)

    def setNumUsbBlocksToPlot(self, numBlocks):
        self.numUsbBlocksToPlot = numBlocks

    # Plot waveforms on screen.
    def drawWaveforms(self):
        painter = QPainter(self.pixmap)
        length = Rhd2000DataBlock.getSamplesPerDataBlock() * self.numUsbBlocksToPlot

        polyline = [0]*(length + 1)

        # Assume all frames are the same size.
        yAxisLength = (
            self.frameList[self.numFramesIndex[self.selectedPort]][0].height() - 2) / 2.0
        tAxisLength = self.frameList[self.numFramesIndex[self.selectedPort]][0].width(
        ) - 1

        for j in range(len(self.frameList[self.numFramesIndex[self.selectedPort]])):
            stream = self.selectedChannelIndex(
                j + self.topLeftFrame[self.selectedPort]).boardStream
            channel = self.selectedChannelIndex(
                j + self.topLeftFrame[self.selectedPort]).chipChannel
            stype = self.selectedChannelIndex(
                j + self.topLeftFrame[self.selectedPort]).signalType

            if self.selectedChannelIndex(j + self.topLeftFrame[self.selectedPort]).enabled:
                xOffset = self.frameList[self.numFramesIndex[self.selectedPort]][j].left(
                ) + 1
                xOffset += self.tPosition * tAxisLength / self.tScale

                # Set clipping region
                adjustedFrame = copy(
                    self.frameList[self.numFramesIndex[self.selectedPort]][j])
                adjustedFrame.adjust(0, 1, 0, 0)
                painter.setClipRect(adjustedFrame)

                # Erase segment of old wavefrom
                eraseBlock = copy(adjustedFrame)
                eraseBlock.setLeft(xOffset)
                eraseBlock.setRight(
                    (tAxisLength * (1000.0 / self.sampleRate) / self.tScale) * (length - 1) + xOffset)
                painter.eraseRect(eraseBlock)

                # Redraw y = 0 axis
                self.drawAxisLines(painter, j)

                if stype == constants.AmplifierSignal:
                    # Plot RHD2000 amplifier waveform

                    tStepMsec = 1000.0 / self.sampleRate
                    xScaleFactor = tAxisLength * tStepMsec / self.tScale
                    yScaleFactor = -yAxisLength / self.yScale
                    yOffset = self.frameList[self.numFramesIndex[self.selectedPort]][j].center(
                    ).y()

                    # build waveform
                    for i in range(length):
                        polyline[i+1] = QPointF(xScaleFactor * i + xOffset, yScaleFactor *
                                                self.signalProcessor.amplifierPostFilter[stream][channel][i] + yOffset)

                    # join to old waveform
                    if self.tPosition == 0.0:
                        polyline[0] = polyline[1]
                    else:
                        polyline[0] = QPointF(xScaleFactor * -1 + xOffset, yScaleFactor * self.plotDataOld[
                            j + self.topLeftFrame[self.selectedPort]] + yOffset)

                    # save last point in waveform to join to next segment
                    self.plotDataOld[j + self.topLeftFrame[self.selectedPort]
                                     ] = self.signalProcessor.amplifierPostFilter[stream][channel][length - 1]

                    # draw waveform
                    painter.setPen(Qt.blue)
                    if self.pointPlotMode:
                        painter.drawPoints(QPolygonF(polyline))
                    else:
                        painter.drawPolyline(QPolygonF(polyline))

                elif stype == constants.AuxInputSignal:
                    # Plot RHD2000 auxiliary input signal

                    tStepMsec = 1000.0 / (self.sampleRate / 4)
                    xScaleFactor = tAxisLength * tStepMsec / self.tScale
                    yScaleFactor = -(2.0 * yAxisLength) / 2.5
                    yOffset = self.frameList[self.numFramesIndex[self.selectedPort]][j].bottom(
                    )

                    # build waveform
                    for i in range(length / 4):
                        polyline[i+1] = QPointF(xScaleFactor * i + xOffset, yScaleFactor *
                                                self.signalProcessor.auxChannel[stream][channel][i] + yOffset)

                    # join to old waveform
                    if self.tPosition == 0.0:
                        polyline[0] = polyline[1]
                    else:
                        polyline[0] = QPointF(xScaleFactor * -1 + xOffset, yScaleFactor * self.plotDataOld[
                            j + self.topLeftFrame[self.selectedPort]] + yOffset)

                    # save last point in waveform to join to next segment
                    self.plotDataOld[j + self.topLeftFrame[self.selectedPort]] = self.signalProcessor.auxChannel[
                        stream][channel][(length / 4) - 1]

                    # draw waveform
                    pen = QPen()
                    pen.setColor(QColor(200, 50, 50))
                    painter.setPen(pen)
                    polyline = polyline[:(length // 4) + 1]
                    if self.pointPlotMode:
                        painter.drawPoints(QPolygonF(polyline))
                    else:
                        painter.drawPolyline(QPolygonF(polyline))

                elif stype == constants.SupplyVoltageSignal:
                    # Plot RHD2000 supply voltage signal

                    tStepMsec = 1000.0 / (self.sampleRate / 60.0)
                    xScaleFactor = tAxisLength * tStepMsec / self.tScale
                    yScaleFactor = -(2.0 * yAxisLength) / 1.5
                    yOffset = self.frameList[self.numFramesIndex[self.selectedPort]][j].bottom(
                    )

                    voltageLow = False
                    voltageOutOfRange = False

                    # build waveform
                    for i in range(length / 60):
                        voltage = self.signalProcessor.supplyVoltage[stream][i]
                        polyline[i+1] = QPointF(xScaleFactor * i + xOffset,
                                                yScaleFactor * (voltage - 2.5) + yOffset)
                        if voltage < 2.9 or voltage > 3.6:
                            voltageOutOfRange = True
                        elif voltage < 3.2:
                            voltageLow = True

                    # join to old waveform
                    if self.tPosition == 0.0:
                        polyline[0] = polyline[1]
                    else:
                        polyline[0] = QPointF(xScaleFactor * -1 + xOffset, yScaleFactor * (
                            self.plotDataOld[j + self.topLeftFrame[self.selectedPort]] - 2.5) + yOffset)

                    # save last point in waveform to join to next segment
                    self.plotDataOld[j + self.topLeftFrame[self.selectedPort]
                                     ] = self.signalProcessor.supplyVoltage[stream][(length / 60) - 1]

                    # draw waveform
                    painter.setPen(Qt.green)
                    if voltageLow:
                        painter.setPen(Qt.yellow)
                    if voltageOutOfRange:
                        painter.setPen(Qt.red)

                    polyline = polyline[:(length // 60) + 1]
                    if self.pointPlotMode:
                        painter.drawPoints(QPolygonF(polyline))
                    else:
                        painter.drawPolyline(QPolygonF(polyline))

                elif stype == constants.BoardAdcSignal:
                    # Plot USB interface board ADC input signal

                    tStepMsec = 1000.0 / self.sampleRate
                    xScaleFactor = tAxisLength * tStepMsec / self.tScale
                    yScaleFactor = -(2.0 * yAxisLength) / 3.3
                    yOffset = self.frameList[self.numFramesIndex[self.selectedPort]][j].bottom(
                    )

                    # build waveform
                    for i in range(length):
                        polyline[i+1] = QPointF(xScaleFactor * i + xOffset, yScaleFactor *
                                                self.signalProcessor.boardAdc[channel][i] + yOffset)

                    # join to old waveform
                    if self.tPosition == 0.0:
                        polyline[0] = polyline[1]
                    else:
                        polyline[0] = QPointF(xScaleFactor * -1 + xOffset, yScaleFactor * self.plotDataOld[
                            j + self.topLeftFrame[self.selectedPort]] + yOffset)

                    # save last point in waveform to join to next segment
                    self.plotDataOld[j + self.topLeftFrame[self.selectedPort]
                                     ] = self.signalProcessor.boardAdc[channel][length - 1]

                    # draw waveform
                    painter.setPen(Qt.darkGreen)
                    if self.pointPlotMode:
                        painter.drawPoints(QPolygonF(polyline))
                    else:
                        painter.drawPolyline(QPolygonF(polyline))

                elif stype == constants.BoardDigInSignal:
                    # Plot USB interface board digital input signal

                    tStepMsec = 1000.0 / self.sampleRate
                    xScaleFactor = tAxisLength * tStepMsec / self.tScale
                    yScaleFactor = -(2.0 * yAxisLength) / 2.0
                    yOffset = (self.frameList[self.numFramesIndex[self.selectedPort]][j].bottom() +
                               self.frameList[self.numFramesIndex[self.selectedPort]][j].center().y()) / 2.0

                    # build waveform
                    for i in range(length):
                        polyline[i+1] = QPointF(xScaleFactor * i + xOffset, yScaleFactor *
                                                self.signalProcessor.boardDigIn[channel][i] + yOffset)

                    # join to old waveform
                    if self.tPosition == 0.0:
                        polyline[0] = polyline[1]
                    else:
                        polyline[0] = QPointF(xScaleFactor * -1 + xOffset, yScaleFactor * self.plotDataOld[
                            j + self.topLeftFrame[self.selectedPort]] + yOffset)

                    # save last point in waveform to join to next segment
                    self.plotDataOld[j + self.topLeftFrame[self.selectedPort]
                                     ] = self.signalProcessor.boardDigIn[channel][length - 1]

                    # draw waveform
                    pen = QPen()
                    pen.setColor(QColor(200, 50, 200))
                    painter.setPen(pen)
                    if self.pointPlotMode:
                        painter.drawPoints(QPolygonF(polyline))
                    else:
                        painter.drawPolyline(QPolygonF(polyline))
                painter.setClipping(False)

        tStepMsec = 1000.0 / self.sampleRate
        self.tPosition += length * tStepMsec
        if self.tPosition >= self.tScale:
            self.tPosition = 0.0

    def refreshScreen(self):
        self.refreshPixmap()
        self.highlightFrame(self.selectedFrame[self.selectedPort], False)

    # Switch to new port.
    def setPort(self, port):
        self.selectedPort = port
        self.refreshScreen()
        self.mainWindow.setNumWaveformsComboBox(self.numFramesIndex[port])

        return self.numFramesIndex[self.selectedPort]

    # Return custom (user-selected) name of selected channel.
    def getChannelName(self):
        return self.selectedChannelIndex(self.selectedFrame[self.selectedPort]).customChannelName

    # Return custom (user-selected) name of specified channel.
    def getChannelNamePort(self, port, index):
        return self.signalSources.signalPort[port].channelByIndex(index).customChannelName

    # Return native name (e.g., "A-05") of selected channel.
    def getNativeChannelName(self):
        return self.selectedChannelIndex(self.selectedFrame[self.selectedPort]).nativeChannelName

    # Return native name (e.g., "A-05") of specified channel.
    def getNativeChannelNamePort(self, port, index):
        return self.signalSources.signalPort[port].channelByIndex(index).nativeChannelName

    # Rename selected channel.
    def setChannelName(self, name):
        self.signalSources.signalPort[self.selectedPort].channelByIndex(
            self.selectedFrame[self.selectedPort]).customChannelName = name
        self.signalSources.signalPort[self.selectedPort].updateAlphabeticalOrder(
        )

    # Rename specified channel.
    def setChannelNamePort(self, name, port, index):
        self.signalSources.signalPort[port].channelByIndex(
            index).customChannelName = name
        self.signalSources.signalPort[self.selectedPort].updateAlphabeticalOrder(
        )

    def sortChannelsByName(self):
        self.signalSources.signalPort[self.selectedPort].setAlphabeticalChannelOrder(
        )

    def sortChannelsByNumber(self):
        self.signalSources.signalPort[self.selectedPort].setOriginalChannelOrder(
        )

    def isSelectedChannelEnabled(self):
        return self.selectedChannelIndex(self.selectedFrame[self.selectedPort]).enabled

    # Enable or disable selected channel.
    def setSelectedChannelEnable(self, enabled):
        self.signalSources.signalPort[self.selectedPort].channelByIndex(
            self.selectedFrame[self.selectedPort]).enabled = enabled
        self.refreshScreen()

    # Toggle enable status of selected channel.
    def toggleSelectedChannelEnable(self):
        if not self.mainWindow.isRecording():
            self.setSelectedChannelEnable(not self.isSelectedChannelEnabled())

    # Enable all channels on currently selected port.
    def enableAllChannels(self):
        for i in range(self.signalSources.signalPort[self.selectedPort].numChannels()):
            self.signalSources.signalPort[self.selectedPort].channelByNativeOrder(
                i).enabled = True
        self.refreshScreen()

    # Disable all channels on currently selected port.
    def disableAllChannels(self):
        for i in range(self.signalSources.signalPort[self.selectedPort].numChannels()):
            self.signalSources.signalPort[self.selectedPort].channelByNativeOrder(
                i).enabled = False
        self.refreshScreen()

    # Update display when new data is available.
    def passFilteredData(self):
        self.drawWaveforms()
        self.update()

    # Enable or disable electrode impedance labels on display.
    def setImpedanceLabels(self, enabled):
        self.impedanceLabels = enabled
        self.refreshScreen()

    # Enable or disable point plotting mode (to reduce CPU load).
    def setPointPlotMode(self, enabled):
        self.pointPlotMode = enabled


# Allocates memory for a 3-D array of doubles.
def allocateDoubleArray3D(xSize, ySize, zSize):
    ret = [0]*xSize
    for i in range(xSize):
        ret[i] = [0]*ySize
        for j in range(ySize):
            ret[i][j] = [0.0]*zSize
    return ret

# Allocates memory for a 2-D array of doubles.


def allocateDoubleArray2D(xSize, ySize):
    ret = [0]*xSize

    for i in range(xSize):
        ret[i] = [0.0]*ySize
    return ret

# Allocates memory for a 2-D array of integers.


def allocateIntArray2D(xSize, ySize):
    ret = [0]*xSize

    for i in range(xSize):
        ret[i] = [0]*ySize
    return ret

# Calculate square of distance between two points.  (Since will only use this
# function to find a minimum distance, we don't need to waste time calculating
# the square root.)


def distanceSquared(a, b):
    return (a.x() - b.x())*(a.x() - b.x()) + (a.y() - b.y())*(a.y() - b.y())
