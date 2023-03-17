# -*- coding:utf-8 -*-
'''!
  @file get_gas_ppm.py
  @brief Read gas concentration unit(PPM).
  @n step: we must first determine the i2c device address, will dial the code switch A0, A1 (MICS_ADDRESS_0 for [0 0]), (MICS_ADDRESS_1 for [1 0]), (MICS_ADDRESS_2 for [0 1]), (MICS_ADDRESS_3 for [1 1]).
  @n       Then wait for the calibration to succeed.
  @n       The calibration time is approximately three minutes.
  @copyright Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license The MIT License (MIT)
  @author [ZhixinLiu](zhixin.liu@dfrobot.com)
  @version V1.2
  @date 2021-6-18
  @url https://github.com/DFRobot/DFRobot_MICS
'''
import sys
import os
import bme680
import time
sensor = bme680.BME680(i2c_addr=0x77)
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

sys.path.append("../")
from DFRobot_MICS import *
import Ozone

CALIBRATION_TIME = 0x01            # calibration time
I2C_BUS          = 0x01            # default use I2C1
COLLECT_NUMBER   = 20  
ozone = Ozone.DFRobot_Ozone_IIC(I2C_BUS ,Ozone.OZONE_ADDRESS_3)
ozone.set_mode(Ozone.MEASURE_MODE_AUTOMATIC)

'''
   The first  parameter is to select i2c0 or i2c1
   The second parameter is the i2c device address
   The default address for i2c is MICS_ADDRESS_0
     MICS_ADDRESS_0              0x75
     MICS_ADDRESS_1              0x76
     MICS_ADDRESS_2              0x77
     MICS_ADDRESS_3              0x78
'''
mics = DFRobot_MICS_I2C (I2C_BUS ,MICS_ADDRESS_0)

def setup():
  '''
    Gets the power mode of the sensor
    The sensor is in sleep mode when power is on,so it needs to wake up the sensor. 
    The data obtained in sleep mode is wrong
  '''
  if mics.get_power_mode() == SLEEP_MODE:
    mics.wakeup_mode()
    print("wake up sensor success")
  else:
    print("the sensor is wake up mode")

  '''
    Do not touch the sensor probe when preheating the sensor.
    Place the sensor in clean air.
    The default calibration time is 3 minutes.
  '''
  mics.warm_up_time(CALIBRATION_TIME)

def loop():
  '''
    Type of detection gas
    CO       = 0x01  (Carbon Monoxide)
    CH4      = 0x02  (Methane)
    C2H5OH   = 0x03  (Ethanol)
    H2       = 0x06  (Hydrogen)
    NH3      = 0x08  (Ammonia)
    NO2      = 0x0A  (Nitrogen Dioxide)
  '''
  gas_concentration = mics.get_gas_ppm(C2H5OH)
  print("C2H5OH  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(CO)
  print("CO  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(CH4)
  print("CH4  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(C3H8)
  print("C3H8  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(C4H10)
  print("C4H10  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(H2)
  print("H2  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(H2S)
  print("H2S  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(NH3)
  print("NH3  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(NO)
  print("NO  %.1f"%gas_concentration)
  gas_concentration = mics.get_gas_ppm(NO2)
  print("NO2  %.1f"%gas_concentration)
  ozone_concentration = ozone.get_ozone_data(COLLECT_NUMBER)
  print("O3 %d PPB."%ozone_concentration)

  if sensor.get_sensor_data():
        output = "{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH".format(sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)
        if sensor.data.heat_stable:
            print("{0},{1} Ohms".format(output, sensor.data.gas_resistance))
        else:
            print(output)
  time.sleep(2)
  #mics.sleep_mode()

if __name__ == "__main__":
  setup()
  m=0
  while True:
    loop()
    m=m+1
    print(m)
