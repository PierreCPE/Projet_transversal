/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "string.h"
#include "stdio.h"
#include "stdlib.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
uint8_t Rxuint4[1];
char RxChar4[50];
char CharData4[1];
char *ptrRxChar4 = RxChar4;
char *ptrCharData4 = CharData4 ;
int taille4 = 0;

uint8_t Rxuint5[1];
char RxChar5[50];
char CharData5[1];
char *ptrRxChar5 = RxChar5;
char *ptrCharData5 = CharData5 ;
int taille5 = 0;

const char *SepCommandes = ",";
const char *SepValeurs = "&";
const char *Fin = "$";
const char *RetChariot = "\r";
char cmd_id[] = "012345"; // 0 est pour le serializer, 1 pour le servomoteur vertical,
						  // 2 le servomoteur horizontal et 3 la LED
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

void CONTROL_Motor(int cmd[]){
	if (cmd[0] == 0 && cmd[1] == 0){
		char stop[] = "stop\r";
		HAL_UART_Transmit(&huart5,(uint8_t *) stop, strlen(stop), 50 );
	}
	else{
		char buff[sizeof("mogo 1:0 2:0\r")];
		sprintf(buff, "mogo 1:%d 2:%d\r", cmd[0], cmd[1]);
		HAL_UART_Transmit(&huart5,(uint8_t *) buff, strlen(buff), 50);
		memset(buff, 0, sizeof(buff));
	}
}

void CONTROL_Servo_V(int cmd){
	int cmd_buff = cmd*200/18+500;
	__HAL_TIM_SetCompare(&htim1,TIM_CHANNEL_1,cmd_buff);
}

void CONTROL_Servo_H(int cmd){
	int cmd_buff = cmd*200/18+500;
	__HAL_TIM_SetCompare(&htim2,TIM_CHANNEL_1,cmd_buff);
}

void CONTROL_LED(int cmd){
	if (cmd == 1){
		__HAL_TIM_SetCompare(&htim3,TIM_CHANNEL_1,9999);
	}
	else if (cmd == 0){
		__HAL_TIM_SetCompare(&htim3,TIM_CHANNEL_1,0);
	}
}

void SELEC_Commande(char cmd[]){
	char *saveptr1, *saveptr2;
	char *TokenCommandeComplete = strtok_r(cmd, SepCommandes, &saveptr1);
	while (TokenCommandeComplete != NULL){
		if (*TokenCommandeComplete == cmd_id[0]){
			char *TokenCommandeUnique = strtok_r(TokenCommandeComplete, SepValeurs, &saveptr2);
			int buff_int[2];
			int i = 0;
			TokenCommandeUnique = strtok_r(NULL, SepValeurs, &saveptr2);
			while (TokenCommandeUnique != NULL){
				buff_int[i] = atoi(TokenCommandeUnique);//probleme lorsque l'on envoie 2 entier (14.15) et apres (0.0)
				i++;

				TokenCommandeUnique = strtok_r(NULL, SepValeurs, &saveptr2);
			}
			CONTROL_Motor(buff_int);
		}

		else if (*TokenCommandeComplete == cmd_id[1]){
			char *TokenCommandeUnique = strtok_r(TokenCommandeComplete, SepValeurs, &saveptr2);
			TokenCommandeUnique = strtok_r(NULL, SepValeurs, &saveptr2);
			int buff_int = atoi(TokenCommandeUnique);
			CONTROL_Servo_V(buff_int);
		}

		else if (*TokenCommandeComplete == cmd_id[2]){
				char *TokenCommandeUnique = strtok_r(TokenCommandeComplete, SepValeurs, &saveptr2);
				TokenCommandeUnique = strtok_r(NULL, SepValeurs, &saveptr2);
				int buff_int = atoi(TokenCommandeUnique);
				CONTROL_Servo_H(buff_int);
			}

		else if (*TokenCommandeComplete == cmd_id[3]){
				char *TokenCommandeUnique = strtok_r(TokenCommandeComplete, SepValeurs, &saveptr2);
				TokenCommandeUnique = strtok_r(NULL, SepValeurs, &saveptr2);
				int buff_int = atoi(TokenCommandeUnique);
				CONTROL_LED(buff_int);
			}

		else {
			char buffer[sizeof("code_incomplet\r\n")];
			memcpy(buffer, "code_incomplet\r\n", sizeof("code_incomplet\r\n"));
			HAL_UART_Transmit(&huart4,(uint8_t *) buffer ,strlen(buffer) ,50 );
		}
		TokenCommandeComplete = strtok_r(NULL, SepCommandes, &saveptr1);
	}
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
	if (huart->Instance == UART4){
		sprintf(CharData4, "%s", Rxuint4); // on convertit Rxuint4 en char dans CharData
		if (*ptrCharData4 != *Fin){
			*ptrRxChar4 = *ptrCharData4;
			*ptrRxChar4++;
			taille4++;
		}
		else if (*ptrCharData4 == *Fin){
			SELEC_Commande(RxChar4);
			ptrRxChar4 = RxChar4;				// on reinitialise le pointeur de RxChar4
			taille4 = 0;						// on reinitialise le vecteur taille
			memset(RxChar4,0,sizeof(RxChar4));	// on reinitialise le vecteur RxChar4
		}
		HAL_UART_Receive_IT(&huart4,Rxuint4,1); // on reenable le Receive */
	}
	else if (huart->Instance == UART5){
		sprintf(CharData5, "%s", Rxuint5);
		if (*ptrCharData5 != *RetChariot){
			*ptrRxChar5 = *ptrCharData5;
			*ptrRxChar5++;
			taille5++;
		}
		else if (*ptrCharData5 == *RetChariot){
			HAL_UART_Transmit(&huart4,(uint8_t *) RxChar5 ,taille5 ,50);
			ptrRxChar5 = RxChar5;
			taille5 = 0;
		}
		HAL_UART_Receive_IT(&huart5,Rxuint5,1);
	}
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_UART4_Init();
  MX_UART5_Init();
  MX_TIM1_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  /* USER CODE BEGIN 2 */
  HAL_UART_Receive_IT(&huart4, Rxuint4, 1);
  HAL_UART_Receive_IT(&huart5, Rxuint5, 1);

  TIM1->CCR1 = 1300;
  HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
  TIM2->CCR1 = 722;
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
  TIM3->CCR1 = 0;
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL16;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV8;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV8;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_UART4|RCC_PERIPHCLK_UART5
                              |RCC_PERIPHCLK_TIM1;
  PeriphClkInit.Uart4ClockSelection = RCC_UART4CLKSOURCE_PCLK1;
  PeriphClkInit.Uart5ClockSelection = RCC_UART5CLKSOURCE_PCLK1;
  PeriphClkInit.Tim1ClockSelection = RCC_TIM1CLK_HCLK;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
