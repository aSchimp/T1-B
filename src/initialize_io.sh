#!/bin/bash
shopt -s extglob

cd /sys/devices/bone_capemgr.*

# serial port for LIDAR
echo BB-UART2 > slots

# i2c bus for IMU - note that this is for the i2c1 pins (17 and 18, or 24 and 26) but the device file name will actually be the i2c-2 one
echo BB-I2C1 > slots

# PWM pin for LIDAR motor
echo am33xx_pwm > slots
echo bone_pwm_P9_14 > slots

# PWM pin for left drive motor
echo bone_pwm_P8_45 > slots

# PWM pin for right drive motor
echo bone_pwm_P9_29 > slots

# sleep for a bit to allow time for the pwm slots to be set up
sleep 1s

# set baud rate for LIDAR serial port
stty -F /dev/ttyO2 115200

# ensure lidar pwm is off
cd /sys/devices/ocp.*/pwm_test_P9_14.*
echo 0 > run

# ensure drive motors are off
cd /sys/devices/ocp.*/pwm_test_P8_45.*
echo 0 > run
cd /sys/devices/ocp.*/pwm_test_P9_29.*
echo 0 > run

# gpio pins for drive motors

# P8_41
cd /sys/class/gpio
echo 74 > export
cd gpio74
echo out > direction
echo 0 > value

# P8_42
cd /sys/class/gpio
echo 75 > export
cd gpio75
echo out > direction
echo 0 > value

# P8_43
cd /sys/class/gpio
echo 72 > export
cd gpio72
echo out > direction
echo 0 > value

# P8_44
cd /sys/class/gpio
echo 73 > export
cd gpio73
echo out > direction
echo 0 > value

# gpio pins for drive motor optical encoder input

# P8_39 - left encoder
cd /sys/class/gpio
echo 76 > export
cd gpio76
echo in > direction

# P8_40 - right encoder
cd /sys/class/gpio
echo 77 > export
cd gpio77
echo in > direction

# gpio pins for infrared proximity sensors

# P8_36 - front sensor
cd /sys/class/gpio
echo 80 > export
cd gpio80
echo in > direction

# P8_37 - left sensor
cd /sys/class/gpio
echo 78 > export
cd gpio78
echo in > direction

# P8_38 - right sensor
cd /sys/class/gpio
echo 79 > export
cd gpio79
echo in > direction

# P8_35 - rear sensor
cd /sys/class/gpio
echo 8 > export
cd gpio8
echo in > direction
