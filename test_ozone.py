# -*- coding:utf-8 -*-
'''!
  @file get_ozone_data.py
  @brief Reading ozone concentration, A concentration of one part per billion (PPB).
  @n step: we must first determine the iic device address, will dial the code switch A0, A1 (OZONE_ADDRESS_0 for [0 0]), (OZONE_ADDRESS_1 for [1 0]), (OZONE_ADDRESS_2 for [0 1]), (OZONE_ADDRESS_3 for [1 1]).
  @n       Then configure the mode of active and passive acquisition, Finally, ozone data can be read.
  @n note: it takes time to stable oxygen concentration, about 3 minutes.
  @copyright Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license The MIT License (MIT)
  @author [ZhixinLiu](zhixin.liu@dfrobot.com)
  @version V1.0
  @date 2020-5-27
  @url https://github.com/DFRobot/DFRobot_Ozone
'''
from machine import I2C
import time
import ozone
i2c1=machine.I2C(1,sda=machine.Pin(18),scl=machine.Pin(19))
i2c1.scan()

COLLECT_NUMBER   = 20              # collect number, the collection range is 1-100

o3 = ozone.DFRobot_Ozone_IIC(i2c1 ,ozone.OZONE_ADDRESS_3)
'''
  The module is configured in automatic mode or passive
    MEASURE_MODE_AUTOMATIC  active  mode
    MEASURE_MODE_PASSIVE    passive mode
''' 
o3.set_mode(ozone.MEASURE_MODE_AUTOMATIC)
while(1):
  ''' Smooth data collection the collection range is 1-100 '''
  ozone_concentration = o3.get_ozone_data(COLLECT_NUMBER)
  print("Ozone concentration is %d PPB."%ozone_concentration)
  time.sleep(1)