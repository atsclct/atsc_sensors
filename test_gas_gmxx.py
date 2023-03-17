# -*- coding:utf-8 -*-
'''!
  @brief Read gas concentration unit(PPM).
  @n step: we must first determine the i2c device address: i2cdetect -y 1 or i2c.scan()
  @copyright
  @license The MIT License (MIT)
  @author Chuntao Liu (chuntao.liu@tamucc.edu)
  @version V1.0
  @date 2023-3-06
'''
from machine import I2C
import time
import gas_gmxx
i2c1=machine.I2C(1,sda=machine.Pin(18),scl=machine.Pin(19))
i2c1.scan()


'''
   The default address for i2c gas_gmxx is 0x08
'''
gas = gas_gmxx.GAS_GMXXX (i2c1 ,0x08)

gas.preheat()
for i in range(2):
    print('heating up '+str(i))
    time.sleep(1)


def loop():
  g_no2 = gas.calc_vol(gas.get_gm102b())
  g_c2h5oh = gas.calc_vol(gas.get_gm302b())
  g_voc = gas.calc_vol(gas.get_gm502b())
  g_co = gas.calc_vol(gas.get_gm702b())
  print("NO2: %.3f"%  g_no2)
  print("C2H5OH: %.3f"%  g_c2h5oh)
  print("VOC: %.3f"%  g_voc)
  print("CO: %.3f"%  g_co)
  time.sleep(1)
  #mics.sleep_mode()

if __name__ == "__main__":
  while True:
    loop()
