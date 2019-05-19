
/* c016.c: **********************************************************}
{* Téma:  Tabulka s Rozptýlenými Položkami
**                      První implementace: Petr Přikryl, prosinec 1994
**                      Do jazyka C prepsal a upravil: Vaclav Topinka, 2005
**                      Úpravy: Karel Masařík, říjen 2014
**                      Úpravy: Radek Hranický, říjen 2014
**                      Úpravy: Radek Hranický, listopad 2015
**
** Vytvořete abstraktní datový typ
** TRP (Tabulka s Rozptýlenými Položkami = Hash table)
** s explicitně řetězenými synonymy. Tabulka je implementována polem
** lineárních seznamů synonym.
**
** Implementujte následující procedury a funkce.
**
**  HTInit ....... inicializuje tabulku před prvním použitím
**  HTInsert ..... vložení prvku
**  HTSearch ..... zjištění přítomnosti prvku v tabulce
**  HTDelete ..... zrušení prvku
**  HTRead ....... přečtení hodnoty prvku
**  HTClearAll ... zrušení obsahu celé tabulky (inicializace tabulky
**                 poté, co již byla použita)
**
** Definici typů naleznete v souboru c016.h.
**
** Tabulka je reprezentována datovou strukturou typu tHTable,
** která se skládá z ukazatelů na položky, jež obsahují složky
** klíče 'key', obsahu 'data' (pro jednoduchost typu float), a
** ukazatele na další synonymum 'ptrnext'. Při implementaci funkcí
** uvažujte maximální rozměr pole HTSIZE.
**
** U všech procedur využívejte rozptylovou funkci hashCode.  Povšimněte si
** způsobu předávání parametrů a zamyslete se nad tím, zda je možné parametry
** předávat jiným způsobem (hodnotou/odkazem) a v případě, že jsou obě
** možnosti funkčně přípustné, jaké jsou výhody či nevýhody toho či onoho
** způsobu.
**
** V příkladech jsou použity položky, kde klíčem je řetězec, ke kterému
** je přidán obsah - reálné číslo.
*/

#include "c016.h"

int HTSIZE = MAX_HTSIZE;
int solved;

/*          -------
** Rozptylovací funkce - jejím úkolem je zpracovat zadaný klíč a přidělit
** mu index v rozmezí 0..HTSize-1.  V ideálním případě by mělo dojít
** k rovnoměrnému rozptýlení těchto klíčů po celé tabulce.  V rámci
** pokusů se můžete zamyslet nad kvalitou této funkce.  (Funkce nebyla
** volena s ohledem na maximální kvalitu výsledku). }
*/

int hashCode ( tKey key ) {
	int retval = 1;
	int keylen = strlen(key);
	for ( int i=0; i<keylen; i++ )
		retval += key[i];
	return ( retval % HTSIZE );
}

/*
** Inicializace tabulky s explicitně zřetězenými synonymy.  Tato procedura
** se volá pouze před prvním použitím tabulky.
*/

void htInit ( tHTable* ptrht ) {

    if(ptrht == NULL){ //pointer check
        return;
    }
    int i = 0;
    while(i < HTSIZE){
        (*ptrht)[i] = NULL;
        i++;
    }

    return;
}

/* TRP s explicitně zřetězenými synonymy.
** Vyhledání prvku v TRP ptrht podle zadaného klíče key.  Pokud je
** daný prvek nalezen, vrací se ukazatel na daný prvek. Pokud prvek nalezen není,
** vrací se hodnota NULL.
**
*/

tHTItem* htSearch ( tHTable* ptrht, tKey key ) {

    if(ptrht == NULL || key == NULL || (*ptrht) == NULL){
        return NULL;
    }

    tHTItem *help = (*ptrht)[hashCode(key)]; //pomocny pointer

    while (help != NULL){ //vyhladavanie s danym klucom
            if(key == help->key){
                return help;
            }
            else {
                help = help->ptrnext;
            }
    }

    return help;
}

/*
** TRP s explicitně zřetězenými synonymy.
** Tato procedura vkládá do tabulky ptrht položku s klíčem key a s daty
** data.  Protože jde o vyhledávací tabulku, nemůže být prvek se stejným
** klíčem uložen v tabulce více než jedenkrát.  Pokud se vkládá prvek,
** jehož klíč se již v tabulce nachází, aktualizujte jeho datovou část.
**
** Využijte dříve vytvořenou funkci htSearch.  Při vkládání nového
** prvku do seznamu synonym použijte co nejefektivnější způsob,
** tedy proveďte.vložení prvku na začátek seznamu.
**/

void htInsert ( tHTable* ptrht, tKey key, tData data ) {

    if(ptrht == NULL || key == NULL || (*ptrht) == NULL){
        return;
    }

    tHTItem *help = htSearch(ptrht,key); //pomocny pointer s adresov polozky podla key

    if (help != NULL){ //nasli sme hladanu polozku
        help->data = data; //len prepis
        return;
    }

    help = (tHTItem *) malloc(sizeof(tHTItem)); //inak vytvarame novu polozku

    if (help != NULL){ //ak vsetko perbehlo v pohode
    help->ptrnext = (*ptrht)[hashCode(key)]; //pridavanie polozky
    (*ptrht)[hashCode(key)] = help;
    help->key = key;
    help->data = data;
    }
    else {
        return;
    }

    return;
}

/*
** TRP s explicitně zřetězenými synonymy.
** Tato funkce zjišťuje hodnotu datové části položky zadané klíčem.
** Pokud je položka nalezena, vrací funkce ukazatel na položku
** Pokud položka nalezena nebyla, vrací se funkční hodnota NULL
**
** Využijte dříve vytvořenou funkci HTSearch.
*/

tData* htRead ( tHTable* ptrht, tKey key ) {

    if(ptrht == NULL || key == NULL || (*ptrht) == NULL){
        return NULL;
    }
    tHTItem *help = htSearch(ptrht,key); //pomocny pointer s adrevos polozky podla key

    if(help == NULL){ //ak sme nenasli
        return NULL;
    }
    else{
        return &help->data; //ak sme nasli vraciame datovu cast
    }
}

/*
** TRP s explicitně zřetězenými synonymy.
** Tato procedura vyjme položku s klíčem key z tabulky
** ptrht.  Uvolněnou položku korektně zrušte.  Pokud položka s uvedeným
** klíčem neexistuje, dělejte, jako kdyby se nic nestalo (tj. nedělejte
** nic).
**
** V tomto případě NEVYUŽÍVEJTE dříve vytvořenou funkci HTSearch.
*/

void htDelete ( tHTable* ptrht, tKey key ) {

    if(ptrht == NULL || key == NULL || (*ptrht) == NULL){
        return;
    }

    tHTItem *help_1 = (*ptrht)[hashCode(key)]; //pomocne pointre
    tHTItem *help_2 = (*ptrht)[hashCode(key)];

    while (help_1 != NULL && help_1->key != key ){ //hladanie polozky
            help_2 = help_1;
            help_1 = help_1->ptrnext;
    }
    if(help_1 == NULL){ //nic sme nenasli
        return;
    }
    else if(help_1 == help_2){ //odstranovanie prvej polozky
        (*ptrht)[hashCode(key)] = help_1->ptrnext;
    }
    else{
        help_2->ptrnext = help_1->ptrnext;
    }
    free((void *)help_1); //uvolnenie polozky


return;
}

/* TRP s explicitně zřetězenými synonymy.
** Tato procedura zruší všechny položky tabulky, korektně uvolní prostor,
** který tyto položky zabíraly, a uvede tabulku do počátečního stavu.
*/

void htClearAll ( tHTable* ptrht ) {

    if(ptrht == NULL){
        return;
    }
    tHTItem *help = NULL;

    int i = 0;
    while(i < HTSIZE){
        while ((*ptrht)[i] != NULL){
            help = (*ptrht)[i];
            (*ptrht)[i] = (*ptrht)[i]->ptrnext;
            free((void *) help);
        }
        i++;
    }

    return;
}
