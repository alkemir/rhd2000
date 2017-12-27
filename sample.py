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

"""
    // Read the resulting single data block from the USB interface.
    Rhd2000DataBlock *dataBlock = new Rhd2000DataBlock(board.getNumEnabledDataStreams())
    board.readDataBlock(dataBlock)

    // Display register contents from data stream 0.
    dataBlock->print(0)

    cout << "Number of 16-bit words in FIFO: " << board.numWordsInFifo() << endl

    // Now that ADC calibration has been performed, we switch to the command sequence
    // that does not execute ADC calibration.
    board.selectAuxCommandBank(rhd2k.constants.PortA, rhd2k.constants.AuxCmd3, 0)


    // Grab current time and date for inclusion in filename
    char timeDateBuf[80]
    time_t now = time(0)
    struct tm tstruct
    tstruct = *localtime(&now)

    // Construct filename
    string fileName
    fileName = "C:\\"  // add your desired path here
    fileName += "test_"
    strftime(timeDateBuf, sizeof(timeDateBuf), "%y%m%d", &tstruct)
    fileName += timeDateBuf
    fileName += "_"
    strftime(timeDateBuf, sizeof(timeDateBuf), "%H%M%S", &tstruct)
    fileName += timeDateBuf
    fileName += ".dat"

    cout << endl << "Save filename:" << endl << "  " << fileName << endl << endl

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

    cout << "Done!" << endl << endl

    // Optionally, set board to run continuously so we can observe SPI waveforms.
    // board.setContinuousRunMode(true)
    // board.run()

    // Turn off LED.
    ledArray[0] = 0
    board.setLedDisplay(ledArray)

    // return a.exec()  // used for Qt applications
}

"""
