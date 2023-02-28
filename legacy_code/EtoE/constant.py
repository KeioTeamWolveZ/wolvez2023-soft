#Last Update 2022/07/02
#Author : Toshiki Fukui

import const

## Pin Number
# Motor&Encoder
const.RIGHT_MOTOR_IN1_PIN = 6
const.RIGHT_MOTOR_IN2_PIN = 5
const.RIGHT_MOTOR_VREF_PIN = 13
const.RIGHT_MOTOR_ENCODER_A_PIN = 26
const.RIGHT_MOTOR_ENCODER_B_PIN = 19

const.LEFT_MOTOR_IN1_PIN = 20
const.LEFT_MOTOR_IN2_PIN = 16
const.LEFT_MOTOR_VREF_PIN = 12
const.LEFT_MOTOR_ENCODER_A_PIN = 7
const.LEFT_MOTOR_ENCODER_B_PIN = 8

# LED
const.RED_LED_PIN =  10
const.BLUE_LED_PIN = 9
const.GREEN_LED_PIN = 11

# Separation Pin
const.SEPARATION_PIN = 25

# Flight Pin
const.FLIGHTPIN_PIN = 4

# Motor VREF
const.LANDING_MOTOR_VREF = 90
const.SPM_MOTOR_VREF = 70
const.RUNNING_MOTOR_VREF = 70
const.STUCK_MOTOR_VREF = 100

## Variables
const.GPS_GOAL_LAT = 35.5559391
const.GPS_GOAL_LON = 139.6525889
const.f1 = 1 # 136
const.f2 = 50 # 196
const.f3 = 776
const.SPMSECOND_MIN = -100
const.SPMSECOND_MAX = 100
const.MOVING_AVERAGE = 5


## State Threshold
const.PREPARING_GPS_COUNT_THRE= 30
const.PREPARING_TIME_THRE = 10

const.FLYING_FLIGHTPIN_COUNT_THRE = 10

const.DROPPING_ACC_COUNT_THRE = 30
const.DROPPING_ACC_THRE = 1 #加速度の値

const.SEPARATION_TIME_THRE = 10 #焼き切り時間

const.LANDING_MOTOR_TIME_THRE = 10 #分離シートから離れるためにモータを回転させる時間

const.SPMFIRST_PIC_COUNT = 1

const.PLANNING_RISK_THRE = 200

const.FINISH_DIS_THRE = 1.5

const.STUCK_ACC_THRE = 0.1
const.STUCK_COUNT_THRE = 30
