#!/usr/bin/python3
# -*- coding: utf-8 -*-

# RHD2000 Evaluation Board constants
MAX_NUM_DATA_STREAMS = 8
SAMPLES_PER_DATA_BLOCK = 60

# Special Unicode characters
QSTRING_MU_SYMBOL = u'\u03BC'
QSTRING_OMEGA_SYMBOL = u'\u03A9'
QSTRING_ANGLE_SYMBOL = u'\u2220'
QSTRING_DEGREE_SYMBOL = u'\u00b0'
QSTRING_PLUSMINUS_SYMBOL = u'\u00b1'

# Saved data file constants
DATA_FILE_MAGIC_NUMBER = 0xc6912702
DATA_FILE_MAIN_VERSION_NUMBER = 1
DATA_FILE_SECONDARY_VERSION_NUMBER = 5

# Saved settings file constants
SETTINGS_FILE_MAGIC_NUMBER = 0x45ab12cd
SETTINGS_FILE_MAIN_VERSION_NUMBER = 1
SETTINGS_FILE_SECONDARY_VERSION_NUMBER = 5

# Trigonometric constants
RADIANS_TO_DEGREES = 57.2957795132
DEGREES_TO_RADIANS = 0.0174532925199

SPIKEPLOT_X_SIZE = 320
SPIKEPLOT_Y_SIZE = 346

# enum SignalType
AmplifierSignal = 0
AuxInputSignal = 1
SupplyVoltageSignal = 2
BoardAdcSignal = 3
BoardDigInSignal = 4
BoardDigOutSignal = 5

# enum SaveFormat
SaveFormatIntan = 0
SaveFormatFilePerSignalType = 1
SaveFormatFilePerChannel = 2

CHIP_ID_RHD2132 = 1
CHIP_ID_RHD2216 = 2
CHIP_ID_RHD2164 = 4
CHIP_ID_RHD2164_B = 1000

REGISTER_59_MISO_A = 53
REGISTER_59_MISO_B = 58
