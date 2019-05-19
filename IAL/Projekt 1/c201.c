
/* c201.c *********************************************************************}
{* Téma: Jednosměrný lineární seznam
**
**                     Návrh a referenční implementace: Petr Přikryl, říjen 1994
**                                          Úpravy: Andrea Němcová listopad 1996
**                                                   Petr Přikryl, listopad 1997
**                                Přepracované zadání: Petr Přikryl, březen 1998
**                                  Přepis do jazyka C: Martin Tuček, říjen 2004
**                                            Úpravy: Bohuslav Křena, říjen 2016
**
** Implementujte abstraktní datový typ jednosměrný lineární seznam.
** Užitečným obsahem prvku seznamu je celé číslo typu int.
** Seznam bude jako datová abstrakce reprezentován proměnnou typu tList.
** Definici konstant a typů naleznete v hlavičkovém souboru c201.h.
** 
** Vaším úkolem je implementovat následující operace, které spolu s výše
** uvedenou datovou částí abstrakce tvoří abstraktní datový typ tList:
**
**      InitList ...... inicializace seznamu před prvním použitím,
**      DisposeList ... zrušení všech prvků seznamu,
**      InsertFirst ... vložení prvku na začátek seznamu,
**      First ......... nastavení aktivity na první prvek,
**      CopyFirst ..... vrací hodnotu prvního prvku,
**      DeleteFirst ... zruší první prvek seznamu,
**      PostDelete .... ruší prvek za aktivním prvkem,
**      PostInsert .... vloží nový prvek za aktivní prvek seznamu,
**      Copy .......... vrací hodnotu aktivního prvku,
**      Actualize ..... přepíše obsah aktivního prvku novou hodnotou,
**      Succ .......... posune aktivitu na další prvek seznamu,
**      Active ........ zjišťuje aktivitu seznamu.
**
** Při implementaci funkcí nevolejte žádnou z funkcí implementovaných v rámci
** tohoto příkladu, není-li u dané funkce explicitně uvedeno něco jiného.
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

#include "c201.h"

int solved;
int errflg;

void Error() {
/*
** Vytiskne upozornění na to, že došlo k chybě.
** Tato funkce bude volána z některých dále implementovaných operací.
**/	
    printf ("*ERROR* The program has performed an illegal operation.\n");
    errflg = TRUE;                      /* globální proměnná -- příznak chyby */
}

void InitList (tList *L) {
/*
** Provede inicializaci seznamu L před jeho prvním použitím (tzn. žádná
** z následujících funkcí nebude volána nad neinicializovaným seznamem).
** Tato inicializace se nikdy nebude provádět nad již inicializovaným
** seznamem, a proto tuto možnost neošetřujte. Vždy předpokládejte,
** že neinicializované proměnné mají nedefinovanou hodnotu.
**/
    L->Act = NULL;
    L->First = NULL;

return;
}

void DisposeList (tList *L) {
/*
** Zruší všechny prvky seznamu L a uvede seznam L do stavu, v jakém se nacházel
** po inicializaci. Veškerá paměť používaná prvky seznamu L bude korektně
** uvolněna voláním operace free.
***/
    tElemPtr hlp;
    hlp = NULL;
   /*
    * Prechod od prveho do posledneho prvku kym ukazatel First nie je NULL.
    */
    while(L->First != NULL){
        L->Act = L->First; //Zmeni aktívny prvok.
        L->First = L->First->ptr; //Posun ukazatela First na nasledujuci prvok
        hlp = L->Act; //Uvolnenie aktívneho prvku.
        free(hlp);
    }
    L->Act = NULL; //Aktivny prvok na stav po inicializacii.

return;
}

void InsertFirst (tList *L, int val) {
/*
** Vloží prvek s hodnotou val na začátek seznamu L.
** V případě, že není dostatek paměti pro nový prvek při operaci malloc,
** volá funkci Error().
**/
    
    tElemPtr new_first;
    new_first = NULL;

    if ((new_first = malloc(sizeof(struct tElem))) == NULL){ //alokacia miesta a kontrola jej uspesnosti pre prvok zoznamu
        Error();
    }
    else {
        //zapis dat a vsunutie na zaciatok zoznamu
        new_first->data = val;
        new_first->ptr = L->First;
        L->First = new_first;
    }

return;
}

void First (tList *L) {
/*
** Nastaví aktivitu seznamu L na jeho první prvek.
** Funkci implementujte jako jediný příkaz, aniž byste testovali,
** zda je seznam L prázdný.
**/
	L->Act = L->First;

return;
}

void CopyFirst (tList *L, int *val) {
/*
** Prostřednictvím parametru val vrátí hodnotu prvního prvku seznamu L.
** Pokud je seznam L prázdný, volá funkci Error().
**/
	if(L->First == NULL){
        Error();
	}
	else {
        *val = L->First->data;
	}

return;
}

void DeleteFirst (tList *L) {
/*
** Zruší první prvek seznamu L a uvolní jím používanou paměť.
** Pokud byl rušený prvek aktivní, aktivita seznamu se ztrácí.
** Pokud byl seznam L prázdný, nic se neděje.
**/
    tElemPtr del_first;
    del_first = NULL;

    if(L->First == NULL){ //ak je zoznam prazdny tak sa nic nedeje
		return;
	}

    if(L->Act == L->First){ //zrusenie aktivity zoznamu
        L->Act = NULL;
    }

    del_first = L->First;
    L->First = L->First->ptr; //uprava ukazatela na novy prvy prvok
    free(del_first); //uvolnenie pamati

return;
}	

void PostDelete (tList *L) {
/* 
** Zruší prvek seznamu L za aktivním prvkem a uvolní jím používanou paměť.
** Pokud není seznam L aktivní nebo pokud je aktivní poslední prvek seznamu L,
** nic se neděje.
**/
    tElemPtr hlp;
    hlp = NULL;

    if ((L->Act == NULL) || (L->Act->ptr == NULL)){ //ak zoznam nie je aktivny alebo posledny prvok je aktivny tak sa nic nedeje
        return;
    }

    hlp = L->Act->ptr; //ulozenie odkazu na dalsi prvok
    L->Act->ptr = L->Act->ptr->ptr; //zmena odkazu na dalsi prvok o dve miesta
    free(hlp); //uvolnenie pamate

return;
}

void PostInsert (tList *L, int val) {
/*
** Vloží prvek s hodnotou val za aktivní prvek seznamu L.
** Pokud nebyl seznam L aktivní, nic se neděje!
** V případě, že není dostatek paměti pro nový prvek při operaci malloc,
** zavolá funkci Error().
**/
	tElemPtr new_item;
	new_item = NULL;

    if (L->Act == NULL) {
        return; //zoznam nie je aktivny nic sa nedeje
    }

    if ((new_item = malloc(sizeof(struct tElem))) == NULL){ //alokacia miesta a kontrola jej uspesnosti pre prvok zoznamu
        Error();
        return;
    }
    new_item->ptr = L->Act->ptr;
    new_item->data = val;
    L->Act->ptr = new_item;
}

void Copy (tList *L, int *val) {
/*
** Prostřednictvím parametru val vrátí hodnotu aktivního prvku seznamu L.
** Pokud seznam není aktivní, zavolá funkci Error().
**/
	
	
	if(L->Act == NULL){ //neaktivny zoznam
		Error();
	}
	else{
		*val = L->Act->data;
	}

return;
}

void Actualize (tList *L, int val) {
/*
** Přepíše data aktivního prvku seznamu L hodnotou val.
** Pokud seznam L není aktivní, nedělá nic!
**/
	if(L->Act == NULL){ //neaktivny zoznam tak sa nic nedeje
		return;
	}
	else{
		L->Act->data = val;
	}

return;
}

void Succ (tList *L) {
/*
** Posune aktivitu na následující prvek seznamu L.
** Všimněte si, že touto operací se může aktivní seznam stát neaktivním.
** Pokud není předaný seznam L aktivní, nedělá funkce nic.
**/
	if(L->Act == NULL){ //neaktivny zoznam tak sa nic nedeje
		return;
	}
	else{
		L->Act = L->Act->ptr; //ak to je posledny prvok tak sa nam z toho stane neaktivny zoznam
	}

return;
}

int Active (tList *L) {		
/*
** Je-li seznam L aktivní, vrací nenulovou hodnotu, jinak vrací 0.
** Tuto funkci je vhodné implementovat jedním příkazem return. 
**/
	
	
	return((L->Act != NULL) ? TRUE : FALSE);
}

/* Konec c201.c */
