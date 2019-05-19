//======== Copyright (c) 2017, FIT VUT Brno, All rights reserved. ============//
//
// Purpose:     White Box - Tests suite
//
// $NoKeywords: $ivs_project_1 $white_box_code.cpp
// $Author:     IVAN EŠTVAN <xestva00@stud.fit.vutbr.cz>
// $Date:       $2017-03-06
//============================================================================//
/**
 * @file white_box_tests.cpp
 * @author IVAN EŠTVAN
 * 
 * @brief Implementace testu prace s maticemi.
 */

#include "gtest/gtest.h"
#include "white_box_code.h"

//============================================================================//
// ** ZDE DOPLNTE TESTY **
//
// Zde doplnte testy operaci nad maticemi. Cilem testovani je:
// 1. Dosahnout maximalniho pokryti kodu (white_box_code.cpp) testy.
// 2. Overit spravne chovani operaci nad maticemi v zavislosti na rozmerech 
//    matic.
//============================================================================//

class TestMatrixZero1x1 : public ::testing::Test {
protected:
	Matrix *matrix;

	virtual void SetUp() {
		matrix = new Matrix();
	}
	virtual void TearDown() {
		delete matrix;
	}
};

class TestMatrixZeroRxC : public ::testing::Test {
protected:
	Matrix *matrix;

	virtual void SetUp() {
		matrix = new Matrix(3, 2);
	}
	virtual void TearDown() {
		delete matrix;
	}
};

class TestMatrixAdv : public ::testing::Test {
protected:
	Matrix *matrix3x2_1;
	Matrix *matrix3x2_2;
	Matrix *matrix3x2_3;
	Matrix *matrix3x3_1;
	Matrix *matrix2x3_1;

	virtual void SetUp() {
		matrix3x2_1 = new Matrix(3, 2);
		matrix3x2_2 = new Matrix(3, 2);
		matrix3x2_3 = new Matrix(3, 2);
		matrix2x3_1 = new Matrix(2, 3);
		matrix3x3_1 = new Matrix(3, 3);
	}
	virtual void TearDown() {
		delete matrix3x2_1;
		delete matrix3x2_2;
		delete matrix3x2_3;
		delete matrix2x3_1;
		delete matrix3x3_1;
	}
};

TEST_F(TestMatrixZero1x1, TestZero1x1) {
	EXPECT_NO_THROW(matrix->get(0, 0));
	EXPECT_EQ(matrix->get(0,0), 0);
}



TEST_F(TestMatrixZeroRxC, TestZeroRxC) {
	for (int r = 0; r < 3; r++) {
		for (int c = 0; c < 2; c++){
		EXPECT_NO_THROW(matrix->get(r, c));
		EXPECT_EQ(matrix->get(r, c), 0);
	}
}
}

TEST_F(TestMatrixZeroRxC, TestSetBas1) {
	EXPECT_TRUE(matrix->set(2, 1, 1));
	EXPECT_EQ(matrix->get(2, 1), 1);
}

TEST_F(TestMatrixZeroRxC, TestSetBas2) {
	EXPECT_FALSE(matrix->set(5, 5, 5));
}

TEST_F(TestMatrixZeroRxC, TestSetAdv1) {
	std::vector<std::vector< double >> values;
	values = std::vector<std::vector< double > >(3, std::vector<double>(2, 5));
	EXPECT_TRUE(matrix->set(values));
}

TEST_F(TestMatrixZeroRxC, TestSetAdv2) {
	std::vector<std::vector< double >> values;
	values = std::vector<std::vector< double > >(1, std::vector<double>(2, 5));
	EXPECT_FALSE(matrix->set(values));
}

TEST_F(TestMatrixZeroRxC, TestGetBas1) {
	EXPECT_ANY_THROW(matrix->get(5, 5));

	//printf("%f \n", matrix->get(5, 5));
}

TEST_F(TestMatrixZeroRxC, TestGetAdv1) {
	std::vector<std::vector< double >> values;
	values = std::vector<std::vector< double > >(3, std::vector<double>(2, 5));
	EXPECT_TRUE(matrix->set(values));
	EXPECT_NO_THROW(matrix->get(2, 1));
	//printf("%f \n", matrix->get(2, 1));
	EXPECT_EQ(matrix->get(2, 1), 5);
}

/*matrix3x2_1 = new Matrix(3, 2);
matrix3x2_2 = new Matrix(3, 2);
matrix3x2_3 = new Matrix(3, 2);
matrix2x3_1 = new Matrix(2, 3);*/

TEST_F(TestMatrixAdv, TestMatrixEqual1) {
	Matrix m = Matrix(3, 2);
	EXPECT_TRUE(matrix3x2_1->operator==(m));
}

TEST_F(TestMatrixAdv, TestMatrixEqual2) {
	Matrix m = Matrix(4, 2);
	EXPECT_ANY_THROW(matrix3x2_1->operator==(m));
}

TEST_F(TestMatrixAdv, TestMatrixEqual3) {
	std::vector<std::vector< double >> values;
	values = std::vector<std::vector< double > >(3, std::vector<double>(2, 5));
	Matrix m = Matrix(3, 2);
	EXPECT_TRUE(matrix3x2_1->set(values));
	EXPECT_FALSE(matrix3x2_1->operator==(m));
}

TEST_F(TestMatrixAdv, TestMatrixEqual4) {
	Matrix m = Matrix(1, 1);
	EXPECT_ANY_THROW(matrix3x2_1->operator==(m));
}

TEST_F(TestMatrixAdv, TestMatrixAdd1) {
	Matrix m = Matrix(3, 2);
	EXPECT_NO_THROW(matrix3x2_1->operator+(m));
}

TEST_F(TestMatrixAdv, TestMatrixAdd2) {
	Matrix m = Matrix(4, 2);
	EXPECT_ANY_THROW(matrix3x2_1->operator+(m));
}

TEST_F(TestMatrixAdv, TestMatrixAdd3) {
	Matrix m = Matrix(1, 1);
	EXPECT_ANY_THROW(matrix3x2_1->operator+(m));
}

TEST_F(TestMatrixAdv, TestMatrixMulM1) {
	Matrix m = Matrix(2, 3);
	EXPECT_NO_THROW(matrix3x2_1->operator*(m));
}

TEST_F(TestMatrixAdv, TestMatrixMulM2) {
	Matrix m = Matrix(3, 3);
	EXPECT_NO_THROW(matrix3x3_1->operator*(m));
}

TEST_F(TestMatrixAdv, TestMatrixMulM3) {
	Matrix m = Matrix(3, 2);
	EXPECT_ANY_THROW(matrix3x2_1->operator*(m));
}




























/*** Konec souboru white_box_tests.cpp ***/
