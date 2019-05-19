Vytvoril: Ivan Eštvan, xestva00
29.4.2016

README k 2. projektu do predmetu IPK


Toto README je k suborom server a client.

Server je spustitelny subor, ktory spusti server, na ktory sa moze napojit lubovolny pocet clientov simultanne ak poznaju meno hosta a port
Client je spustitelny subor pomocou ktoreho sa dokaze uzivatel pripojit na dany server za pomoci mena hosta a portu a nasledne stahovat/nahravat
subor z/na server.

 

Samostatné spustenie:

Pomocou "make" sa vytvoria spustitelne subory client a server.

	Spustenie serveru:

	./server -p <cislo_portu> ---- argument -p a <cislo_portu> su povinne

	Spustenie klientu:
	
	./client -h <meno_hosta> -p <cislo_portu> [-u|-d] [<meno_suboru>] ---- argumenty -h <meno_hosta> a -p <cislo_portu> su povinne			
																	  ---- argumenty -u alebo -d su exkluzivne dobrovolne argumenty obe doplna <meno_suboru>
																	  ---- argument -h definuje meno hosta
																	  ---- argument -p definuje cislo portu
																	  ---- argument -u definuje upload (nahravanie) daneho suboru 
																	  ---- argument -d definuje download (stahovanie) daneho suboru
		
Spustenie pomocou prilozeneho testovacieho scriptu test.sh:

	Spustenie scriptu:
	
	./test.sh
	
	Testovaci Script testuje preklad programu, spustenie serveru na porte 3456, upload a download pomocou clienta cez port 3456 na localhost.
	Vstupne subory su ulozene v zlozkach client_files, server_files.
	Do rovnakych zloziek sa ulozi aj vystup testovacieho scriptu.
	
	Pred spustenim serveru a clienta sa dany program presunie z hlavneho adresaru do client_files a server_files.

	Ocakavany vystup testovacieho scriptu:
	
	Starting Compilation
	[preklad info]
	Moving Server to folder
	Moving Client to Folder
	Going to Start Server
	With Port 3456
	[Chyba ak sa nepodari spustit server]
	Client Sending picture.jpg
	[chyba ak sa nepodarilo spustit server]
	Client Sending text.txt
	[chyba ak sa nepodarilo spustit server]
	Client Download picture2.jpg
	[chyba ak sa nepodarilo spustit server]
	Client Download text2.txt
	[chyba ak sa nepodarilo spustit server]
	Client Download Wrong File
	Error: File not found on server
	Cliend Sending wrong file
	Error: File Not Found.
	Client connecting wrong port
	Error: Connection to Host failed!
	Client connecting Wrong hosta
	Error: Connection to Host failed! "ALEBO" Error: Host not found --- druhy error by sa maj objavit v pripade ze nepozname hosta
	
	
		
Vystup programu:

Poslane subory sa ukladaju do adresaru so serverom v pripade -u, do adresaru s klientom v pripade -d.

V pripade argumentu -u pri spustani klienta to mozu byt:
	- novy subor s danym menom, v adresari serveru a rovnakym obsahom ako dany subor v adresari klienta
	- ak subor s danym menom existoval tak sa jeho stary obsah nahradi novym obsahom

V pripade argumentu -d pri spusteni klienta to mozu byt:
	- novy subor s danym menom, v adresari klienta a rovnakym obsahom ako dany subor v adresari servera
	- ak subor s danym menom existoval tak sa jeho stary obsah nahradi novym obsahom
	
Chyby:

V pripade, ze nastane chyba na strane klienta tak sa ukonci cely proces s chybovou hlaskou, ktora sa zapise na stderr.

V pripade, ze nastane chyba na strane serveru tak sa moze ukoncit proces serveru v pripade chyby pri zapinani serveru 
alebo sa ukonci podproces, ak nastane chyba az pocas komunikacie s klientom. V oboch pripadoch sa chybova hlaska vypise na stderr.



			

