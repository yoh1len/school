


all: build

build:
	cd src/ && /usr/bin/qmake-qt5 blockeditor.pro && make -f qtMakefile
	
doxygen:
	cd src && doxygen

pack:
	zip -r ./xestva00-xvalka03.zip Makefile src doc README.txt examples

clean:
	cd src && rm *.o && rm qtMakefile && rm moc_mainwindow.cpp && rm blockeditor && rm ui_mainwindow.h
	cd doc && rm -f *

run:
	./src/blockeditor
	
