# rhd2000
Python bindings for the rhd2000 evaluation board

This repository provides bindings to the C++ Rhythm API through ctypes (and hand-written C wrapper code).
Also, the GUI has been reimplemented in Python (PyQt5) following the original code closely, so that updating
the code or extending the GUI are simple tasks.


# Dependencies
To use the ctypes wrapper you don't need any special software, but if you want to use the GUI you need to install
PyQt5. If you want to be build everything from source, a C and C++ compiling environment is needed.



# Deploying
Depending on the operating system the steps and software requirements vary:

virtualenv -p python3 pyntan
cd pyntan
source bin/activate
pip install pyqt5

Now copy the contents of the pyntan folder to the virtualenv you just created.
Also, some binaries are necesary. You can obtain them from pre-compiled distributions by Intan
or compile them yourself.

Particularly, to compile the shared library in Mac invoke:

g++ -c -fPIC python_wrapper.cpp -o librhd2k.o
g++ -shared -o librhd2k.so librhd2k.o rhd2000evalboard.cpp okFrontPanelDLL.cpp rhd2000datablock.cpp rhd2000registers.cpp

## Mac
(Instructions on how to build the dynamic lib and where to position files)

To use the python wrapper check out sample.py, it follows closely the example provided by Intan.
To run the GUI just execute main.py

## Windows
(Still under work)

## Linux
(Help wanted, I have never tried to get this running on Linux)

# Contributing
Any help is welcome, but please keep in mind that the code is purposely written so that is follows the original
code, thus any efforst into making it more Pythonic would be wasted. If you find a bug please create and issue
and we can solve it together.
