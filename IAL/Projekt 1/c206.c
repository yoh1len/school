	
/* c206.c **********************************************************}
{* Téma: Dvousměrně vázaný lineární seznam
**
**                   Návrh a referenční implementace: Bohuslav Křena, říjen 2001
**                            Přepracované do jazyka C: Martin Tuček, říjen 2004
**                                            Úpravy: Bohuslav Křena, říjen 2016
**
** Implementujte abstraktní datový typ dvousměrně vázaný lineární seznam.
** Užitečným obsahem prvku seznamu je hodnota typu int.
** Seznam bude jako datová abstrakce reprezentován proměnnou
** typu tDLList (DL znamená Double-Linked a slouží pro odlišení
** jmen konstant, typů a funkcí od jmen u jednosměrně vázaného lineárního
** seznamu). Definici konstant a typů naleznete v hlavičkovém souboru c206.h.
**
** Vaším úkolem je implementovat následující operace, které spolu
** s výše uvedenou datovou částí abstrakce tvoří abstraktní datový typ
** obousměrně vázaný lineární seznam:
**
**      DLInitList ...... inicializace seznamu před prvním použitím,
**      DLDisposeList ... zrušení všech prvků seznamu,
**      DLInsertFirst ... vložení prvku na začátek seznamu,
**      DLInsertLast .... vložení prvku na konec seznamu, 
**      DLFirst ......... nastavení aktivity na první prvek,
**      DLLast .......... nastavení aktivity na poslední prvek, 
**      DLCopyFirst ..... vrací hodnotu prvního prvku,
**      DLCopyLast ...... vrací hodnotu posledního prvku, 
**      DLDeleteFirst ... zruší první prvek seznamu,
**      DLDeleteLast .... zruší poslední prvek seznamu, 
**      DLPostDelete .... ruší prvek za aktivním prvkem,
**      DLPreDelete ..... ruší prvek před aktivním prvkem, 
**      DLPostInsert .... vloží nový prvek za aktivní prvek seznamu,
**      DLPreInsert ..... vloží nový prvek před aktivní prvek seznamu,
**      DLCopy .......... vrací hodnotu aktivního prvku,
**      DLActualize ..... přepíše obsah aktivního prvku novou hodnotou,
**      DLSucc .......... posune aktivitu na další prvek seznamu,
**      DLPred .......... posune aktivitu na předchozí prvek seznamu, 
**      DLActive ........ zjišťuje aktivitu seznamu.
**
** Při implementaci jednotlivých funkcí nevolejte žádnou z funkcí
** implementovaných v rámci tohoto příkladu, není-li u funkce
** explicitně uvedeno něco jiného.
**
** Nemusíte ošetřovat situaci, kdy místo legálního ukazatele na seznam 
** předá někdo jako parametr hodnotu NULL.
**
** Svou implementaci vhodně komentujte!
**
** Terminologická poznámka: Jazyk C nepoužívá pojem procedura.
** Proto zde používáme pojem funkce i pro operace, které by byly
** v algoritmickém jazyce Pascalovského typu implemenovány jako
** procedury (v jazyce C procedurám odpovídají funkce vracející typ void).
**/

#include "c206.h"

int solved;
int errflg;

void DLError() {
/*
** Vytiskne upozornění na to, že došlo k chybě.
** Tato funkce bude volána z některých dále implementovaných operací.
**/	
    printf ("*ERROR* The program has performed an illegal operation.\n");
    errflg = TRUE;             /* globální proměnná -- příznak ošetření chyby */
    return;
}

void DLInitList (tDLList *L) {
/*
** Provede inicializaci seznamu L před jeho prvním použitím (tzn. žádná
** z následujících funkcí nebude volána nad neinicializovaným seznamem).
** Tato inicializace se nikdy nebude provádět nad již inicializovaným
** seznamem, a proto tuto možnost neošetřujte. Vždy předpokládejte,
** že neinicializované proměnné mají nedefinovanou hodnotu.
**/
    L->First = NULL;
    L->Last = NULL;
    L->Act = NULL;

return;
}

void DLDisposeList (tDLList *L) {
/*
** Zruší všechny prvky seznamu L a uvede seznam do stavu, v jakém
** se nacházel po inicializaci. Rušené prvky seznamu budou korektně
** uvolněny voláním operace free. 
**/
    tDLElemPtr hlp;
    hlp = NULL;
   /*
    * Prechod od prveho do posledneho prvku kym ukazatel First nie je NULL.
    */
    while(L->First != NULL){
        L->Act = L->First; //Zmeni aktívny prvok.
        L->First = L->First->rptr; //Posun ukazatela First na nasledujuci prvok
        hlp = L->Act; //Uvolnenie aktívneho prvku.
        free(hlp);
    }
    L->Act = NULL; //Aktivny prvok na stav po inicializacii.
    L->Last = NULL;

return;
}

void DLInsertFirst (tDLList *L, int val) {
/*
** Vloží nový prvek na začátek seznamu L.
** V případě, že není dostatek paměti pro nový prvek při operaci malloc,
** volá funkci DLError().
**/
    tDLElemPtr new_first;
    new_first = NULL;

    if((new_first = malloc(sizeof(struct tDLElem))) == NULL){ //alokacia miesta a kontrola jej uspesnosti pre prvok zoznamu
        DLError();
    }
    new_first->rptr = L->First; //posun prveho na dalsi
    new_first->lptr = NULL; //na predchadzajucom nič
	if((L->First == NULL) && (L->Last == NULL)){ //ak je prazdny zoznam
            L->Last = new_first; //nastavim novy prvy aj ako posledny
        }
    else {
        L->First->lptr = new_first;
    }
        //zapis dat a vsunutie na zaciatok zoznamu
    new_first->data = val;
    L->First = new_first;

return;
}

void DLInsertLast(tDLList *L, int val) {
/*
** Vloží nový prvek na konec seznamu L (symetrická operace k DLInsertFirst).
** V případě, že není dostatek paměti pro nový prvek při operaci malloc,
** volá funkci DLError().
**/ 	
    tDLElemPtr new_last;
    new_last = NULL;

    if((new_last = malloc(sizeof(struct tDLElem))) == NULL){ //alokacia miesta a kontrola jej uspesnosti pre prvok zoznamu
        DLError();
    }
    new_last->lptr = L->Last;
    new_last->rptr = NULL;
    if((L->Last == NULL) && (L->First == NULL)){ //to iste co insert first akurat nastavime novy posledny aj ako prvy
        L->First = new_last;
    }
    else {
        L->Last->rptr = new_last;
    }
    new_last->data = val;
    L->Last = new_last;

return;
}

void DLFirst (tDLList *L) {
/*
** Nastaví aktivitu na první prvek seznamu L.
** Funkci implementujte jako jediný příkaz (nepočítáme-li return),
** aniž byste testovali, zda je seznam L prázdný.
**/
    L->Act = L->First;

return;
}

void DLLast (tDLList *L) {
/*
** Nastaví aktivitu na poslední prvek seznamu L.
** Funkci implementujte jako jediný příkaz (nepočítáme-li return),
** aniž byste testovali, zda je seznam L prázdný.
**/
	
    L->Act = L->Last;

return;
}

void DLCopyFirst (tDLList *L, int *val) {
/*
** Prostřednictvím parametru val vrátí hodnotu prvního prvku seznamu L.
** Pokud je seznam L prázdný, volá funkci DLError().
**/
    if(L->First == NULL){
        DLError();
		return;
    }
    else {
    *val = L->First->data;
    }

return;
}

void DLCopyLast (tDLList *L, int *val) {
/*
** Prostřednictvím parametru val vrátí hodnotu posledního prvku seznamu L.
** Pokud je seznam L prázdný, volá funkci DLError().
**/
    if(L->First == NULL){
        DLError();
		return;
    }
    else {
    *val = L->Last->data;
    }

return;
}

void DLDeleteFirst (tDLList *L) {
/*
** Zruší první prvek seznamu L. Pokud byl první prvek aktivní, aktivita 
** se ztrácí. Pokud byl seznam L prázdný, nic se neděje.
**/
    tDLElemPtr del_first;
    del_first = NULL;

    if(L->First == NULL){ //ak je zoznam prazdny tak sa nic nedeje
		return;
	}

    if(L->Act == L->First){ //zrusenie aktivity zoznamu
        L->Act = NULL;
    }

    if(L->Last == L->First){ //ak je tam len jeden vstup tak sa vratime na prazdny zoznam
        del_first = L->First;
        free(del_first);
        L->First = NULL;
        L->Last = NULL;
    }
    else {
    del_first = L->First;
    L->First = L->First->rptr; //uprava ukazatela na novy prvy prvok
	L->First->lptr = NULL;
    free(del_first); //uvolnenie pamati
    }

return;
}	

void DLDeleteLast (tDLList *L) {
/*
** Zruší poslední prvek seznamu L. Pokud byl poslední prvek aktivní,
** aktivita seznamu se ztrácí. Pokud byl seznam L prázdný, nic se neděje.
**/ 
	
	
    tDLElemPtr del_last;
    del_last = NULL;

    if(L->First == NULL){ //ak je zoznam prazdny tak sa nic nedeje
		return;
	}

    if(L->Act == L->Last){ //zrusenie aktivity zoznamu
        L->Act = NULL;
    }

    if(L->Last == L->First){ //to ise ako deletefirst
        del_last = L->Last;
        free(del_last);
        L->First = NULL;
        L->Last = NULL;
    }
    else {
    del_last = L->Last;
    L->Last = L->Last->lptr;
    free(del_last); //uvolnenie pamati
    L->Last->rptr = NULL;
    }

return;
}

void DLPostDelete (tDLList *L) {
/*
** Zruší prvek seznamu L za aktivním prvkem.
** Pokud je seznam L neaktivní nebo pokud je aktivní prvek
** posledním prvkem seznamu, nic se neděje.
**/
    tDLElemPtr hlp;
    hlp = NULL;

    if((L->Act == NULL) || (L->Act->rptr == NULL)){ //ak zoznam nie je aktivny alebo posledny prvok je aktivny tak sa nic nedeje
        return;
    }

    if(L->Act->rptr->rptr == NULL){ //v pripade ze sme na konci zoznamu
        hlp = L->Last;
        L->Last = L->Act;
		L->Last->rptr = NULL;
        free(hlp);
    }
    else {
    hlp = L->Act->rptr; //ulozenie odkazu na dalsi prvok
    L->Act->rptr = L->Act->rptr->rptr; //zmena odkazu na dalsi prvok o dve miesta
	L->Act->rptr->lptr = L->Act; 
    free(hlp); //uvolnenie pamate
    }

return;
}

void DLPreDelete (tDLList *L) {
/*
** Zruší prvek před aktivním prvkem seznamu L .
** Pokud je seznam L neaktivní nebo pokud je aktivní prvek
** prvním prvkem seznamu, nic se neděje.
**/
    tDLElemPtr hlp;
    hlp = NULL;

    if((L->Act == NULL) || (L->Act == L->First)){ //ak zoznam nie je aktivny alebo prvy prvok je aktivny tak sa nic nedeje
        return;
    }

    if(L->Act->lptr->lptr == NULL){ //pripad ak sme na zaciatku zoznamu
        hlp = L->First;
        L->First = L->Act;
        free(hlp);
        L->First->lptr = NULL;
    }
    else {
    hlp = L->Act->lptr; //ulozenie odkazu na predchadzajuci prvok
    L->Act->lptr = L->Act->lptr->lptr; //zmena odkazu na predchadzajuci prvok o dve miesta
	L->Act->lptr->rptr = L->Act; 
    free(hlp); //uvolnenie pamate
    }

return;
}

void DLPostInsert (tDLList *L, int val) {
/*
** Vloží prvek za aktivní prvek seznamu L.
** Pokud nebyl seznam L aktivní, nic se neděje.
** V případě, že není dostatek paměti pro nový prvek při operaci malloc,
** volá funkci DLError().
**/
	tDLElemPtr new_item;
	new_item = NULL;

    if(L->Act == NULL) {
        return; //zoznam nie je aktivny nic sa nedeje
    }

    if((new_item = malloc(sizeof(struct tDLElem))) == NULL){ //alokacia miesta a kontrola jej uspesnosti pre prvok zoznamu
        DLError();
		return;
    }
	
	if(L->Act->rptr == NULL){ //ak vkladame na koniec
		new_item->lptr = L->Act;
		new_item->rptr = NULL;
		L->Last = new_item;
	}
	else { //nevkladame na koniec
		new_item->rptr = L->Act->rptr;
		new_item->lptr = L->Act;
		L->Act->rptr->lptr = new_item;
	}
	
    new_item->data = val;
    L->Act->rptr = new_item;

return;
}

void DLPreInsert (tDLList *L, int val) {
/*
** Vloží prvek před aktivní prvek seznamu L.
** Pokud nebyl seznam L aktivní, nic se neděje.
** V případě, že není dostatek paměti pro nový prvek při operaci malloc,
** volá funkci DLError().
**/
	tDLElemPtr new_item;
	new_item = NULL;

    if(L->Act == NULL) {
        return; //zoznam nie je aktivny nic sa nedeje
    }

    if((new_item = malloc(sizeof(struct tDLElem))) == NULL){ //alokacia miesta a kontrola jej uspesnosti pre prvok zoznamu
        DLError();
		return;
    }
	
	if(L->Act->lptr == NULL){ //vkladame na zaciatok
		new_item->rptr = L->Act;
		new_item->lptr = NULL;
		L->First = new_item;
	}
	else{ //nevkladame na zaciatok
		new_item->rptr = L->Act;
		new_item->lptr = L->Act->lptr;
		L->Act->lptr->rptr = new_item;
	}

    new_item->data = val;
    L->Act->lptr = new_item;

return;
}

void DLCopy (tDLList *L, int *val) {
/*
** Prostřednictvím parametru val vrátí hodnotu aktivního prvku seznamu L.
** Pokud seznam L není aktivní, volá funkci DLError ().
**/
	if(L->Act == NULL){ //neaktivny zoznam
		DLError();
		return;
	}
	else{
		*val = L->Act->data;
	}

return;
}

void DLActualize (tDLList *L, int val) {
/*
** Přepíše obsah aktivního prvku seznamu L.
** Pokud seznam L není aktivní, nedělá nic.
**/
	if(L->Act == NULL){ //neaktivny zoznam tak sa nic nedeje
		return;
	}
	else{
		L->Act->data = val;
	}

return;
}

void DLSucc (tDLList *L) {
/*
** Posune aktivitu na následující prvek seznamu L.
** Není-li seznam aktivní, nedělá nic.
** Všimněte si, že při aktivitě na posledním prvku se seznam stane neaktivním.
**/
	
	if(L->Act == NULL){ //neaktivny zoznam tak sa nic nedeje
		return;
	}
	else{
		L->Act = L->Act->rptr; //ak to je posledny prvok tak sa nam z toho stane neaktivny zoznam
	}

return;
}


void DLPred (tDLList *L) {
/*
** Posune aktivitu na předchozí prvek seznamu L.
** Není-li seznam aktivní, nedělá nic.
** Všimněte si, že při aktivitě na prvním prvku se seznam stane neaktivním.
**/
	
	
	if(L == NULL || L->Act == NULL){
		return;
	}

	L->Act = L->Act->lptr; //ak je to prvy prvok tak sa stane neaktivny zoznam

return;
}

int DLActive (tDLList *L) {
/*
** Je-li seznam L aktivní, vrací nenulovou hodnotu, jinak vrací 0.
** Funkci je vhodné implementovat jedním příkazem return.
**/
	
	
	return((L->Act != NULL) ? TRUE : FALSE);
}

/* Konec c206.c*/
