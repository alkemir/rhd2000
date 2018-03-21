CXX = i686-w64-mingw32-g++
#CXX = g++
CPPFLAGS=-I./rhythm -mwin32

ifeq ($(OS),Windows_NT)
    CPPFLAGS += -D WIN32
endif

ifeq ($(OS),Windows_NT)
    TARGETNAME=librhd2k.dll
else
	TARGETNAME=librhd2k.so
endif


RDIR = rhythm
ODIR = $(RDIR)/obj

_DEPS = rhd2000evalboard.h rhd2000datablock.h rhd2000registers.h okFrontPanelDLL.h
DEPS = $(patsubst %,$(RDIR)/%,$(_DEPS))
_OBJ = librhd2k.o rhd2000evalboard.o okFrontPanelDLL.o rhd2000datablock.o rhd2000registers.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

$(ODIR)/%.o: $(RDIR)/%.cpp $(DEPS)
	$(CXX) -c -o $@ $< $(CPPFLAGS)

all: directories librhd2k

librhd2k: $(OBJ)
	$(CXX) -shared -static -static-libstdc++ -o lib/$(TARGETNAME) $^ $(CPPFLAGS)

$(ODIR)/librhd2k.o:
	$(CXX) -c -fPIC rhd2k/python_wrapper.cpp -o $@ $(CPPFLAGS)

directories:
	mkdir -p $(ODIR)

.PHONY: clean
clean:
	rm -f $(ODIR)/*.o