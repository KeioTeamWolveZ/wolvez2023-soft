#Last Update 2022/07/02
#Author : Toshiki Fukui

import const

## Pin Number
# Motor
const.RIGHT_MOTOR_IN1_PIN = 6
const.RIGHT_MOTOR_IN2_PIN = 5
const.RIGHT_MOTOR_VREF_PIN = 13

const.LEFT_MOTOR_IN1_PIN = 20
const.LEFT_MOTOR_IN2_PIN = 16
const.LEFT_MOTOR_VREF_PIN = 12

# Servo motor
const.SERVO_PIN = 23

# LED
const.RED_LED_PIN =  10
const.BLUE_LED_PIN = 9
const.GREEN_LED_PIN = 11

# Separation Pin
const.SEPARATION_PIN1 = 24
const.SEPARATION_PIN2 = 25
const.SEPARATION_PIN3 = 8

# Flight Pin
const.FLIGHTPIN_PIN = 4

# Motor VREF
const.LANDING_MOTOR_VREF = 90
const.RUNNING_MOTOR_VREF = 70
const.STUCK_MOTOR_VREF = 100

## Variables
const.GPS_GOAL_LAT = 35.5559391
const.GPS_GOAL_LON = 139.6525889
const.f1 = 1 # 136
const.f2 = 50 # 196
const.f3 = 776


## State Threshold
const.PREPARING_GPS_COUNT_THRE= 30
const.PREPARING_TIME_THRE = 10

const.FLYING_FLIGHTPIN_COUNT_THRE = 10

const.DROPPING_ACC_COUNT_THRE = 30
const.DROPPING_ACC_THRE = 1 #加速度の値

const.SEPARATION_TIME_THRE = 10 #焼き切り時間

const.LANDING_MOTOR_TIME_THRE = 10 #分離シートから離れるためにモータを回転させる時間

const.FINISH_DIS_THRE = 1.5

# Stack
const.STUCK_ACC_THRE = 0.1
const.STUCK_COUNT_THRE = 30
