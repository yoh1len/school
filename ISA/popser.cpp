/* 	Meno: Ivan Eštvan
	Login: xestva00
	Datum: 20.11.2017
	*/


#define __USE_POSIX
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <iostream>
#include <cstring>
#include <dirent.h>
#include <mutex>
#include <vector>
#include "md5.h"
#include <fcntl.h>
#include <signal.h>

using namespace std;

/* Trieda na uchovanie nastavenia argumentov aby som nemusel stale predavat argv, argc */

class argumentFlags{
	public:
		bool help;
		bool auth;
		char *auth_path;
		bool port;
		int port_no;
		bool directory;
		char *dir_path;
		bool clear;
		bool reset;
};

/* Globalne pouzivane premenne */
argumentFlags flagsSet; // flagy
mutex mtx; //stav mutexu
vector<bool> deleted_msg; // vektor obsahujuci info o tom ktora sprava je oznacena na zmazanie
vector<int> size_msg; // vektor obsahujuci info o velkostiach suborov
vector<int> socket_vector; // vektor obsahujuci sockety
int random_difference = 150; //pomocna premenna pre rozlisenie time stampov


/* Funkcia na vypis napovedy */
void write_help(){
	printf("Popser help:\n");
	printf("---------------\n");
	printf("./popser [-h] [-a PATH]* [-c] [-p PORT]* [-d PATH]* [-r] \n");
	printf("-h 		-> writes help \n");
	printf("-a [PATH] 	-> required, provide with path to authentication file\n");
	printf("-p [PORT] 	-> required, provide with port on which the server will run\n");
	printf("-d [PATH] 	-> required, provide with path to Maildir folder\n");
	printf("-c 		-> optional, if set, server accepts non hash password, else only hash password\n");
	printf("-r		-> optional, if set, server resets to it's default and removes all temp files\n");
	printf("------------------------------------------------------------------------------------------\n");
	printf("Authentication file should look like: \n");
	printf("username = [username]\n");
	printf("password = [password]\n");
}


/* Funkcia, ktora sa spusti pri zadani parametru -r */
int reset(){
	FILE *file;
	string path_to_new = "";
	string path_to_cur = "";
	/* Zistime ci vieme otvorit temp subor, ktory ma obsahovat zmeny */
	if ((file = fopen("temp_moves.txt", "r")) == NULL){
		fprintf(stderr, "Error: No temporary file or can not be open.\n");
		return 1;
	}
	/* Ideme znak po znaku a parsujeme si dany subor, ktory obsahuje info v tvare:
		path_to_new:path_to_cur
		
		Kedze tento subor generuje program, predpokladam ze v nom nebude chyba.
		*/
	int c;
	int last_was =  0;
	int switch_string = 0;
	while ((c = getc(file)) != EOF){
		if(switch_string == 0 && c == ':'){
			switch_string = 1;
			last_was = c;
		}
		else if(switch_string == 0 && c != '\r' && c != '\n' ){
			path_to_new = path_to_new + (char) c;
			last_was = c;
		}
		else if(switch_string == 1 && c != '\r' && c != '\n'){
			path_to_cur = path_to_cur + (char) c;
			last_was = c;
		}
		else if (switch_string ==1 && c == '\r'){
			last_was = c;
		}
		else if(switch_string == 1 && c == '\n' && last_was =='\r'){
			/* Mame rozparsovany jeden riadok, vratime subory na miesto kam patria 
				Ak sa jedna o neexistujuci subor tak sa jednoducho ignoruje a pokracujeme dalej */
			rename(path_to_cur.c_str(),path_to_new.c_str());
			path_to_cur.clear();
			path_to_new.clear();
			last_was = 0;
			switch_string = 0;
		}
	}		
	
	fclose(file);
	/* Po skonceni reset stadia zmazeme aj pomocny subor */
	remove("temp_moves.txt");
	return 0;
}
/* Pomocna funkcia na overenie ci mame cislo 
	isdigit nebolo dostatocne potreboval som nieco vlastne */
	
bool is_number(char *test_string){
	int len = strlen(test_string);
	int i = 0;
	while(isdigit(test_string[i])){
		i++;
	}
	if(len == i){
		return true;
	}
	else return false;
}

/* Funkcia, ktora nam kontroluje zadanie argumentov a nastavuje 
	odpovedajuce flagy v triede argumentFlags */
	
argumentFlags arguments(int argc, char *argv[]){
	/* pre istotu inicializujeme hodnoty, ktore tam chceme mat na zaciatku pred
		kontrolou argumentov */ 
		
	argumentFlags flags_reg;
	flags_reg.help = false;
	flags_reg.auth = false;
	flags_reg.auth_path = NULL;
	flags_reg.port = false;
	flags_reg.port_no = 0;
	flags_reg.directory = false;
	flags_reg.dir_path = NULL;
	flags_reg.clear = false;
	flags_reg.reset = false;
	
	if (argc < 2){
		fprintf(stderr, "Error: Not Enough Arguments\n");
		exit(EXIT_FAILURE);
	}
	else if (argc == 2 && strcmp(argv[1], "-h") == 0){
		write_help();
		exit(EXIT_SUCCESS);
	}
	else if (argc == 2 && strcmp(argv[1], "-r") == 0){
		reset();
		exit(EXIT_SUCCESS);
	}
	else if (argc >= 7 && argc < 11){
		for(int i=1; i<argc;i++){
			if(strcmp(argv[i], "-a") == 0 && (strchr(argv[i+1], '-') == NULL || strcspn(argv[i+1], "-") != 0 )){
				flags_reg.auth = true;
				flags_reg.auth_path = argv[i+1];
				i++;
			}
			else if (strcmp(argv[i], "-p") == 0 && is_number(argv[i+1])){
				flags_reg.port = true;
				flags_reg.port_no = atoi(argv[i+1]);
				i++;
			}
			else if (strcmp(argv[i], "-d") == 0 && (strchr(argv[i+1], '-') == NULL || strcspn(argv[i+1], "-") != 0 )){
				flags_reg.directory = true;
				flags_reg.dir_path = argv[i+1];
				i++;
			}
			else if (strcmp(argv[i], "-c") == 0 ){
				flags_reg.clear = true;
			}
			else if (strcmp(argv[i], "-r") == 0 ){
				flags_reg.reset = true;
			}
			else if (strcmp(argv[i], "-h") == 0 ){
				flags_reg.help = true;
			}
			else{
				fprintf(stderr,"Error: Wrong arguments, see -h for help.\n");
				exit(EXIT_FAILURE);
			}
		}
	}
	else{
		fprintf(stderr,"Error: Wrong arguments count, see -h for help.\n");
		exit(EXIT_FAILURE);
	}	
	return flags_reg;
}

/* Funkcia, ktora sa vola pri ukonceni spojenia z transakcnej fazy */
void closeClientSock(int client_socket_fd){
	for(unsigned int i = 0; i<socket_vector.size(); i++){
		if(socket_vector[i] == client_socket_fd){
			socket_vector.erase(socket_vector.begin()+i);
		}
	}
	close(client_socket_fd);
	deleted_msg.clear();
	size_msg.clear();
	mtx.unlock();
	
	pthread_exit(NULL);
	// UNLOCK MUTEX
	
}


/* Pomocna funkcia na odoslanie spravy klientovi */
void sendMessage(int client_socket_fd, const char *text_to_send){
	if((send(client_socket_fd, text_to_send, strlen(text_to_send),0)) < 0){
		fprintf(stderr, "Error: Send failed.");
		closeClientSock(client_socket_fd);
	}
}
/* Funkcia, ktora sa vola pri ukonceni spojenia mimo transakcnej fazy,
napriklad pocas autorizacnej. */
void closeClientSockUnlogged(int client_socket_fd){
	for(unsigned int i = 0; i<socket_vector.size(); i++){
		if(socket_vector[i] == client_socket_fd){
			socket_vector.erase(socket_vector.begin()+i);
		}
	}
	string send_msg= "";
	send_msg = "+OK POP3 server signing off\r\n";
	sendMessage(client_socket_fd, send_msg.c_str());
	close(client_socket_fd);
	pthread_exit(NULL);
}

/* Funkcia ktora overuje spravne zadany username */
int checkUser(char *data){
	
	string data_to_parse = "";
	data_to_parse.append(data);
	
	FILE *fp;
	
	char username[255];
	/* Ak si nevieme otvorit autorizacny subor vratime chybovy stav */
	if ((fp = fopen(flagsSet.auth_path, "r")) == NULL){
		fprintf(stderr, "Error: Auth file does not exist or can not be open.\n");
		return 2;
	}
	
	fgets(username, 255, (FILE*)fp);
	fclose(fp);
	
	string str_username = "";
	
	str_username.append(username);
	
	str_username.erase(0,11);
	str_username.pop_back();
	
	data_to_parse.erase(0,5);
	data_to_parse.pop_back();
	data_to_parse.pop_back();
	
	/* kontrola ci sa username zhoduju */
	if(str_username.compare(data_to_parse) == 0){
		return 0;
	}
	else return 1;
	
}

/* Funkcia ktora overuje spravne zadane heslo pomocou PASS */
int checkPassword(char *data){
	
	
	string data_to_parse = "";
	data_to_parse.append(data);
	
	FILE *fp;
	
	char username[255];
	char password[255];
	/* Ak si nevieme otvorit autorizacny subor vratime chybovy stav */
	if ((fp = fopen(flagsSet.auth_path, "r")) == NULL){
		fprintf(stderr, "Error: Auth file does not exist or can not be open.\n");
		return 2;
	}
	fgets(username, 255, (FILE*)fp);
	
	fgets(password, 255, (FILE*)fp);
	fclose(fp);
	
	string str_password = "";
	
	str_password.append(password);
	
	str_password.erase(0,11);
	str_password.pop_back();
	
	data_to_parse.erase(0,5);
	data_to_parse.pop_back();
	data_to_parse.pop_back();
	
	int compare = str_password.compare(data_to_parse);
	
	/* kontrola ci sa username zhoduju */
	if(compare == 0){
		return 0;
	}
	else return 1;
	
}

/* Funkcia, ktora v pripade uspesnej autorizacie presunie obsah /new do /cur */

int move_new_to_cur(){
	FILE *temp;
	
	temp = fopen("temp_moves.txt","a+");
	string write_to_file = "";
	
	DIR *dir;
	struct dirent *ent;
	/* Nastavenie PATH */
	string directory_path_new = "";
	string directory_path_cur = "";
	directory_path_new.append(flagsSet.dir_path);
	directory_path_new.append("/new/");
	directory_path_cur.append(flagsSet.dir_path);
	directory_path_cur.append("/cur/");
	
	if ((dir = opendir (directory_path_new.c_str())) != NULL) {

		while ((ent = readdir (dir)) != NULL) {
			/* Temp premenne pre PATH k suboru */
			string directory_path_new_temp = "";
			directory_path_new_temp.append(directory_path_new);
			string directory_path_cur_temp = "";
			directory_path_cur_temp.append(directory_path_cur);
			/* Ignorujeme . a .. subory */
			if(strcmp(ent->d_name,".") != 0 && strcmp(ent->d_name,"..") != 0){
				/* Nastavime si cestu az ku suborom */
				directory_path_new_temp.append(ent->d_name);
				directory_path_cur_temp.append(ent->d_name);
				/* Zapiseme si co presuvame do pomocneho suboru */
				write_to_file = directory_path_new_temp+":"+directory_path_cur_temp+"\r\n";
				fprintf(temp, write_to_file.c_str());
				/* Presunieme subor z new do cur */
				rename(directory_path_new_temp.c_str(), directory_path_cur_temp.c_str());
			}
		}
		closedir (dir);
		fclose(temp);
	} 
	else {
		//mozno iny exit
		 exit(EXIT_FAILURE);
	}
	/* Otvorime si zlozku cur a sprave spocitame velkost suborov aj podla chybajucich \r \n */
	if ((dir = opendir (directory_path_cur.c_str())) != NULL) {
		while ((ent = readdir (dir)) != NULL) {
			string directory_path_cur_temp = "";
			directory_path_cur_temp.append(directory_path_cur);
	  
			if(strcmp(ent->d_name,".") != 0 && strcmp(ent->d_name,"..") != 0){
				directory_path_cur_temp.append(ent->d_name);
				FILE *file;
				if((file = fopen(directory_path_cur_temp.c_str(), "r")) != NULL){
					int c;
					int last_was =  0;
					int size = 0;
					while ((c = getc(file)) != EOF){
						size = size +1;
						if(c == '\n' && last_was != '\r'){
							size= size +1;
						}
						last_was = c;
					
					}
					if(c == EOF && last_was !='\n'){
						size = size +2;
					}
				size_msg.push_back(size);
				}
				fclose(file);
			}
		}
		closedir (dir);
	} 
	else {
		// MOZNO INY EXIT
		 exit(EXIT_FAILURE);
	}
	
	
	
	return 0;
}

/* Pomocna funkcia na rychle spocitanie kolko sprav je oznacenych na zmazanie */
int to_delete(){
	int count = 0;
	 for (unsigned i=0; i<deleted_msg.size(); i++){
		 if(deleted_msg[i] == true){
			 count++;
		 }

	}
	return count;
}

/* Spocita nam pocet sprav v zlozke cur */
int count_in_cur(){
	int files_no = size_msg.size();
return files_no;
}

/* Pocita nam velkost suborov v zlozke cur 
		Trigger 0 - pouzity uplne na zaciatku
		Trigger 1 - pouzivany neskor v programe ignorujeme spravy oznacene na zmazanie */

int size_in_cur(int trigger){

	int files_size = 0;

if(trigger == 0){
	
	unsigned int vector_size = size_msg.size();
	
	for(unsigned int i = 0; i<vector_size; i++){
		files_size = files_size+ size_msg[i];
	}
return files_size;
}
else if(trigger == 1){
	
	unsigned int vector_size = size_msg.size();
	
	for(unsigned int i = 0; i<vector_size; i++){
		if(deleted_msg[i] == false){
			files_size = files_size + size_msg[i];
		}
	}

return files_size;	
}
return 0;
}

/* Funkcia ktora sa vola ako odpoved na prikaz LIST 
	number = 0 - volame ked chceme vypis LIST
	number = 1 - volame ked chceme vypis nejakej spravy LIST <X>
	
	V oboch pripadoch ignorujeme spravy oznacene na zmazanie.
	*/

int send_list(int number, int client_socket_fd, char *data){
	string send_msg = "";
	int files_size = 0;
	int files_count = 0;
	unsigned int msg_count = count_in_cur();
	
if(number == 0){
	
	unsigned int vector_size = size_msg.size();
	/* Vypis vsetkych sprav */ 
	for(unsigned int i = 0; i<vector_size; i++){

		if(deleted_msg[i] == false){
			files_count = i +1;
			files_size = size_msg[i];
			send_msg = to_string(files_count) + " " + to_string(files_size)+"\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
		}
	}
	return 0;
}
else if(number == 1){
	/* potrebujeme ziskat informaciu, ktoru spravu chceme vypisat,
		takze parsujeme prijaty prikaz*/ 
	string data_to_parse = "";
	data_to_parse.append(data);
	
	data_to_parse.erase(0,5);
	data_to_parse.pop_back();
	data_to_parse.pop_back();

	
	unsigned int to_info_number = stoi(data_to_parse,nullptr);
	unsigned int vector_size = size_msg.size();
	
	for(unsigned int i = 0; i<vector_size; i++){
		/* Ak sme nasli spravu ktoru klient chce tak mu o nej posleme info, inak posleme chybove hlasenie*/
		if(deleted_msg[i] == false && to_info_number == i+1){
			files_count = i +1;
			files_size = size_msg[i];
			send_msg = "+OK "+to_string(files_count) + " " + to_string(files_size)+"\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			return 0;
		}
		else if((deleted_msg[i] == true && to_info_number == i+1) || to_info_number > msg_count){
			msg_count = msg_count - to_delete();
			send_msg = "-ERR no such message, only "+to_string(msg_count)+ " messages in maildrop\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			return 0;
		}
	}
	return 0;	
	
}
return 0;
}
/* Funkcia ktora sa vola ako odpoved na prikaz UIDL
	number = 0 - volame ked chceme vypis UIDL
	number = 1 - volame ked chceme vypis nejakej spravy UIDL <X>
	
	V oboch pripadoch ignorujeme spravy oznacene na zmazanie.
	*/
int send_uidl(int number, int client_socket_fd, char *data){
	
	string send_msg = "";
	DIR *dir;
	struct dirent *ent;

	int files_count = 0;
	int msg_count = count_in_cur();
	
	string directory_path_cur = "";
	directory_path_cur.append(flagsSet.dir_path);
	directory_path_cur.append("/cur/");
	/* Prechadzame mena suborov v zlozke /cur */
if(number == 0){
	if ((dir = opendir (directory_path_cur.c_str())) != NULL) {
		while ((ent = readdir (dir)) != NULL) {
	  
			if(strcmp(ent->d_name,".") != 0 && strcmp(ent->d_name,"..") != 0){
				
				files_count = files_count + 1;
			
				if(deleted_msg[files_count-1] == false){
					send_msg = "+OK "+to_string(files_count) + " " + ent->d_name +"\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());
				}
			}
		}
		closedir (dir);
	} else {
		exit(EXIT_FAILURE);
	}
	return 0;
}
else if(number == 1){
	/* Potrebujeme ziskat cislo spravy , ktoru chceme vypisat 
	takze parsujeme */
	string data_to_parse = "";
	data_to_parse.append(data);
	
	data_to_parse.erase(0,5);
	data_to_parse.pop_back();
	data_to_parse.pop_back();
	int to_info_number = stoi(data_to_parse,nullptr);
	
	if ((dir = opendir (directory_path_cur.c_str())) != NULL) {
		while ((ent = readdir (dir)) != NULL) {
	  
			if(strcmp(ent->d_name,".") != 0 && strcmp(ent->d_name,"..") != 0){
		
				files_count = files_count + 1;
				/* Vypis info spravy ak sa nasla, inak posielame chybovu spravu */
				if(deleted_msg[files_count-1] == false && to_info_number == files_count){
					send_msg = "+OK "+to_string(files_count) + " " + ent->d_name +"\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());
					/* Potrebujeme zatvorit zlozku lebo odchadzame */
					closedir (dir);
					return 0;
				}
				else if((deleted_msg[files_count-1] == true && to_info_number == files_count) || to_info_number > msg_count){
					msg_count = msg_count - to_delete();
					send_msg = "-ERR no such message, only "+to_string(msg_count)+ " messages in maildrop\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());
					closedir (dir);
					return 0;
				}
			}
		}
		closedir (dir);
	} else {
		exit(EXIT_FAILURE);
	}
	return 0;	
	
}
	
return 0;
}

/* Funkcia na odoslanie zpravy klientovi */
int send_retr(char *data, int client_socket_fd){
	
	string send_msg = "";
	DIR *dir;
	struct dirent *ent;
	
	int files_size = 0;
	int files_count = 0;
	int msg_count = count_in_cur();
	

	/* Nastavime si cestu do zlozky cur */
	string directory_path_cur = "";
	directory_path_cur.append(flagsSet.dir_path);
	directory_path_cur.append("/cur/");
	string data_to_parse = "";
	data_to_parse.append(data);
	
	data_to_parse.erase(0,5);
	data_to_parse.pop_back();
	data_to_parse.pop_back();

	
	int to_info_number = stoi(data_to_parse,nullptr);
	/* Prechadzame zlozku kym nenajdeme spravu ktoru klient chce obdrzat */
	if ((dir = opendir (directory_path_cur.c_str())) != NULL) {
		while ((ent = readdir (dir)) != NULL) {
			string directory_path_cur_temp = "";
			directory_path_cur_temp.append(directory_path_cur);
	  
			if(strcmp(ent->d_name,".") != 0 && strcmp(ent->d_name,"..") != 0){
				directory_path_cur_temp.append(ent->d_name);
		

				files_count = files_count + 1;
				files_size = size_msg[files_count-1];

				/* Najdeme spravu ktora nie je zmazana a chce ju klient */
				if(deleted_msg[files_count-1] == false && to_info_number == files_count){
					FILE *fp;

					char buffer[1024];
					string to_send = "";
					memset(buffer, 0, sizeof(buffer));
					/* Pred odoslanim do nej musime doplnit znaky CRLF aby sme dodrzali standard */
					if ((fp = fopen(directory_path_cur_temp.c_str(), "r")) != NULL){
						int last_was;
						int c;
						
						while ((c = getc(fp)) != EOF){
							if(c == '\n' && last_was == '\r'){
								to_send = to_send + (char)c;
							}
							else if(c == '\n' && last_was != '\r'){
								to_send = to_send + '\r' + (char)c;			
							}
							else if (c == '.' && last_was == '\n'){
								to_send = to_send + '.' + (char)c;
							}
							else {
								to_send = to_send + (char)c;
							}
							
							
							last_was = c;
					
						}
						if(c == EOF && last_was != '\n'){
							to_send = to_send +"\r\n";
						}
					}
					
					/*Odosielame spravy*/
					send_msg = "+OK "+to_string(files_count) + " " + to_string(files_size)+"\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());

					send_msg = to_send;
					sendMessage(client_socket_fd, send_msg.c_str());

					fclose(fp);
					send_msg = ".\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());

					return 0;
				}
				/*ak sme danu spravu nenasli tak posleme chybove hlasenie klientovi */
				else if((deleted_msg[files_count-1] == true && to_info_number == files_count) || to_info_number > msg_count){
					msg_count = msg_count - to_delete();
					//-ERR no such message, only 1 message in maildrop\r\n
					send_msg = "-ERR no such message, only "+to_string(msg_count)+ " messages in maildrop\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());
					return 0;
				}
			}
		}
		closedir (dir);
	} else {
		exit(EXIT_FAILURE);
	}
	return 0;	
}

/* Funkcia ktora sa vola pri DELE 
	oznaci nam spravu na zmazanie

	Parsuje si vstup aby zistila ktoru spravu treba zmazat. */
int mark_msg_to_delete(char *data){
	
	string data_to_parse = "";
	data_to_parse.append(data);
	
	data_to_parse.erase(0,5);
	data_to_parse.pop_back();
	data_to_parse.pop_back();

	
	unsigned int to_delete_number = stoi(data_to_parse,nullptr);
	int return_number = to_delete_number;
	
	if(to_delete_number > deleted_msg.size() || to_delete_number <= 0){
		return 0; // msg does not exist
	}
	/* Oznaci danu spravu na zmazanie vo vektore pre zmazane spravy */
	if(deleted_msg[to_delete_number-1] == false){
			deleted_msg[to_delete_number-1] = true;
	}
	else if(deleted_msg[to_delete_number-1] == true){
		return return_number*-1;
	}
		
 return return_number;	
}

/* Funkcia ktora sa vola pri volani QUIT z transakcnej fazy a predtym nez sa uzavrie spojenie */
int update(int client_socket_fd){
	string send_msg = "";
	DIR *dir;
	struct dirent *ent;

	int files_count = 0;
	int not_deleted = 0;
	int flag = 0;
	string directory_path_cur = "";
	directory_path_cur.append(flagsSet.dir_path);
	directory_path_cur.append("/cur/");

	/* Otvorime si cur zlozku, zacneme ju prechadzat */
	if ((dir = opendir (directory_path_cur.c_str())) != NULL) {
		while ((ent = readdir (dir)) != NULL) {
	  		string directory_path_cur_temp = "";
			directory_path_cur_temp.append(directory_path_cur);
			if(strcmp(ent->d_name,".") != 0 && strcmp(ent->d_name,"..") != 0){
				directory_path_cur_temp.append(ent->d_name);
		
				files_count = files_count + 1;
				not_deleted = not_deleted +1;

				/* Ak sme na sprave ktoru treba zmazat, tak ju zmazeme */
				if(deleted_msg[files_count-1] == true){
					if(remove(directory_path_cur_temp.c_str()) != 0){
						flag = 1;
					}
					not_deleted = not_deleted -1;
				}
			}
		}
		closedir (dir);
		/* Ak sa uspesne zmazali vsetky spravy*/
		if(flag == 0){
			// VSETKO OK
			//+OK dewey POP3 server signing off 5 message(s) left)\r\n
			send_msg = "+OK POP3 server signing off "+to_string(not_deleted)+ " messages left\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			closeClientSock(client_socket_fd);
		}
		/* Ak sa nejaka sprava nezmazala */
		else if (flag == 1){
			//ERR
			//-ERR some deleted messages not removed\r\n
			send_msg = "-ERR some deleted messages not removed\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			closeClientSock(client_socket_fd);
		}
		
		
		
	} else {
		send_msg = "-ERR some deleted messages not removed\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		closeClientSock(client_socket_fd);
	}
	return 0;	
}

/* Funkcia ktora sa vola z autorizacnej fazy pri pouziti sifrovania hesla */
int apop_login(char *data, char *timestamp){
	string data_to_parse = "";
	data_to_parse.append(data);
	
	FILE *fp;
	
	char username[255];
	char password[255];
	
	if ((fp = fopen(flagsSet.auth_path, "r")) == NULL){
		fprintf(stderr, "Error: Auth file does not exist or can not be open.\n");
		return 2;
	}
	
	fgets(username, 255, (FILE*)fp);
	fgets(password, 255, (FILE*)fp);
	fclose(fp);
	
	string str_password = "";
	
	str_password.append(password);

	str_password.erase(0,11);
	str_password.pop_back();	
	
	string str_username = "";

	str_username.append(username);
	
	str_username.erase(0,11);
	str_username.pop_back();
	
	/* Potrebujeme si vytvorit vlastny hash s ktorym budeme porovnavat
	hasd od uzivatela */
	string to_hash = "";
	to_hash.append(timestamp);
	to_hash.append(str_password);
	
	string hash = "";
	/* Zavolame hashovaciu funkciu */
	hash = md5(to_hash);
	
	
	data_to_parse.erase(0,5);
	size_t space_char = data_to_parse.find_first_of(" ");
	if(space_char == string::npos){
		return 1;
	}
	/* porovname heslo od klienta s nasim hashom */
	else if(data_to_parse.compare(0,space_char,str_username) == 0){
		data_to_parse.erase(0, space_char+1);
		data_to_parse.pop_back();
		data_to_parse.pop_back();
		if(hash.compare(data_to_parse) == 0){
			return 0;
		}
		else{
			return 1;
		}
	}
return 1;
}
/* Funkcia ktora posiela len isty pocet riadkov zpravy po hlavicke 
Velmi podobna RETR rozdiely su okomentovane */
int send_top(char *data, int client_socket_fd){
	
	string send_msg = "";
	DIR *dir;
	struct dirent *ent;
	
	int files_size = 0;
	int files_count = 0;
	int msg_count = count_in_cur();
	int number_of_lines = 0;

	/* Nastavime si cestu do zlozky cur */
	string directory_path_cur = "";
	directory_path_cur.append(flagsSet.dir_path);
	directory_path_cur.append("/cur/");
	string data_to_parse = "";
	data_to_parse.append(data);
	
	data_to_parse.erase(0,4);
	
	size_t first_of = 0;
	/* Potrebujeme si ziskat cislo spravy a pocet riadkov z prijateho prikazu */
	first_of = data_to_parse.find_first_of(" ");
	string n = data_to_parse.substr(0,first_of);
	data_to_parse.erase(0, first_of+1);
	data_to_parse.pop_back();
	data_to_parse.pop_back();
	string m = data_to_parse;
	
	int to_msg_number = stoi(n,nullptr);
	int to_lines_number = stoi(m, nullptr);
	/* Ak prisiel v prikaze zly pocet riadkov */
	if(to_lines_number < 0){
		send_msg = "-ERR number of lines must be 0 or greater\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		return 0;
	}
	
	/* Prechadzame zlozku kym nenajdeme spravu ktoru klient chce obdrzat */
	if ((dir = opendir (directory_path_cur.c_str())) != NULL) {
		while ((ent = readdir (dir)) != NULL) {
			string directory_path_cur_temp = "";
			directory_path_cur_temp.append(directory_path_cur);
	  
			if(strcmp(ent->d_name,".") != 0 && strcmp(ent->d_name,"..") != 0){
				directory_path_cur_temp.append(ent->d_name);
		

				files_count = files_count + 1;
				files_size = size_msg[files_count-1];

				/* Najdeme spravu ktora nie je zmazana a chce ju klient */
				if(deleted_msg[files_count-1] == false && to_msg_number == files_count){
					FILE *fp;

					char buffer[1024];
					string to_send = "";
					memset(buffer, 0, sizeof(buffer));
					/* Pred odoslanim do nej musime doplnit znaky CRLF aby sme dodrzali standard */
					if ((fp = fopen(directory_path_cur_temp.c_str(), "r")) != NULL){
						int last_was;
						int c;
						int snd_to_last; //pomocne premenne aby sme vedeli urcit kedy sa konci hlavicka
						int trd_to_last;
						int real_last;
						int msg_flag = 0;
						/* V pripade ze sme precitali uz ziadany pocet riadkov ukoncime citanie suboru */
						while ((c = getc(fp)) != EOF && number_of_lines < to_lines_number){
							if(c == '\n' && last_was == '\r'){
								to_send = to_send + (char)c;
							}
							else if(c == '\n' && last_was != '\r'){
								trd_to_last = snd_to_last;
								snd_to_last = real_last;
								to_send = to_send + '\r' + (char)c;	
								real_last = '\r';
							}
							else if (c == '.' && last_was == '\n'){
								to_send = to_send + '.' + (char)c;
							}
							else {
								to_send = to_send + (char)c;
							}
							
							if(msg_flag == 1 && c == '\n'){
								number_of_lines = number_of_lines +1;
							} //ak sa konci hlavicka nasleduju za sebou \r\n\r\n, nastavime flag na 1 a pri kazdom dalsiom prechode ked narazime na koniec riadku zvysime pocet riadkov 
							if(trd_to_last == '\r' && snd_to_last == '\n' && real_last == '\r' && c == '\n'){
								msg_flag = 1;
							}

							
							trd_to_last = snd_to_last;
							snd_to_last = real_last;
							real_last = c;
							last_was = c;
					
						}
						if(c == EOF && last_was != '\n'){
							to_send = to_send +"\r\n";
						}
					}
					
					/*Odosielame spravy*/
					send_msg = "+OK "+to_string(files_count) + " " + to_string(files_size)+"\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());

					send_msg = to_send;
					sendMessage(client_socket_fd, send_msg.c_str());

					fclose(fp);
					send_msg = ".\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());

					return 0;
				}
				/*ak sme danu spravu nenasli tak posleme chybove hlasenie klientovi */
				else if((deleted_msg[files_count-1] == true && to_msg_number == files_count) || to_msg_number > msg_count){
					msg_count = msg_count - to_delete();
					//-ERR no such message, only 1 message in maildrop\r\n
					send_msg = "-ERR no such message, only "+to_string(msg_count)+ " messages in maildrop\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());
					return 0;
				}
			}
		}
		closedir (dir);
	} else {
		exit(EXIT_FAILURE);
	}
	return 0;	
}



/* Hlavna funkcia, ktora sa vola vzdy ked pride sprava od klienta
	urcuje kam ma server dalej pokracovat.
	
	Jej sucastou je len porovnavanie prvych 4 alebo 3 znakov a urcenie
	aka sprava prisla. Ak sa nenajde zhoda posle sa chybova sprava klientovi.
	
	FAZA pripojenia je drzana v premennej status
	*/

int decode_request(int client_socket_fd, char *data, int status, char *timestamp){
	// STATUS 0 - start, 1 - LOGIN, 2 - TRANSAKCE
	string data_to_parse = "";
	data_to_parse.append(data);
	
	for(int i = 0; i<4; i++){	
	data_to_parse[i] = toupper(data_to_parse[i]);
	}
	
	string send_msg = "";
	/* APOP */ 
	if(data_to_parse.compare(0,4,"APOP") == 0 && status == 0 && flagsSet.clear == false){
		if(apop_login(data, timestamp) == 0){
			/* Spravne udaje, skusame locknut pristup k maildir */
			if(mtx.try_lock()){
				/* Vsetko sa podarilo pokracujeme */
				if(move_new_to_cur() == 0){
					int msg_count = count_in_cur();
					int msg_size = size_in_cur(0);


					deleted_msg.assign(msg_count, false);
					
					send_msg = "+OK username's maildrop has " + to_string(msg_count) + " messages (" + to_string(msg_size) +" octets)\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());
					/* Vratime 2, co je nas status, presunuli sme sa do transakcnej fazy*/
					return 2;
				}
				else{
					fprintf(stderr,"Error: Could not move filed from new to cur");
					exit(EXIT_FAILURE);
				}
			}
			else {
				send_msg = "-ERR could not give access to maildrop.\r\n";
				sendMessage(client_socket_fd, send_msg.c_str());
				/* Vraciame 0, ostavame v autorizacnej faze, ocakavame znovu pokus o prihlasenie */
				return 0;
			}
		}
		else if(apop_login(data, timestamp) == 1){
			send_msg = "-ERR invalid username or password\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
				/* Vraciame 0, ostavame v autorizacnej faze, ocakavame znovu pokus o prihlasenie */
			return 0;
		}
	}
	/* USER */
	else if (data_to_parse.compare(0,4,"USER") == 0 && status == 0 && flagsSet.clear == true){
		if(checkUser(data) == 0){
			send_msg = "+OK now enter password\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			/* Dostali sme spravne username, presuvame sa na cakanie hesla */
			return 1;
		}
		else if (checkUser(data) == 1){
			send_msg = "-ERR invalid username\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
				/* Vraciame 0, ostavame v autorizacnej faze, ocakavame znovu pokus o prihlasenie */
			return 0;
		}
		else closeClientSock(client_socket_fd);
		
	}
	/* PASS */
	else if (data_to_parse.compare(0,4,"PASS") == 0 && status == 1 && flagsSet.clear == true){
		int test = checkPassword(data);
		if(test == 0){
			/* Spravne udaje skusame locknut maildir */
			if(mtx.try_lock()){
				if(move_new_to_cur() == 0){
					int msg_count = count_in_cur();
					int msg_size = size_in_cur(0);
					/* Vsetko sa podarilo tak si vytvorime vector o velkosti poctu sprav v  cur, do ktoreho budeme oznacovat spravy na zmazanie */
					deleted_msg.assign(msg_count, false);
					
					send_msg = "+OK username's maildrop has " + to_string(msg_count) + " messages (" + to_string(msg_size) +" octets)\r\n";
					sendMessage(client_socket_fd, send_msg.c_str());
					/* Vratime 2, co je nas status, presunuli sme sa do transakcnej fazy*/
					return 2;
				}
			}
			else {
				send_msg = "-ERR could not give access to maildrop.\r\n";
				sendMessage(client_socket_fd, send_msg.c_str());
				return 0; //Status
			}
		}
		else if (checkPassword(data) == 1){
			send_msg = "-ERR invalid password\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			return 0; //Status
		}
		else closeClientSock(client_socket_fd);
	}
	/* Noop*/
	else if(data_to_parse.compare(0,4,"NOOP") == 0 && status != 1){
		send_msg = "+OK\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		return status;
	}
	/* STAT */
	else if(data_to_parse.compare(0,4,"STAT") == 0 && status == 2){ 				//STAT
		int msg_count = count_in_cur() - to_delete();
		int msg_size = size_in_cur(1);
		//+OK x xyz\r\n
		send_msg = "+OK " + to_string(msg_count) + " " + to_string(msg_size) +"\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		return status;
	}
	//LIST
	else if(data_to_parse.compare(0,4,"LIST") == 0 && status == 2 && strlen(data_to_parse.c_str()) < 7){
		/* Pocet sprav v cur */
		int msg_count = count_in_cur() - to_delete();
		/* Ak nula tak odpovedame */
		if(msg_count == 0){
			send_msg = "+OK 0 messages in maildrop\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			send_msg = ".\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			return status;
		}
		else{
			/* Inak odpovedame info o tom kolko sprav a ich velksot */
			int msg_size = size_in_cur(1); 
			
			send_msg = "+OK " + to_string(msg_count) + " messages (" + to_string(msg_size) +" octets)\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			
			send_list(0, client_socket_fd, data);
			
			send_msg = ".\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());

			return status;
		}
	}
	/* LIST  <X> */ 
	else if(data_to_parse.compare(0,4,"LIST") == 0 && status == 2 && strlen(data_to_parse.c_str()) > 7){					
		send_list(1, client_socket_fd, data);
		return status;
	}
	else if(data_to_parse.compare(0,4,"DELE") == 0 && status == 2 && strlen(data_to_parse.c_str()) > 7){
		int temp;
		if((temp = mark_msg_to_delete(data)) > 0){
			send_msg = "+OK message "+to_string(temp)+" deleted\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			
			//+OK message 1 deleted\r\n
		}
		else if (mark_msg_to_delete(data) == 0){
			int msg_count = count_in_cur() - to_delete();
			send_msg = "-ERR no such message (only "+to_string(msg_count)+" messages in maildrop)\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
			//-ERR no such message (only x messages in maildrop)\r\n
		}
		else if((temp = mark_msg_to_delete(data)) < 0){
			send_msg = "-ERR message "+to_string(temp*-1)+" already deleted\r\n";
			sendMessage(client_socket_fd, send_msg.c_str());
		}
		//-ERR message 1 already deleted\r\n 
		return status;
	}
	else if(data_to_parse.compare(0,4,"RSET") == 0 && status == 2){					//RSET
		deleted_msg.clear();
		int msg_count = count_in_cur();

		deleted_msg.assign(msg_count, false);
		int msg_size = size_in_cur(1); 
		//+OK x messages in maildrop (xyz octets)\r\n
		send_msg = "+OK " + to_string(msg_count) + " messages in maildrop (" + to_string(msg_size) +" octets)\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		return status;
	}
	else if(data_to_parse.compare(0,4,"UIDL") == 0 && status == 2 && strlen(data_to_parse.c_str()) > 7){					//UIDL number
		send_uidl(1, client_socket_fd, data);
		return status;
	}
	else if(data_to_parse.compare(0,4,"UIDL") == 0 && status == 2 && strlen(data_to_parse.c_str()) < 7){					//UIDL
		send_uidl(0, client_socket_fd, data);
		send_msg = ".\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		return status;
	}
	else if(data_to_parse.compare(0,4,"RETR") == 0 && status == 2 && strlen(data_to_parse.c_str()) > 7){					//RETR number
		send_retr(data,client_socket_fd);
		return status;
	}
	else if(data_to_parse.compare(0,3,"TOP") == 0 && status == 2 && strlen(data_to_parse.c_str()) > 8){					//RETR number
		send_top(data,client_socket_fd);
		return status;
	}
	else if(data_to_parse.compare(0,4,"QUIT") == 0 && status == 2){					//QUIT
		update(client_socket_fd);
		return 0;
	}
	else if(data_to_parse.compare(0,4,"QUIT") == 0 && status != 2){					//QUIT
		closeClientSockUnlogged(client_socket_fd);
		return 0;
	}
	else if(status == 1){
		send_msg = "-ERR invalid request\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		return 0;
	}
	else {
		send_msg = "-ERR invalid request\r\n";
		sendMessage(client_socket_fd, send_msg.c_str());
		return status;
	}
	
	return 0;
}

/* FUNKCIA NA KOMUNIKACIU S CLIENTOM */

void *communication(void *param_client_socket){
	int status = 0; // uplny zaciatok
	int flags;
	int client_socket_fd;
	client_socket_fd = *(int*) param_client_socket;
	
	random_difference = random_difference + 1;
	
	/* Pokusime sa nastavit socket na neblokujuci */
	if ((flags=fcntl(client_socket_fd,F_GETFL,0))< 0){
		fprintf(stderr, "Error: Could not get socket flags\n");
		closeClientSock(client_socket_fd);
	}
	/* Nastavime neblokujuci flag */
	flags |= O_NONBLOCK; 
	/* Skusime aktualizovat nastavenie socketu */ 
	if (fcntl(client_socket_fd, F_SETFL,flags) < 0){
		fprintf(stderr, "Error: Could not set nonblock socket.\n");
		closeClientSock(client_socket_fd);
	}
	

	/* Ak vsetko v pohdoe pokracujeme */
	
	/* Ziskame si informacie na vytvorenie time stamp */
	int process_id = getpid();
	time_t clock = time(0);
	char hostname[HOST_NAME_MAX];
	gethostname(hostname, HOST_NAME_MAX);
	
	/* Pridame zvysenie hodin aby sme mali pre kazdeho klienta iny timestamp aj ak sa pripoja v rovnaku sekundu */
	clock = clock + random_difference;
	
	char send_msg[255];
	
	string timestamp = "";
	timestamp = "<"+to_string(process_id)+"."+to_string(clock)+"@"+hostname+">";
	
	char timestamp_arg[100];
	strcpy(timestamp_arg, timestamp.c_str());
	
	strcpy(send_msg,"+OK POP3 server ready <");
	strcat(send_msg, to_string(process_id).c_str());
	strcat(send_msg,".");
	strcat(send_msg, to_string(clock).c_str());
	strcat(send_msg,"@");
	strcat(send_msg, hostname);
	strcat(send_msg,">\r\n");
			
	/* Posleme uvitaciu spravu s timestamp klientovi */
	sendMessage(client_socket_fd, send_msg);
	
	bool waiting = true;
	string received_data = "";	
	int received = 0;
	char receiver[1024];
	
	fd_set fdesc;
	struct timeval wait; 
	
	FD_ZERO(&fdesc); // vynulujeme mnozinu sledovanych deskriptorov
	FD_SET(client_socket_fd,&fdesc); // nastavime si nas socket do mnoziny sledovanych descriptorov
	
	/* Zahajime cakanie na spravy od klienta */
	while(waiting){
		wait.tv_sec = 600; // timeout pripojenia po 10 minutach
		wait.tv_usec = 0;
		/*Zistujeme ci mame nejake dava od klienta */
		int sel_check = select(FD_SETSIZE,&fdesc,NULL,NULL,&wait);
		
		if(sel_check == 0){
			//time out
			closeClientSock(client_socket_fd);
		}
		if(sel_check == -1){
			// nedokazali sme prijat
			fprintf(stderr,"Error: Could not read data from client\n");
			closeClientSock(client_socket_fd);
		}
		memset(receiver, 0, sizeof(receiver));
		/* Prisli nam data */
		if((received = recv(client_socket_fd, receiver, 1024, 0))  > 0){
			status = decode_request(client_socket_fd, receiver, status, timestamp_arg);
		}
		else {
			break;
		}
	}
	closeClientSock(client_socket_fd);
return 0;
}

/* Funkcia na prvotne overenie zadanie spravnosti PATH do maildir a k auth file */
void testPaths(){
	FILE *fp;
	DIR *dir;
	char username[255];
	char password[255];
	
	if ((fp = fopen(flagsSet.auth_path, "r")) == NULL){
		fprintf(stderr, "Error: Auth file does not exist or can not be open.\n");
		exit(EXIT_FAILURE);
	}
	
	if ((dir = opendir(flagsSet.dir_path)) == NULL){
		fprintf(stderr, "Error: Maildir does not exist or can not be open.\n");
		exit(EXIT_FAILURE);
	}
	
	
	fgets(username, 255, (FILE*)fp);
	fgets(password, 255, (FILE*)fp);
	fclose(fp);
	
	string str_username = "";
	string str_password = "";
	
	str_username.append(username);
	str_password.append(password);
	
	str_username.erase(0,11);
	str_password.erase(0,11);
	str_username.pop_back();
	str_password.pop_back();
	
	
	closedir (dir);
	
}

/* Handler v pripade ze pride SIGINT */
void sig_handler(int SIG_num){
	for(unsigned int i = 0; i< socket_vector.size(); i++){
		close(socket_vector[i]);
	}
	exit(SIG_num);
}

int main(int argc, char *argv[])
{

	signal(SIGINT, sig_handler);

	flagsSet = arguments(argc, argv);
	
	if(flagsSet.help){
		write_help();
		exit(EXIT_SUCCESS);
	}
	
	if(flagsSet.reset){
		reset();
	}
	
	testPaths(); // TESTOVAT CI AUTH FILE a DIR PATH MA SPRAVNY FORMAT

	
	int socket_fd, client_socket_fd;
	socklen_t socket_size;
	struct sockaddr_in server_address, client_address;
	
	/* Socket descriptor */
	
	if(( socket_fd  = socket(AF_INET, SOCK_STREAM,0)) < 0){
		fprintf(stderr, "Error: No Socket Descriptor obrained. \n");
		exit(EXIT_FAILURE);
	}
	
	server_address.sin_family = AF_INET;
	server_address.sin_port = htons(flagsSet.port_no);
	server_address.sin_addr.s_addr = INADDR_ANY;
	
	/* Port binding */
	
	if( bind(socket_fd, (struct sockaddr*)&server_address, sizeof(struct sockaddr)) == -1){
		fprintf(stderr, "Error: Port binding failed. \n");
		exit(EXIT_FAILURE);
	}
	
	/* Listening */ 
	
	if (listen(socket_fd, 1) < 0){
		fprintf(stderr,"Error: Listening failed. \n");
		exit(EXIT_FAILURE);
	}
	
	bool waiting = true;
	while(waiting){
		socket_size = sizeof(client_address); 
		if((client_socket_fd = accept(socket_fd, (struct sockaddr *)&client_address, &socket_size)) == -1){
			fprintf(stderr,"Error: No client Socket Descriptor obtained. \n");
			exit(EXIT_FAILURE);
		}
		socket_vector.push_back(client_socket_fd);
		// PTHREAD HERE
		
		pthread_t id;
		pthread_create(&id, NULL, communication, &client_socket_fd);
		pthread_detach(id);
	}
	
	

   exit(EXIT_SUCCESS);
}