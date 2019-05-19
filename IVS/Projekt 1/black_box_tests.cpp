//======== Copyright (c) 2017, FIT VUT Brno, All rights reserved. ============//
//
// Purpose:     Red-Black Tree - public interface tests
//
// $NoKeywords: $ivs_project_1 $black_box_tests.cpp
// $Author:     IVAN EŠTVAN <xestva00@stud.fit.vutbr.cz>
// $Date:       $2017-03-06
//============================================================================//
/**
 * @file black_box_tests.cpp
 * @author IVAN EŠTVAN
 * 
 * @brief Implementace testu binarniho stromu.
 */

#include <vector>

#include "gtest/gtest.h"

#include "red_black_tree.h"

//============================================================================//
// ** ZDE DOPLNTE TESTY **
//
// Zde doplnte testy Red-Black Tree, testujte nasledujici:
// 1. Verejne rozhrani stromu
//    - InsertNode/DeleteNode a FindNode
//    - Chovani techto metod testuje pro prazdny i neprazdny strom.
// 2. Axiomy (tedy vzdy platne vlastnosti) Red-Black Tree:
//    - Vsechny listove uzly stromu jsou *VZDY* cerne.
//    - Kazdy cerveny uzel muze mit *POUZE* cerne potomky.
//    - Vsechny cesty od kazdeho listoveho uzlu ke koreni stromu obsahuji
//      *STEJNY* pocet cernych uzlu.
//============================================================================//

class EmptyBinaryT : public ::testing::Test{
protected:
	BinaryTree *tree;
	virtual void SetUp(){
		tree = new BinaryTree();
	}
	virtual void TearDown(){
		delete tree;
	}
		
};

class NotEmptyBinaryT : public ::testing::Test{
protected:
	BinaryTree *tree2;
	virtual void SetUp(){
		tree2 = new BinaryTree();
		tree2->InsertNode(5);
		tree2->InsertNode(9);
		tree2->InsertNode(13);
		tree2->InsertNode(17);
		tree2->InsertNode(21);
	}
	virtual void TearDown(){
		delete tree2;
	}
};

// Test 1 - vlozenie do prazdneho stromu
TEST_F(EmptyBinaryT, InsertNode){
	int key = 5;
	EXPECT_NO_THROW(tree->InsertNode(key));
}

// Test 2 - Zrusenie v prazdnom strome
TEST_F(EmptyBinaryT, DeleteNode){
	int key = 5;
	EXPECT_FALSE(tree->DeleteNode(key));
	EXPECT_NO_THROW(tree->DeleteNode(key));
}

// Test 3 - Hladanie v prazdnom strome
TEST_F(EmptyBinaryT, FindNode){
	int key = 5;
	EXPECT_NO_THROW(tree->FindNode(key));
	BinaryTree::Node_t *temp = NULL;
	EXPECT_EQ(tree->FindNode(key),temp);
}

// Test 4 - vlozenie a overenie pri prazdnom zozname
TEST_F(EmptyBinaryT, InsertNodeAdv){
	int key = 5;
	EXPECT_NO_THROW(tree->InsertNode(key));
	bool first = tree->InsertNode(key).first;
	BinaryTree::Node_t *second = tree->InsertNode(key).second;
	EXPECT_FALSE(first);
	EXPECT_EQ(second->key, key);

}

// Test 5 - vlozenie do prazdneho, test prveho vlozenia

TEST_F(EmptyBinaryT, InsertNodeBas){
	int key = 5;
	EXPECT_TRUE(tree->InsertNode(key).first);
}

//-----------------------------------------------------------

// Test 7 - vlozenie do neprazdneho stromu

TEST_F(NotEmptyBinaryT, InsertNodeBas1){
	int key = 6;
	EXPECT_TRUE(tree2->InsertNode(key).first);
}

// Test 8 - vlozenie do neprazdneho stromu uz existujuci prvok

TEST_F(NotEmptyBinaryT, InsertNodeBas2){
	int key = 5;
	EXPECT_FALSE(tree2->InsertNode(key).first);
}

// Test 9 - vlozenie do neprazdneho stromu

TEST_F(NotEmptyBinaryT, InsertNodeAdv){
	int key = 6;
	EXPECT_NO_THROW(tree2->InsertNode(key));
	bool first = tree2->InsertNode(key).first;
	BinaryTree::Node_t *second = tree2->InsertNode(key).second;
	EXPECT_FALSE(first);
	EXPECT_EQ(second->key, key);
}

// Test 10 - odstranenie z neprazdneho, neexistujuci

TEST_F(NotEmptyBinaryT, DeleteNodeBas1){
	int key = 6;
	EXPECT_FALSE(tree2->DeleteNode(key));
}

// Test 11 - odstranenei z neprazdneho , existujuci

TEST_F(NotEmptyBinaryT, DeleteNodeBas2){
	int key = 9;
	EXPECT_TRUE(tree2->DeleteNode(key));
}

// Test 12 - hladanie v neprazdnom, neexistujuci

TEST_F(NotEmptyBinaryT, FindNodeBas1){
	int key = 6;
	BinaryTree::Node_t *temp = NULL;
	EXPECT_EQ(tree2->FindNode(key), temp);
}

// Test 13 - hladanie v neprazdnom, existujuci

TEST_F(NotEmptyBinaryT, FindNodeBas2){
	int key = 13;
	EXPECT_EQ(tree2->FindNode(key)->key, key);
}

//-----------------------------------------------------

// Test 14 - listove uzly su cierne

TEST_F(NotEmptyBinaryT, GetLeafNodes){
	std::vector<BinaryTree::Node_t *> outLeafNodes;
	tree2->GetLeafNodes(outLeafNodes);
	BinaryTree::Color_t color = BinaryTree::BLACK;
	EXPECT_GT(outLeafNodes.size(),0);
	for (int i = 0; i < outLeafNodes.size(); i++){
		EXPECT_EQ(color, outLeafNodes.at(i)->color);
	}

}

// Test 15 - overenie cervenych uzlov

TEST_F(NotEmptyBinaryT, RedNodes){
	std::vector<BinaryTree::Node_t *> outNonLeafNodes;
	tree2->GetNonLeafNodes(outNonLeafNodes);
	EXPECT_GT(outNonLeafNodes.size(),0);
	BinaryTree::Color_t colorR = BinaryTree::RED;
	BinaryTree::Color_t colorB = BinaryTree::BLACK;
	
	for (int i = 0; i < outNonLeafNodes.size(); i++){
		if (outNonLeafNodes.at(i)->color == colorR){
			EXPECT_EQ(outNonLeafNodes.at(i)->pLeft->color, colorB);
			EXPECT_EQ(outNonLeafNodes.at(i)->pRight->color, colorB);
		}

	}



}
























/*** Konec souboru black_box_tests.cpp ***/
