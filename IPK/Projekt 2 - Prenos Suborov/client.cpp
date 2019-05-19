#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <string>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <signal.h>
#include <ctype.h>          
#include <arpa/inet.h>
#include <netdb.h>
#include <locale>
#define BUF_SIZE 1024 

using namespace std;

static string server_host_name;
char* file_name;
int port_no;
int send_st; //send status
int receive_st; 
char sender[1024];
char receiver[1024];
int event = -1; // 0 for upload, 1 for download

int arguments(int argc, char *argv[])
{
	if(argc<5)
	{
		exit(EXIT_FAILURE);
	}
	else
	{
		if((strcmp(argv[1], "-h")) == 0)
		{

			server_host_name = argv[2];
//			printf("Host: '%s'\n",server_host_name.c_str());
		}
		
		if((strcmp(argv[3], "-p")) == 0)
		{
			int tempTest = atoi(argv[4]);
  //              	printf("%d \n",tempTest);
                        if ((isalpha(tempTest)) == 0)
                        {
                        	port_no = tempTest;
    //                    	printf("Assigned port: %d \n", port_no);
                        }

		}
	}
	
	if (argc == 7)
	{
		if((strcmp(argv[5], "-u")) == 0)
		{
			event = 0; //upload flag set
		}
		else if((strcmp(argv[5], "-d")) == 0)
		{
			event = 1; //download flag set
		}
		else 
		{
			exit(EXIT_FAILURE);
		}
		
		file_name = argv[6];
	}
return 0;	
}

int main(int argc, char *argv[])
{
	// Arguments check
	arguments(argc,argv);	
	// Variables
	int socket_fd; 
	char receiver[1024];
	struct sockaddr_in server_address;
	struct hostent *server_IP;
	if ((server_IP = gethostbyname(server_host_name.c_str())) == NULL)
	{
		fprintf(stderr,"Error: Host not found. \n");
		exit(EXIT_FAILURE);
	}
	

	// Socket descriptor
	if ((socket_fd = socket(AF_INET, SOCK_STREAM, 0)) <= 0)
	{
		fprintf(stderr, "Error: No Socket Descriptor obtained. \n");
		exit(EXIT_FAILURE);
	}

	// Fill address struct
	server_address.sin_family = AF_INET; 
	server_address.sin_port = htons(port_no); 
	memcpy(&server_address.sin_addr, server_IP->h_addr, server_IP->h_length);


	// Connect to server
	int temp = connect(socket_fd, (struct sockaddr *)&server_address, sizeof(server_address));
	//printf("%d \n", temp);
	if (temp != 0)
	{
		fprintf(stderr, "Error: Connection to host failed! \n");
		exit(EXIT_FAILURE);
	}
	else
	{
	//	printf("[Client] Connected to server! \n");
	}

	//printf("Event: %d \n", event);		
		
		
	//Upload flag = 0
	//Check If Client wants to Upload or Download	
	if (event == 0)
	{
	        FILE *file_send = fopen(file_name, "r");
                if(file_send == NULL)
                {
                        fprintf(stderr, "Error: File  not found. \n");
                        exit(EXIT_FAILURE);
                }
		


		sprintf(sender, "Upload %s", file_name);
	//	printf("Sender: %s \n", sender);
	
		if((send_st = send(socket_fd,sender,strlen(sender),0)) <= 0)
		{
			fprintf(stderr, "Error: Sending Upload status has failed. \n");
			exit(EXIT_FAILURE);
		}
		
		bzero(receiver,1024);		
		if ((receive_st = recv(socket_fd, receiver, 1024, 0)) <= 0)
		{
			fprintf(stderr,"Error: Answer for upload status has not been received. \n");
			exit(EXIT_FAILURE);
		}
		else
		send(socket_fd,"OK",2,0);
			if((strncmp(receiver,"OK",2)) != 0)
			{
				fprintf(stderr,"Error: Server has refused the file upload. \n");
				exit(EXIT_FAILURE);
			}
		
		
		
		
		
		
		bzero(sender, 1024); 
	//	printf("[Client] Sending file to the Server. \n");
	//	FILE *file_send = fopen(file_name, "r");
	//	if(file_send == NULL)
	//	{
	//		fprintf(stderr, "Error: File  not found. \n");
	//		exit(EXIT_FAILURE);
	//	}

		//Send File
		int file_send_size; 
		while((file_send_size = fread(sender, sizeof(char), 1024, file_send)) > 0)
		{
		    if(send(socket_fd, sender, file_send_size, 0) < 0)
		    {
		        fprintf(stderr, "ERROR: Failed to send file. \n");
				exit(EXIT_FAILURE);
		    }
		    bzero(sender, 1024);
		}
		
	//	printf("[Client] File was sent! \n");
		close(socket_fd);
	//	printf("[Client] Connection closed. \n");
		exit(EXIT_SUCCESS);
	}
	else if (event == 1) //download flag = 1
	{
		sprintf(sender, "Download %s", file_name);
		
	//	printf("Download: %s \n", sender);
	
		if((send_st = send(socket_fd,sender,strlen(sender),0)) < 0)
		{
			fprintf(stderr,"Error: Sending Download status has failed. \n");
			exit(EXIT_FAILURE);
		}
	//	printf("Po 1. send\n");
		bzero(receiver,1024);	
		if ((receive_st = recv(socket_fd, receiver, 2, 0)) < 0)
		{
			fprintf(stderr,"Error: Answer for download status has not been received. \n");
			exit(EXIT_FAILURE);
		}
		send(socket_fd,"OK",2,0);
		//printf("Po 1. recv \n");
		//int test2 = strcmp(receiver,"OK");
		//printf("Compare result: %d\n",test2);
			if((strncmp(receiver,"OK",2)) != 0)
			{
				
				fprintf(stderr,"Error: Server has refused the file download. \n");
				exit(EXIT_FAILURE);
			}
			
		
		//Receive File

//		printf("[Client] Receiveing file from Server. \n");
		FILE *file_receive = fopen(file_name, "w+");
		if(file_receive == NULL)
		{
			fprintf(stderr,"Error: File cant be opened. \n");
			exit(EXIT_FAILURE);
		}
		else
			{
				bzero(receiver, 1024); 
				int file_rec_size = 0;
				int was_while = 0;
				
				
				while((file_rec_size = recv(socket_fd, receiver, 1024, 0)) > 0)
				{		 
					
					was_while = 1;	
						if (file_rec_size == 0) 
						{
							exit(EXIT_FAILURE);
						}
						
						int write_size = fwrite(receiver, sizeof(char), file_rec_size, file_receive);
						if(write_size < file_rec_size)
						{
							fprintf(stderr,"Error: File write failed. \n");
							exit(EXIT_FAILURE);
						}
						bzero(receiver, 1024);			
					}
				//If Nothing was received remove created file
				if(file_rec_size == 0 && was_while == 0)
				{
				remove(file_name);
			//	fprintf(stderr,"Error: File not found on server. \n");
				exit(EXIT_FAILURE);
				}
					
	//			printf("[Client] File has been received! \n");
				fclose(file_receive); 
			}
		
		close(socket_fd);
	//	printf("[Client] Connection closed. \n");
		
	}
	else
	{
		
	//	printf("[Client] Nothing to do. Connection closed. \n");
		
	}	
	close(socket_fd);
	exit(EXIT_SUCCESS);
}
