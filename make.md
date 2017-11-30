g++ -c -fPIC python_wrapper.c -o librhd2k.o
g++ -shared -o librhd2k.so librhd2k.o *.cpp
