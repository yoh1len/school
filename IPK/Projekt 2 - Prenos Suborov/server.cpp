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
using namespace std;
int port_no;
char sender[1024];
char receiver[1024];

void communication(int n_sock);
void SigCatcher(int n)
{
n=n;
wait3(NULL,WNOHANG,NULL);
}
int arguments(int argc, char *argv[])
{
	if(argc<3)
	{
		fprintf(stderr, "Error: Wrong arguments. Call: server -p <port> \n");
		exit(EXIT_FAILURE);
	}
	else
	{	

                //int tempTest = atoi(argv[2]);
                //printf("%d \n",tempTest);
	
		if((strcmp(argv[1], "-p")) == 0)
		{
		
		int tempTest = atoi(argv[2]);
		//printf("%d \n",tempTest);
			if ((isalpha(tempTest)) == 0)
			{
			port_no = tempTest;
		//	printf("Assigned port: %d \n", port_no);
			}
		}
	}
return 0;
}



int main (int argc, char *argv[])
{
	// Zombie Killer
	signal(SIGCHLD,SigCatcher); 
	
	// Check arguments
	arguments(argc,argv);

	//Variables
	int socket_fd; 
	int new_socket_fd; 
	socklen_t socket_size; 
	struct sockaddr_in client_address; 
	struct sockaddr_in server_address; 
	string received_data = "";

	// Socket descriptor
	if((socket_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0 )
	{
		fprintf(stderr, "Error: No Socket Descriptor obtained. \n");
		exit(EXIT_FAILURE);
	}
	else 
	{
	//	printf("[Server] Socket Descriptor obtained. \n");
	}
	
	// Fill address struct 
	client_address.sin_family = AF_INET; 
	client_address.sin_port = htons(port_no);
	client_address.sin_addr.s_addr = INADDR_ANY;
	

	// Port Binding
	if( bind(socket_fd, (struct sockaddr*)&client_address, sizeof(struct sockaddr)) == -1 )
	{
		fprintf(stderr, "Error: Port binding failed. \n");
		exit(EXIT_FAILURE);
	}
	else 
	{
		int tempport=atoi(argv[2]);
		if(tempport == port_no)
		{
	//		printf("[Server] Port binding done. Binded port: %d \n",port_no);
		}
		else
		{
			fprintf(stderr,"Error: Magical, mystical error has occured while port binding. \n");
		exit(EXIT_FAILURE);
		}
	}
	// Listening
	if(listen(socket_fd,1) < 0)
	{
		fprintf(stderr, "Error: Listening failed.");
		exit(EXIT_FAILURE);
	}
	else
	{
	//	printf ("[Server] Listening the port %d.\n", port_no);
	}
	bool waiting = true;
	while(waiting)
	{
	
		socket_size = sizeof(client_address);

		// Waiting for a new conection 
		if ((new_socket_fd = accept(socket_fd, (struct sockaddr *)&server_address, &socket_size)) == -1) 
		{
		    fprintf(stderr, "Error: No (new) Socket Descriptor obtained. \n");
			exit(EXIT_FAILURE);
		}
		else 
		{
	//		printf("[Server] Connection established with %s . \n", inet_ntoa(server_address.sin_addr));
		}
		
		//Fork
		int pid = fork();
		if(pid<0)
		{
			fprintf(stderr, "Error: Fork failed.");
		}
		if(pid == 0){
		close(socket_fd);
		communication(new_socket_fd);
		exit(EXIT_SUCCESS);
		}
		else
		{ 
		close(new_socket_fd);
		}
	}
	close(socket_fd);
	fprintf(stderr,"Error: You should not be here, fail!");
	return 0;
}	
void communication(int n_sock)
{	
		//printf("Som tu\n");
		string received_data = "";
		int res = 0;
		for (;;)
		{
			if((res = recv(n_sock, receiver, 1024,0)) <= 0)
			{
		//	printf("Test %d \n", res);
			break;
			}
		break;
		}
		//printf("Received data: %s \n", receiver);
		
		received_data.append(receiver);
		//printf("%s \n", received_data.c_str());
		
		//Compare if Download <file> or Upload <file>
		
		if (received_data.compare(0,8,"Download") == 0)
		{
                    
                    	
			int answer;
			sprintf(sender, "OK");
			//printf("Download %s \n",sender);
			if((answer = send(n_sock,sender,2,0)) < 0)
			{
				fprintf(stderr,"Error: Sending Download answer failed \n");
			
				close(n_sock);
	//			printf("[Server] Connection closed. \n");
		
			}			
			recv(n_sock, receiver,2,0); 	
			received_data.erase(0,9);
			
			//printf("Sending Data: %s\n",received_data.c_str());
			
			char* file_name = (char *)(received_data.c_str());
			
		  
 
	//	    printf("[Server] Sending %s to the Client... \n", file_name);
		   // Send File
		    FILE *file_send = fopen(file_name, "r");
		    if(file_send == NULL)
		    {
		       fprintf(stderr, "Error: File not found on server. \n");
			exit(EXIT_FAILURE);
		    }

		    bzero(sender, 1024); 
		    int file_send_size; 
		    while((file_send_size = fread(sender, sizeof(char), 1024, file_send))>0)
		    {
		        if(send(n_sock, sender, file_send_size, 0) < 0)
		        {
		            fprintf(stderr, "Error: Failed to send file. \n");
		            exit(EXIT_FAILURE);
		        }
		        bzero(sender, 1024);
		    }
	//	    printf("[Server] File has been sent! \n");
		 
		    close(n_sock);
	//	    printf("[Server] Connection closed. \n");
		   
			
			
			
		}
		else if (received_data.compare(0,6,"Upload") == 0)
		{
			int answer;
                        sprintf(sender, "OK");
		//	printf("Upload %s \n",sender);
			if((answer = send(n_sock,sender,strlen(sender),0)) < 0)
			{
				fprintf(stderr,"Error: Sending Upload answer failed \n");
				
				close(n_sock);
	//			printf("[Server] Connection closed. \n");
			
			}
			recv(n_sock, receiver,2,0);	
			
			received_data.erase(0,7);
			//printf("Received_data: %s \n",received_data.c_str());
			
			char* file_name = (char *)(received_data.c_str());
			
			//Receive file
	
			FILE *file_receive = fopen(file_name, "w+");
			if(file_receive == NULL)
			{
			fprintf(stderr,"Error: Cant open file. \n");
			}
			else
			{
				bzero(receiver, 1024); 
				int file_rec_size = 0;
				
				
				
				while((file_rec_size = recv(n_sock, receiver, 1024, 0)) > 0)
				{ 
					
										                                 
				//	printf("%s \n", receiver);
				//	printf("Test\n");
				//	printf("File_rec: %d \n",file_rec_size);
						if (file_rec_size == 0) 
						{
				//		printf("Test2");
						exit(EXIT_FAILURE);
						}
						int write_size = fwrite(receiver, sizeof(char), file_rec_size, file_receive);
				//		printf("Write size %d \n",write_size);
				//		printf("File_rec_size %d \n", file_rec_size);		


						if(write_size < file_rec_size)
						{
							fprintf(stderr,"Error: File write failed. \n");
						}
						bzero(receiver, 1024);			
					
					
				}
				
		//		printf("[Server] File has been received! \n");
				fclose(file_receive); 
			}
		
		close(n_sock);
	//	printf("[Server] Connection closed. \n");	
		}
		else
		{
	//	printf("Nothing to do. Connection closed\n");
		close(n_sock);
		}
	}

