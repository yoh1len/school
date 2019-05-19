CC = g++
CFLAGS = -std=c++11 -pedantic -Wextra -Wall
CFLAGS_EXTRA = -pthread
BIN_FILE = popser
OBJ_FILES = popser.o md5.o
SRC_FILES = popser.cpp md5.cpp

all: $(BIN_FILE)
$(BIN_FILE): $(OBJ_FILES) popser.cpp
	$(CC) $(CFLAGS) $(OBJ_FILES) -o $(BIN_FILE) $(CFLAGS_EXTRA)
$(OBJ_FILES):
	$(CC) $(CFLAGS) -c $(SRC_FILES)

clean:
	rm $(OBJ_FILES) $(BIN_FILE)

.PHONY: clean
