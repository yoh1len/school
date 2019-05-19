//Ivan Eštva, xestva00, 90%
/*
 * The Clear BSD License
 * Copyright (c) 2016, Freescale Semiconductor, Inc.
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
 * o Neither the name of Freescale Semiconductor, Inc. nor the names of its
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

/* clang-format off */
/*
 * TEXT BELOW IS USED AS SETTING FOR TOOLS *************************************
!!GlobalInfo
product: Pins v3.0
processor: MKL27Z64xxx4
package_id: MKL27Z64VLH4
mcu_data: ksdk2_0
processor_version: 0.0.8
 * BE CAREFUL MODIFYING THIS COMMENT - IT IS YAML SETTINGS FOR TOOLS ***********
 */
/* clang-format on */

#include "fsl_common.h"
#include "fsl_port.h"
#include "pin_mux.h"
#include "fsl_device_registers.h"
#include "fsl_gpio.h"

/* FUNCTION ************************************************************************************************************
 *
 * Function Name : BOARD_InitBootPins
 * Description   : Calls initialization functions.
 *
 * END ****************************************************************************************************************/
void BOARD_InitBootPins(void)
{
    BOARD_InitPins();
}

/* clang-format off */
/*
 * TEXT BELOW IS USED AS SETTING FOR TOOLS *************************************
BOARD_InitPins:
- options: {callFromInitBoot: 'true', coreID: core0, enableClock: 'true'}
- pin_list:
  - {pin_num: '23', peripheral: LPUART0, signal: RX, pin_signal: PTA1/LPUART0_RX/TPM2_CH0}
  - {pin_num: '24', peripheral: LPUART0, signal: TX, pin_signal: PTA2/LPUART0_TX/TPM2_CH1}
 * BE CAREFUL MODIFYING THIS COMMENT - IT IS YAML SETTINGS FOR TOOLS ***********
 */
/* clang-format on */

/* FUNCTION ************************************************************************************************************
 *
 * Function Name : BOARD_InitPins
 * Description   : Configures pin routing and optionally pin electrical features.
 *
 * END ****************************************************************************************************************/

static const gpio_pin_config_t LED_configOutput = {
  kGPIO_DigitalOutput,  /* use as output pin */
  0,  /* initial value */
};

static const gpio_pin_config_t LED_configOutputOn = {
  kGPIO_DigitalOutput,  /* use as output pin */
  1,  /* initial value */
};

void BOARD_InitPins(void)
{
    /* Clock enabled */
    CLOCK_EnableClock(kCLOCK_PortA);
    CLOCK_EnableClock(kCLOCK_PortB);
    CLOCK_EnableClock(kCLOCK_PortC);
    CLOCK_EnableClock(kCLOCK_PortD);
    CLOCK_EnableClock(kCLOCK_PortE);






    PORT_SetPinMux(PORTA, 1u, kPORT_MuxAsGpio); //S1_G2
    PORT_SetPinMux(PORTA, 2u, kPORT_MuxAsGpio); //S1_R
    PORT_SetPinMux(PORTA, 5u, kPORT_MuxAsGpio); //S3_R
    PORT_SetPinMux(PORTA, 12u, kPORT_MuxAsGpio); //S3_PG


    PORT_SetPinMux(PORTB, 1u, kPORT_MuxAsGpio); //S1_G1
    PORT_SetPinMux(PORTB, 0u, kPORT_MuxAsGpio); //S1_O

    PORT_SetPinMux(PORTC, 0u, kPORT_MuxAsGpio); //S1_PG
    PORT_SetPinMux(PORTC, 4u, kPORT_MuxAsGpio); //S3_O
    PORT_SetPinMux(PORTC, 5u, kPORT_MuxAsGpio); //S2_O
    PORT_SetPinMux(PORTC, 6u, kPORT_MuxAsGpio); //S3_G1
    PORT_SetPinMux(PORTC, 7u, kPORT_MuxAsGpio); //S2_R
    PORT_SetPinMux(PORTC, 8u, kPORT_MuxAsGpio); //S2_PG
    PORT_SetPinMux(PORTC, 9u, kPORT_MuxAsGpio); //S2_PR

    PORT_SetPinMux(PORTD, 6u, kPORT_MuxAsGpio); //S2_G1
    PORT_SetPinMux(PORTD, 7u, kPORT_MuxAsGpio); //S2_G2

    PORT_SetPinMux(PORTE, 20u, kPORT_MuxAsGpio); //S1_PR
    PORT_SetPinMux(PORTE, 25u, kPORT_MuxAsGpio); //S3_PR
    PORT_SetPinMux(PORTE, 31u, kPORT_MuxAsGpio); //S3_G2

    GPIO_PinInit(GPIOA, 1u, &LED_configOutput);
    GPIO_PinInit(GPIOA, 2u, &LED_configOutput);
    GPIO_PinInit(GPIOA, 5u, &LED_configOutput);
    GPIO_PinInit(GPIOA, 12u, &LED_configOutput);

    GPIO_PinInit(GPIOB, 1u, &LED_configOutput);
    GPIO_PinInit(GPIOB, 0u, &LED_configOutput);

    GPIO_PinInit(GPIOC, 0u, &LED_configOutput);
    GPIO_PinInit(GPIOC, 4u, &LED_configOutput);
    GPIO_PinInit(GPIOC, 5u, &LED_configOutput);
    GPIO_PinInit(GPIOC, 6u, &LED_configOutput);
    GPIO_PinInit(GPIOC, 7u, &LED_configOutput);
    GPIO_PinInit(GPIOC, 8u, &LED_configOutput);
    GPIO_PinInit(GPIOC, 9u, &LED_configOutputOn);

    GPIO_PinInit(GPIOD, 6u, &LED_configOutput);
    GPIO_PinInit(GPIOD, 7u, &LED_configOutput);

    GPIO_PinInit(GPIOE, 20u, &LED_configOutputOn);
    GPIO_PinInit(GPIOE, 25u, &LED_configOutputOn);
    GPIO_PinInit(GPIOE, 31u, &LED_configOutput);

}
/***********************************************************************************************************************
 * EOF
 **********************************************************************************************************************/
