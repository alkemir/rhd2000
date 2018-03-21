import os
import numpy as np
from threading import Thread
import evalboard
import constants

def initialize():
    board = evalboard.EvalBoard()
    board.open()
    board.uploadFpgaBitfile(b'main.bit')
    board.initialize()

    board.setDataSource(0, constants.PortA1)
    board.setDataSource(1, constants.PortB1)
    for stream in range(2, 8):
    	board.enableDataStream(stream, False)

    board.setSampleRate(constants.SampleRate20000Hz)
    board.setCableLengthFeet(constants.PortA, 3.0)
    board.setCableLengthFeet(constants.PortB, 3.0)
    board.setContinuousRunMode(False)

    return board

def listen(board, stream, channel):
    board.enableDac(0, True)
    board.selectDacDataStream(0, stream)
    board.selectDacDataChannel(0, channel)

def readData(board, steps):
    queue = rhd2k.dataqueue.DataQueue()

    board.setMaxTimeStep(steps)
    board.run()

    def readBlocks():
        usbDataRead = True
        while (usbDataRead or board.isRunning()):
            usbDataRead = board.readDataBlocks(1, queue)

        board.flush()

    p1 = Thread(target=readBlocks)
    p1.start()
    return queue

def queueToArrays(queue):
    adc = np.zeros(len(queue)*constants.samples_per_data_block * 333)
    channels = []
    for chan in range(32+16):
        channels.append(np.zeros(len(queue)*constants.samples_per_data_block * 333))

    b = 0
    while len(queue) != 0:
        block = datablocks.DataBlock(0, ptr=queue.front())
        blockADCData = block.readADC(7)
        blockStreamA = []
        blockStreamB = []
        for chan in xrange(8, 24):
            blockStreamA.append(block.readAmplifier(0, chan))
        for chan in xrange(0, 32):
            blockStreamB.append(block.readAmplifier(1, chan))

        for sample in xrange(rhd2k.constants.samples_per_data_block):
            idx = b + sample
            adc[idx] = blockADCData[sample]
            for chan in xrange(8, 24):
                channels[chan][idx] = blockStreamA[chan][sample]
            for chan in xrange(0, 32):
                channels[chan+16][idx] = blockStreamB[chan][sample]

        b += rhd2k.constants.samples_per_data_block
        queue.pop()

    return adc, channels

def saveRun(run, description, adc, channels):
    basePath = '/Users/br/data/29Enero2018/' + str(run) + '/'

    os.mkdir(basePath)
    np.save(basePath+'adc', adc)

    fd = open(basePath+'desc.txt', 'w')
    fd.write(description)
    fd.close()

    for chan in xrange(len(channels)):
        np.save(basePath+'chan_'+str(chan), channels[chan])

def getRun():
    fd = open('/Users/br/data/29Enero2018/currentRun', 'r')
    run = int(fd.read())
    fd.close()
    return run

def setRun(run):
    fd = open('/Users/br/data/29Enero2018/currentRun', 'w')
    fd.write(str(run))
    fd.close()
