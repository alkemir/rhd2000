from datetime import datetime, strftime
import rhd2k

print ("creating board")
board = rhd2k.evalboard.EvalBoard()

print ("opening board")
board.open()

print ("uploading main.bit")
board.uploadFpgaBitfile(b'main.bit')

print ("initializing")
board.initialize()

print ("setting data source")
board.setDataSource(0, rhd2k.constants.PortA1)

print ("setting sample rate")
board.setSampleRate(rhd2k.constants.SampleRate20000Hz)

print ("setting MISO sampling delay to 3-feet cable")
board.setCableLengthFeet(rhd2k.constants.PortA, 3.0)

print ("turn one LED on")
board.setLedDisplay([1, 0, 0, 0, 0, 0, 0, 0])

print ("setup register to optimize MUX-related settings")
chipRegisters = rhd2k.registers.Registers(board.getSampleRate())

print ("creating command list")
commandList = rhd2k.vector.Vector()

print ("creating sequence for impedance testing")
commandSequenceLength = chipRegisters.createCommandListZcheckDac(commandList, 1000.0, 128.0)
print commandSequenceLength

print ("uploading commands")
board.uploadCommandList(commandList, rhd2k.constants.AuxCmd1, 0)
board.selectAuxCommandLength(rhd2k.constants.AuxCmd1, 0, commandSequenceLength - 1)
board.selectAuxCommandBank(rhd2k.constants.PortA, rhd2k.constants.AuxCmd1, 0)

print ("printing commands")
board.printCommandList(commandList)

print ("creating sequence for temp sensor and aux ADC")
commandSequenceLength = chipRegisters.createCommandListTempSensor(commandList)

print ("uploading commands")
board.uploadCommandList(commandList, rhd2k.constants.AuxCmd2, 0)
board.selectAuxCommandLength(rhd2k.constants.AuxCmd2, 0, commandSequenceLength - 1)
board.selectAuxCommandBank(rhd2k.constants.PortA, rhd2k.constants.AuxCmd2, 0)

print ("printing commands")
board.printCommandList(commandList)

print ("setting amplifier bw paramenters")
dspCutoffFreq = chipRegisters.setDspCutoffFreq(10.0)
print ("Actual DSP cutoff frequency: ", dspCutoffFreq, " Hz")

print ("now really setting amplifier bw paramenters")
chipRegisters.setLowerBandwidth(1.0)
chipRegisters.setUpperBandwidth(7500.0)

print ("creating sequences for register rw and ADC calibration")
commandSequenceLength = chipRegisters.createCommandListRegisterConfig(commandList, False)

print ("uploading version without ADC calibration")
board.uploadCommandList(commandList, rhd2k.constants.AuxCmd3, 0)

print ("creating sequences for register rw and ADC calibration")
chipRegisters.createCommandListRegisterConfig(commandList, True)

print ("uploading version with ADC calibration")
board.uploadCommandList(commandList, rhd2k.constants.AuxCmd3, 1)
board.selectAuxCommandLength(rhd2k.constants.AuxCmd3, 0, commandSequenceLength - 1)
board.selectAuxCommandBank(rhd2k.constants.PortA, rhd2k.constants.AuxCmd3, 1)

print ("printing commands")
board.printCommandList(commandList)

print ("configuring to run SPI for 60 samples")
board.setMaxTimeStep(60)
board.setContinuousRunMode(False)

print ("number of 16-bit words in FIFO: ")
print (board.numWordsInFifo())

print ("starting SPI interface")
board.run()

print ("waiting for 60 samples")
while board.isRunning():
	pass

print ("number of 16-bit words in FIFO: ")
print (board.numWordsInFifo())

print ("creating data block")
dataBlock = rhd2k.datablocks.DataBlock(board.getNumEnabledDataStreams())

print ("reading data block")
board.readDataBlock(dataBlock)

print ("printing data")
dataBlock.print(0)

print ("number of 16-bit words in FIFO: ")
print (board.numWordsInFifo())

print ("executing command without ADC calibration")
board.selectAuxCommandBank(rhd2k.constants.PortA, rhd2k.constants.AuxCmd3, 0)

print ("getting current date time")
now = strftime("%Y-%m-%d %H:%M:%S", datetime.now())

print ("setting filename")
filename = "./test_" + now + ".dat"
print(filename)

"""
    // Let's save one second of data to a binary file on disk.
    ofstream saveOut
    saveOut.open(fileName, ios::binary | ios::out)

    queue<Rhd2000DataBlock> dataQueue

    // Run for one second.
    board.setMaxTimeStep(20000)
    cout << "Reading one second of RHD2000 data..." << endl
    board.run()

    bool usbDataRead
    do {
        usbDataRead = board.readDataBlocks(1, dataQueue)
        if (dataQueue.size() >= 50) {
            board.queueToFile(dataQueue, saveOut)
        }
    } while (usbDataRead || board.isRunning())

    board.queueToFile(dataQueue, saveOut)

    board.flush()

    saveOut.close()

    // Optionally, set board to run continuously so we can observe SPI waveforms.
    // board.setContinuousRunMode(true)
    // board.run()

"""
print ("done!")

print ("turning LED off")
board.setLedDisplay([1, 0, 0, 0, 0, 0, 0, 0])
