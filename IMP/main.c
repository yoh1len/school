// Ivan Eštva, xestva00, original
/*
 * The Clear BSD License
 * Copyright (c) 2013 - 2015, Freescale Semiconductor, Inc.
 * Copyright 2016-2017 NXP
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted (subject to the limitations in the disclaimer below) provided
 * that the following conditions are met:
 *
 * o Redistributions of source code must retain the above copyright notice, this list
 *   of conditions and the following disclaimer.
 *
 * o Redistributions in binary form must reproduce the above copyright notice, this
 *   list of conditions and the following disclaimer in the documentation and/or
 *   other materials provided with the distribution.
 *
 * o Neither the name of the copyright holder nor the names of its
 *   contributors may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "MKL27Z644.h"
#include <fsl_gpio.h>
#include <fsl_port.h>
#include "board.h"
#include "pin_mux.h"
#include "clock_config.h"
#include <stdio.h>

static void delay(volatile uint32_t nof) {
  while(nof!=0) {
    __asm("NOP");
    nof--;
  }
}

void PORTB_PORTC_PORTD_PORTE_IRQHandler(void)
{
	int64_t timeout_debounce = 50000;

	delay(timeout_debounce);

	//S1 button
	if (PORTE->PCR[21] & PORT_PCR_ISF_MASK) {
		delay(5000000);

		GPIO_ClearPinsOutput(GPIOB, 1<<0u); //S1_O OFF
		GPIO_ClearPinsOutput(GPIOB, 1<<1u); //S1_G1 OFF
		GPIO_ClearPinsOutput(GPIOA, 1<<1u); //S1_G2 OFF
		GPIO_ClearPinsOutput(GPIOC, 1<<6u); //S3_G1 OFF
		GPIO_ClearPinsOutput(GPIOC, 1<<4u); //S3_O OFF
		GPIO_ClearPinsOutput(GPIOD, 1<<7u); //S2_G2 OFF
		GPIO_ClearPinsOutput(GPIOC, 1<<5u); //S2_O OFF
		GPIO_SetPinsOutput(GPIOA, 1<<2u); //S1_R ON
		GPIO_SetPinsOutput(GPIOA, 1<<5u); //S3_R ON
		GPIO_SetPinsOutput(GPIOC, 1<<7u); //S2_R ON
		delay(5000000);
		GPIO_ClearPinsOutput(GPIOE, 1<<20u); //S1_PR OFF
		GPIO_SetPinsOutput(GPIOC, 1<<0u); //S1_PG ON
		delay(10000000);
		GPIO_SetPinsOutput(GPIOE, 1<<20u); //S1_PR ON
		GPIO_ClearPinsOutput(GPIOC, 1<<0u); //S1_PG OFF

	    PORTE->PCR[21] |=  PORT_PCR_ISF_MASK;
	}//S2 button
	else if (PORTE->PCR[16] & PORT_PCR_ISF_MASK) {
		delay(5000000);

		GPIO_ClearPinsOutput(GPIOD, 1<<6u); //S2_G1 OFF
		GPIO_ClearPinsOutput(GPIOD, 1<<7u); //S2_G2 OFF
		GPIO_ClearPinsOutput(GPIOC, 1<<5u); //S2_O OFF
		GPIO_ClearPinsOutput(GPIOE, 1<<31u); //S3_G2 OFF
		GPIO_ClearPinsOutput(GPIOB, 1<<1u); //S1_G1 OFF
		GPIO_ClearPinsOutput(GPIOB, 1<<0u); //S1_O OFF
		GPIO_SetPinsOutput(GPIOC, 1<<7u); //S2_R ON
		GPIO_SetPinsOutput(GPIOA, 1<<2u); //S1_R ON
		delay(5000000);
		GPIO_ClearPinsOutput(GPIOC, 1<<9u); //S2_PR OFF
		GPIO_SetPinsOutput(GPIOC, 1<<8u); //S2_PG ON
		delay(10000000);
		GPIO_SetPinsOutput(GPIOC, 1<<9u); //S2_PR ON
		GPIO_ClearPinsOutput(GPIOC, 1<<8u); //S2_PG OFF

	    PORTE->PCR[16] |=  PORT_PCR_ISF_MASK;
	}//S3 button
	else if (PORTE->PCR[24] & PORT_PCR_ISF_MASK) {
		delay(5000000);

		GPIO_ClearPinsOutput(GPIOE, 1<<31u); //S3_G2 OFF
		GPIO_ClearPinsOutput(GPIOC, 1<<6u); //S3_G1 OFF
		GPIO_ClearPinsOutput(GPIOD, 1<<6u); //S2_G1 OFF
		GPIO_ClearPinsOutput(GPIOA, 1<<1u); //S1_G2 OFF
		GPIO_ClearPinsOutput(GPIOC, 1<<4u); //S3_O OFF
		GPIO_SetPinsOutput(GPIOA, 1<<5u); //S3_R ON
		delay(5000000);
		GPIO_ClearPinsOutput(GPIOE, 1<<25u); //S3_PR OFF
		GPIO_SetPinsOutput(GPIOA, 1<<12u); //S3_PG ON
		delay(10000000);
		GPIO_SetPinsOutput(GPIOE, 1<<25u); //S3_PR ON
		GPIO_ClearPinsOutput(GPIOA, 1<<12u); //S3_PG OFF

	    PORTE->PCR[24] |=  PORT_PCR_ISF_MASK;
	}
	else{}

    /* Change state of button. */

}

int main(void)
{


	/* Structure for input pit */
	    gpio_pin_config_t button_config = {
	        kGPIO_DigitalInput, 0,
	    };

	  /* Init board hardware. */
	  BOARD_InitPins();
	  BOARD_BootClockRUN();
	  BOARD_InitDebugConsole();
	  /* Add your code here */
	  //S1
	  PORTE->PCR[21] = ( 	PORT_PCR_MUX(0x01) 	|
						PORT_PCR_PE(0x01)	|
						PORT_PCR_PS(0x01)	|
						PORT_PCR_ISF(0x00)	|
						PORT_PCR_IRQC(0x0A)
		);
	//S2
	  PORTE->PCR[16] = ( 	PORT_PCR_MUX(0x01) 	|
						PORT_PCR_PE(0x01)	|
						PORT_PCR_PS(0x01)	|
						PORT_PCR_ISF(0x00)	|
						PORT_PCR_IRQC(0x0A)
		);

	  //S3
	  PORTE->PCR[24] = ( 	PORT_PCR_MUX(0x01) 	|
						PORT_PCR_PE(0x01)	|
						PORT_PCR_PS(0x01)	|
						PORT_PCR_ISF(0x00)	|
						PORT_PCR_IRQC(0x0A)
		);

	  // 31 is IRQ for PORTE
	  NVIC_ClearPendingIRQ(31);

	  NVIC_EnableIRQ(31);
	  //Init button pins as input
	  GPIO_PinInit(GPIOE, 21u, &button_config);
	  GPIO_PinInit(GPIOE, 16u, &button_config);
	  GPIO_PinInit(GPIOE, 24u, &button_config);

	  for(;;) {

		  GPIO_ClearPinsOutput(GPIOC, 1<<4u); //S3_O OFF
		  GPIO_SetPinsOutput(GPIOC, 1<<6u); //S3_G1 ON
		  GPIO_SetPinsOutput(GPIOE, 1<<31u); //S3_G2 ON
		  GPIO_SetPinsOutput(GPIOA, 1<<1u); //S1_G2 ON
		  GPIO_SetPinsOutput(GPIOA, 1<<2u); //S1_R ON
		  GPIO_SetPinsOutput(GPIOC, 1<<7u); //S2_R ON

		  delay(50000000);
		  //TODO BLINKING GREEN
		  GPIO_ClearPinsOutput(GPIOC, 1<<6u); //S3_G1 OFF
		  GPIO_SetPinsOutput(GPIOC, 1<<4u); //S3_O ON

		  delay(10000000);

		  GPIO_ClearPinsOutput(GPIOE, 1<<31u); //S3_G2 OFF
		  GPIO_ClearPinsOutput(GPIOC, 1<<4u); //S3_O OFF
		  GPIO_SetPinsOutput(GPIOA, 1<<5u); //S3_R ON

		  delay(10000000);

		  GPIO_ClearPinsOutput(GPIOA, 1<<2u); //S1_R OFF
		  GPIO_ClearPinsOutput(GPIOC, 1<<7u); //S2_R OFF
		  GPIO_SetPinsOutput(GPIOB, 1<<0u); //S1_O ON
		  GPIO_SetPinsOutput(GPIOC, 1<<5u); //S2_O ON

		  delay(10000000);

		  GPIO_ClearPinsOutput(GPIOB, 1<<0u); //S1_O OFF
		  GPIO_ClearPinsOutput(GPIOC, 1<<5u); //S2_O OFF
		  GPIO_SetPinsOutput(GPIOD, 1<<7u); //S2_G2 ON
		  GPIO_SetPinsOutput(GPIOB, 1<<1u);	//S1_G1 ON

		  delay(50000000);

		  GPIO_ClearPinsOutput(GPIOB, 1<<1u); //S1_G1 OFF
		  GPIO_SetPinsOutput(GPIOB, 1<<0u); //S1_O ON

		  delay(10000000);

		  GPIO_ClearPinsOutput(GPIOB, 1<<0u); //S1_O OFF
		  GPIO_ClearPinsOutput(GPIOA, 1<<1u); //S1_G2 OFF
		  GPIO_SetPinsOutput(GPIOA, 1<<2u); //S1_R ON


		  delay(10000000);

		  GPIO_SetPinsOutput(GPIOD, 1<<6u); //S2_G1 ON
		  GPIO_SetPinsOutput(GPIOE, 1<<31u); //S3_G2 ON

		  delay(50000000);

		  GPIO_ClearPinsOutput(GPIOD, 1<<7u); //S2_G2 OFF
		  GPIO_SetPinsOutput(GPIOC, 1<<5u); //S2_O ON

		  delay(10000000);

		  GPIO_ClearPinsOutput(GPIOC, 1<<5u); //S2_O OFF
		  GPIO_ClearPinsOutput(GPIOD, 1<<6u); //S2_G1 OFF
		  GPIO_SetPinsOutput(GPIOC, 1<<7u); //S2_R ON

		  delay(10000000);

		  GPIO_ClearPinsOutput(GPIOA, 1<<5u); //S3_R OFF
		  GPIO_SetPinsOutput(GPIOC, 1<<4u); //S3_O ON

		  delay(10000000);

	    }

	  for(;;) { /* Infinite loop to avoid leaving the main function */
	    __asm("NOP"); /* something to use as a breakpoint stop while looping */
	  }
}
