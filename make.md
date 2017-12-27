g++ -c -fPIC python_wrapper.cpp -o librhd2k.o
g++ -shared -o librhd2k.so librhd2k.o rhd2000evalboard.cpp okFrontPanelDLL.cpp rhd2000datablock.cpp
