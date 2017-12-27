import ../rdh2k

print ("creating board")
b = rdh2k.EvalBoard()

print ("opening board")
b.open()

print ("uploading main.bit")
b.uploadFpgaBitfile(b'main.bit')

print ("initializing")
b.initialize()

print ("setting data source")
b.setDataSource(0, PortA1)

print ("setting sample rate")
b.setSampleRate(SampleRate20000Hz)

print ("setting MISO sampling delay to 3-feet cable")
b.setCableLengthFeet(PortA, 3.0)

print ("turn one LED on")
b.setLedDisplay([1, 0, 0, 0, 0, 0, 0, 0])

print ("setup register to optimize MUX-related settings")
#    Rhd2000Registers *chipRegisters
#    chipRegisters = new Rhd2000Registers(b.getSampleRate())

print ("creating command list")
#    int commandSequenceLength
#    vector<int> commandList

"""
    // First, let's create a command list for the AuxCmd1 slot.  This command
    // sequence will create a 1 kHz, full-scale sine wave for impedance testing.
    commandSequenceLength = chipRegisters->createCommandListZcheckDac(commandList, 1000.0, 128.0) // 1000.0, 128.0
    b.uploadCommandList(commandList, Rhd2000EvalBoard::AuxCmd1, 0)
    b.selectAuxCommandLength(Rhd2000EvalBoard::AuxCmd1, 0, commandSequenceLength - 1)
    b.selectAuxCommandBank(Rhd2000EvalBoard::PortA, Rhd2000EvalBoard::AuxCmd1, 0)
    // b.printCommandList(commandList) // optionally, print command list

    // Next, we'll create a command list for the AuxCmd2 slot.  This command sequence
    // will sample the temperature sensor and other auxiliary ADC inputs.
    commandSequenceLength = chipRegisters->createCommandListTempSensor(commandList)
    b.uploadCommandList(commandList, Rhd2000EvalBoard::AuxCmd2, 0)
    b.selectAuxCommandLength(Rhd2000EvalBoard::AuxCmd2, 0, commandSequenceLength - 1)
    b.selectAuxCommandBank(Rhd2000EvalBoard::PortA, Rhd2000EvalBoard::AuxCmd2, 0)
    // b.printCommandList(commandList) // optionally, print command list

    // For the AuxCmd3 slot, we will create two command sequences.  Both sequences
    // will configure and read back the RHD2000 chip registers, but one sequence will
    // also run ADC calibration.

    // Before generating register configuration command sequences, set amplifier
    // bandwidth paramters.

    double dspCutoffFreq
    dspCutoffFreq = chipRegisters->setDspCutoffFreq(10.0)
    cout << "Actual DSP cutoff frequency: " << dspCutoffFreq << " Hz" << endl

    chipRegisters->setLowerBandwidth(1.0)
    chipRegisters->setUpperBandwidth(7500.0)

    commandSequenceLength = chipRegisters->createCommandListRegisterConfig(commandList, false)
    // Upload version with no ADC calibration to AuxCmd3 RAM Bank 0.
    b.uploadCommandList(commandList, Rhd2000EvalBoard::AuxCmd3, 0)

    chipRegisters->createCommandListRegisterConfig(commandList, true)
    // Upload version with ADC calibration to AuxCmd3 RAM Bank 1.
    b.uploadCommandList(commandList, Rhd2000EvalBoard::AuxCmd3, 1)

    b.selectAuxCommandLength(Rhd2000EvalBoard::AuxCmd3, 0, commandSequenceLength - 1)
    // Select RAM Bank 1 for AuxCmd3 initially, so the ADC is calibrated.
    b.selectAuxCommandBank(Rhd2000EvalBoard::PortA, Rhd2000EvalBoard::AuxCmd3, 1)
    // b.printCommandList(commandList) // optionally, print command list

"""

print ("configuring to run SPI for 60 samples")
b.setMaxTimeStep(60)
b.setContinuousRunMode(False)

print ("number of 16-bit words in FIFO: ")
print (b.numWordsInFifo())

print ("starting SPI interface")
b.run()

print ("waiting for 60 samples")
while b.isRunning():
	pass

print ("number of 16-bit words in FIFO: ")
print (b.numWordsInFifo())

"""
    // Read the resulting single data block from the USB interface.
    Rhd2000DataBlock *dataBlock = new Rhd2000DataBlock(b.getNumEnabledDataStreams())
    b.readDataBlock(dataBlock)

    // Display register contents from data stream 0.
    dataBlock->print(0)

    cout << "Number of 16-bit words in FIFO: " << b.numWordsInFifo() << endl

    // Now that ADC calibration has been performed, we switch to the command sequence
    // that does not execute ADC calibration.
    b.selectAuxCommandBank(Rhd2000EvalBoard::PortA, Rhd2000EvalBoard::AuxCmd3, 0)


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
    b.setMaxTimeStep(20000)
    cout << "Reading one second of RHD2000 data..." << endl
    b.run()

    bool usbDataRead
    do {
        usbDataRead = b.readDataBlocks(1, dataQueue)
        if (dataQueue.size() >= 50) {
            b.queueToFile(dataQueue, saveOut)
        }
    } while (usbDataRead || b.isRunning())

    b.queueToFile(dataQueue, saveOut)

    b.flush()

    saveOut.close()

    cout << "Done!" << endl << endl

    // Optionally, set board to run continuously so we can observe SPI waveforms.
    // b.setContinuousRunMode(true)
    // b.run()

    // Turn off LED.
    ledArray[0] = 0
    b.setLedDisplay(ledArray)

    // return a.exec()  // used for Qt applications
}

"""
