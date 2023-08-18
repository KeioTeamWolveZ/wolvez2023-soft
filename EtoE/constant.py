#Last Update 2023/07/12
#Author : Masato Inoue

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
const.SEPARATION_PARA = 24
const.SEPARATION_MOD1 = 25
const.SEPARATION_MOD2 = 17

# Flight Pin
const.FLIGHTPIN_PIN = 4

## Variables
# Goal information
const.GPS_GOAL_LAT = 40.142614  # 南緯は負の値で与える
const.GPS_GOAL_LON = 139.987489 # 西経は負の値で与える
const.GOAL_DISTANCE_THRE = 0.0005 # [km] (50 [cm])
const.f1 = 1 # 136
const.f2 = 50 # 196
const.f3 = 776

# Motor VREF
const.LANDING_MOTOR_VREF = 90
const.RELEASING_MOTOR_VREF = 50
const.RUNNING_MOTOR_VREF = 100
const.STUCK_MOTOR_VREF = 100

# State Threshold
const.PREPARING_GPS_COUNT_THRE= 30
const.PREPARING_TIME_THRE = 10

const.FLYING_FLIGHTPIN_COUNT_THRE = 10

const.DROPPING_ACC_COUNT_THRE = 30
const.DROPPING_ACC_THRE = 1 #加速度の値

const.SEPARATION_TIME_THRE = 10 #焼き切り時間
const.ARM_CARIBRATION_THRE = 5 #アームのマーカーが認識できるまで繰り返す時間
const.LANDING_MOTOR_TIME_THRE = 10 #分離シートから離れるためにモータを回転させる時間
const.RELEASING_MOTOR_TIME_THRE = 0.7 #放出と放出の間にモータを回転させる時間
const.TURNING_MOTOR_TIME_THRE = 1.5 #turning time after the end of second-releasing
const.MODULE_SEPARATION_TIME_THRE = 30 # モジュール同士の接続の際の焼き切り時間

const.ARM_CALIB_POSITION = 0

const.AVOID_COLOR_THRE = 20 #色認識されなかった合計回数の閾値

const.CONNECTED_HEIGHT_THRE = 700 #アームを上げた場合に接続できていることを確認する時の色の高さの閾値

const.EARTH_RADIUS = 6378.137 # [km]

# Stack
const.STUCK_ACC_THRE = 0.5
const.STUCK_COUNT_THRE = 30
const.MIRRER_COUNT_THRE = 10
const.VANISH_BY_STUCK_THRE = 240 # ステート6で長時間何も見えなかった場合
