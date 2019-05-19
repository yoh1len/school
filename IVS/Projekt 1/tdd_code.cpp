//======== Copyright (c) 2017, FIT VUT Brno, All rights reserved. ============//
//
// Purpose:     Test Driven Development - priority queue code
//
// $NoKeywords: $ivs_project_1 $tdd_code.cpp
// $Author:     IVAN EŠTVAN <xestva00@stud.fit.vutbr.cz>
// $Date:       $2017-03-06
//============================================================================//
/**
 * @file tdd_code.cpp
 * @author IVAN EŠTVAN
 * 
 * @brief Implementace metod tridy prioritni fronty.
 */

#include <stdlib.h>
#include <stdio.h>

#include "tdd_code.h"

//============================================================================//
// ** ZDE DOPLNTE IMPLEMENTACI **
//
// Zde doplnte implementaci verejneho rozhrani prioritni fronty (Priority Queue)
// 1. Verejne rozhrani fronty specifikovane v: tdd_code.h (sekce "public:")
//    - Konstruktor (PriorityQueue()), Destruktor (~PriorityQueue())
//    - Metody Insert/Remove/Find a GetHead
//    - Pripadne vase metody definovane v tdd_code.h (sekce "protected:")
//
// Cilem je dosahnout plne funkcni implementace prioritni fronty implementovane
// pomoci tzv. "double-linked list", ktera bude splnovat dodane testy 
// (tdd_tests.cpp).
//============================================================================//

PriorityQueue::PriorityQueue()
{
	front = NULL;
}

PriorityQueue::~PriorityQueue()
{
	PriorityQueue::Element_t *temp, *prechod;

	if (front == NULL) {
	}
	else {
		prechod = front;

		while (prechod->pNext != NULL) {
			temp = prechod;
			prechod = prechod->pNext;
			temp->pNext->pPrev = NULL;
			free(temp);
		}
		free(prechod);
		front = NULL;
	}
}

void PriorityQueue::Insert(int value)
{
	PriorityQueue::Element_t *temp, *prechod;
	temp = new Element_t;
	prechod = front;
	temp->value = value;
		
	if (front == NULL) {
		temp->pNext = NULL;
		temp->pPrev = NULL;
		front = temp;
	}
	else {
		while (prechod->pNext != NULL && prechod->pNext->value <= temp->value) {
			prechod = prechod->pNext;
		}
		if (temp->value <= prechod->value) {
			temp->pNext = front;
			prechod->pPrev = temp;
			temp->pPrev = NULL;
			front = temp;
		}
		else {
			if (prechod->pNext == NULL) {
				temp->pPrev = prechod;
				temp->pNext = prechod->pNext;
				prechod->pNext = temp;
			}
			else {
				prechod->pNext->pPrev = temp;
				temp->pPrev = prechod;
				temp->pNext = prechod->pNext;
				prechod->pNext = temp;
			}
		}
	}
}

bool PriorityQueue::Remove(int value)
{
	PriorityQueue::Element_t *temp, *prechod;

	if (front == NULL) {
		return false;
	}

	prechod = front;
	
	while (prechod->pNext != NULL) {
		if (prechod->value == value) {
			temp = prechod;
			if (temp == front) {
				temp->pNext->pPrev = NULL;
				front = temp->pNext;
				return true;
			}
			else {
				temp->pPrev->pNext = temp->pNext;
				temp->pNext->pPrev = temp->pPrev;
				free(temp);
				return true;
			}
		}
		else {
			prechod = prechod->pNext;
		}
	}
	if (prechod->pNext == NULL) {
		if (prechod->value == value) {
			temp = prechod;
			if (temp == front) {
				front = NULL;
				free(temp);
				return true;
			}
			else {
				temp->pPrev->pNext = NULL;
				free(temp);
				return true;
			}
		}
		else {
			return false;
		}
	}
	


    return false;
}

PriorityQueue::Element_t *PriorityQueue::Find(int value)
{
	PriorityQueue::Element_t *prechod;

	if (front == NULL) {
		return NULL;
	}

	prechod = front;

	while (prechod->pNext != NULL) {
		if (prechod->value == value) {
			return prechod;
		}
		else {
			prechod = prechod->pNext;
		}
	}
	if (prechod->pNext == NULL) {
		if (prechod->value == value) {
			return prechod;
		}
		else {
			return NULL;
		}
	}
    return NULL;
}

PriorityQueue::Element_t *PriorityQueue::GetHead()
{
	if (front == NULL) {
		return NULL;
	}
	else {
		return front;
	}
}

/*** Konec souboru tdd_code.cpp ***/
