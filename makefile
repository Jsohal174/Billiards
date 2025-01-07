CC := clang
CFLAGS := -Wall -pedantic -std=c99 -fPIC
PYTHON_INCLUDE := /Library/Frameworks/Python.framework/Versions/3.11/include/python3.11
LIBS := -lm
PYTHON_LIB := /Library/Frameworks/Python.framework/Versions/3.11/lib
SWIG := swig


all: _phylib.so

phylib.o: phylib.c
	$(CC) $(CFLAGS) -c phylib.c -o phylib.o

libphylib.so: phylib.o
	$(CC) -shared -o libphylib.so phylib.o $(LIBS)

phylib_wrap.c phylib.py: phylib.i
	$(SWIG) -python phylib.i

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -I$(PYTHON_INCLUDE) -c phylib_wrap.c -o phylib_wrap.o

_phylib.so: phylib_wrap.o libphylib.so
	$(CC) $(CFLAGS) -shared phylib_wrap.o -L. -L$(PYTHON_LIB) -lpython3.11 -lphylib -o _phylib.so

clean:
	rm -f *.o *.so phylib_wrap.c phylib.py