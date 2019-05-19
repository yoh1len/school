CC=g++
PRE=-std=c++98 -pedantic -Wextra -Wall

all: client server
client.o: client.cpp
	$(CC) $(PRE) -c client.cpp -o client.o
server.o: server.cpp
	$(CC) $(PRE) -c server.cpp -o server.o
client: client.o
	$(CC) $(PRE) client.o -o client
server: server.o
	$(CC) $(PRE) server.o -o server
