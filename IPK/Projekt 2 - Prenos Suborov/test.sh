#!/bin/sh

#Test script pre proj 2 IPK client-server prenos suborov.

rm *.o

echo "--- Starting Compilation... ---"
make all

echo "-------------------------------"
echo "--- Moving Server To Folder ---"
mv server server_files

echo "-------------------------------"
echo "--- Moving Client To Folder ---"
mv client client_files

echo "-------------------------------"
echo "---  Going To Start Server  ---"
echo "---      With Port 3456     ---"
cd server_files
./server -p 3456 &
echo "-------------------------------"
echo "--Client Sending  picture.jpg--"
cd ../
cd client_files
./client -h localhost -p 3456 -u picture.jpg
echo "-------------------------------"
echo "--- Client Sending text.txt ---"
./client -h localhost -p 3456 -u text.txt
echo "-------------------------------"
echo "-Client Download  picture2.jpg-"
./client -h localhost -p 3456 -d picture2.jpg
echo "-------------------------------"
echo "-- Client Download text2.txt --"
./client -h localhost -p 3456 -d text2.txt
echo "-------------------------------"
echo "--Client Download  Wrong File--"
./client -h localhost -p 3456 -d music.mp3
echo "-------------------------------"
echo "-- Client Sending Wrong File --"
./client -h localhost -p 3456 -u neexistuje.pdf
echo "-------------------------------"
echo "-Client Connecting  Wrong Port-"
./client -h localhost -p 2345
echo "-------------------------------"
echo "-Client Connecting Wrong Host -"
./client -h eva.fit.vutbr.cz -p 3456 -u picture.jpg

echo "--- Testing Done ---"
# ps | grep 'server' |awk '{print $1}'













