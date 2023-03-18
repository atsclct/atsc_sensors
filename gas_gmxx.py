'''
  @brief  implementation of underlying methods
  @copyright 
  @license 
  @author Chuntao Liu (chuntao.liu@tamucc.edu)
  @version V1.0
  @date 2023-03-06
'''
import time
import struct

class GAS_GMXXX:
    GM_102B = 0x01
    GM_302B = 0x03
    GM_502B = 0x05
    GM_702B = 0x07
    CHANGE_I2C_ADDR = 0x55
    WARMING_UP = 0xFE
    WARMING_DOWN = 0xFF
    GM_VERF = 3.3
    GM_RESOLUTION = 1023
    # GM102B (NO2)
    # Rs means resistance of sensor in 2ppm NO2 under different temp. and humidity.
    # Rso means resistance of the sensor in 2ppm NO2 under 20°C/55%RH.
    gm102b_rh_offset = [ 
      [ -10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0 ],  #// °C
      [ 1.71, 1.58, 1.45, 1.39, 1.12, 1.00, 0.89 ],  #// Rs/R0 @ 30%RH
      [ 1.49, 1.32, 1.28, 1.08, 0.99, 0.88, 0.71 ],  #// Rs/R0 @ 60%RH
      [ 1.28, 1.15, 10.9, 0.90, 0.86, 0.71, 0.68 ] ]  #// Rs/R0 @ 85%RH
    gm102b_u2gas= [ 
      [ 0.0, 0.21, 0.39, 0.7, 0.95, 1.15, 1.35, 1.45, 1.6, 1.69, 1.79, 1.81 ],  # // V
      [ 0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0 ]] #// NO2 [ppm]
    # GM302B (Ethanol=C2H5OH)
    # Rs means resistance of sensor in 50ppm ethanol under different temp. and humidity.
    # Rso means resistance of the sensor in 50ppm ethanol under 20°C/65%RH.
    gm302b_rh_offset = [ 
      [ -10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0 ],   #// °C
      [ 1.71, 1.61, 1.58, 1.50, 1.42, 1.30, 1.25, 1.18, 1.15, 1.12, 1.00, 0.92, 0.88 ],  #// Rs/R0 @ 30%RH
      [ 1.45, 1.36, 1.33, 1.28, 1.20, 1.11, 1.08, 1.00, 0.98, 0.95, 0.85, 0.79, 0.73 ],  #// Rs/R0 @ 60%RH
      [ 1.27, 1.20, 1.18, 1.10, 1.05, 0.95, 0.92, 0.88, 0.86, 0.81, 0.72, 0.69, 0.64 ]]   #// Rs/R0 @ 85%RH
    gm302b_u2gas = [ 
      [ 1.25, 1.5, 2.0, 2.25, 2.5, 3.1, 3.3, 3.6, 3.7, 3.8, 3.85 ],       #// Alcohol/Ethanol [V]
      [ 0.0, 1.0, 3.5, 5.0, 10.0, 30.0, 50.0, 80.0, 100.0, 200.0, 500.0 ]] # // VOC [ppm]
    # GM502B (VOC)
    # Rs means resistance of sensor in 150ppm CO gas under different temp. and humidity.
    # Rso means resistance of the sensor in 150ppm CO gas under 20°C/55%RH.
    gm502b_rh_offset= [ 
      [ -10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0 ],   # // °C
      [ 1.71, 1.62, 1.54, 1.50, 1.42, 1.30, 1.25, 1.16, 1.14, 1.11, 1.00, 0.92, 0.88 ],  # // Rs/R0 @ 30%RH
      [ 1.45, 1.38, 1.35, 1.28, 1.21, 1.11, 1.08, 1.00, 0.98, 0.96, 0.85, 0.79, 0.75 ],  # // Rs/R0 @ 60%RH
      [ 1.25, 1.20, 1.18, 1.10, 1.05, 0.95, 0.92, 0.88, 0.86, 0.81, 0.73, 0.68, 0.62 ]]   # // Rs/R0 @ 85%RH
    gm502b_u2gas = [ 
      [ 2.52, 2.90, 3.20, 3.40, 3.60, 3.90, 4.05, 4.15, 4.20 ],  #// Alcohol [V]
      [ 0.0, 1.0, 3.5, 5.0, 10.0, 30.0, 50.0, 80.0, 100.0 ]]      #// VOC [ppm]
    # GM702B (CO)
    # Rs means resistance of sensor in 150ppm CO gas under different temp. and humidity.
    # Rso means resistance of the sensor in 150ppm CO gas under 20°C/55%RH
    gm702b_rh_offset = [ 
      [ -10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0 ],  #// °C
      [ 1.71, 1.58, 1.45, 1.38, 1.13, 1.01, 0.88 ],  #// Rs/R0 @ 30%RH
      [ 1.47, 1.32, 1.28, 1.08, 0.98, 0.88, 0.72 ],  #// Rs/R0 @ 60%RH
      [ 1.28, 1.15, 1.08, 0.90, 0.87, 0.71, 0.68 ]]  #// Rs/R0 @ 85%RH
    gm702b_u2gas = [
      [ 0.25, 0.65, 0.98, 1.35, 1.8, 1.98, 2.1, 2.38, 2.42 ],  #// V
      [ 0.0, 5.0, 10.0, 20.0, 50.0, 100.0, 160.0, 500.0, 1000.0 ]]  #// CO [ppm]

    def __init__(self, bus, address):
        self.bus = bus
        #time.sleep(1)
        self.address = address
        self.is_preheated = False

    def write_byte(self, addr, cmd):
            #try:
                self.bus.writeto_mem(self.address, addr, cmd)
                return
            #except:
                print('writing error, check connection')

    def read_32(self,addr):
        while True:
            #try:
                data = self.bus.readfrom_mem(self.address, addr, 4)
                #print(data)
                newdata=(data[3]<<24)+(data[2]<<16)+(data[1]<<8)+data[0]
                #newdata=struct.unpack('>I', bytes(newdata))[0]
                return newdata
            #except:
                print('reading error, check connection')

    def preheat(self):
        self.write_byte(GAS_GMXXX.WARMING_UP,bytearray([0x01]))
        self.is_preheated = True

    def un_preheat(self):
        self.write_byte(GAS_GMXXX.WARMING_DOWN,bytearray([0x01]))
        self.is_preheated = False

    def get_gm102b(self):
        if not self.is_preheated:
            self.preheat()
        #self.write_byte(GAS_GMXXX.GM_102B,[0x01])
        return self.read_32(GAS_GMXXX.GM_102B)

    def get_gm302b(self):
        if not self.is_preheated:
            self.preheat()
        #self.write_byte(GAS_GMXXX.GM_302B,[0x01])
        return self.read_32(GAS_GMXXX.GM_302B)

    def get_gm502b(self):
        if not self.is_preheated:
            self.preheat()
        #self.write_byte(GAS_GMXXX.GM_502B,[0x01])
        return self.read_32(GAS_GMXXX.GM_502B)

    def get_gm702b(self):
        if not self.is_preheated:
            self.preheat()
        #self.write_byte(GAS_GMXXX.GM_702B,[0x01])
        return self.read_32(GAS_GMXXX.GM_702B)

    def change_address(self, new_address):
        self.write_byte(GAS_GMXXX.CHANGE_I2C_ADDR,bytearray([new_address]))
        self.address = new_address

    def calc_vol(self, adc):
        return adc * self.GM_VERF / (self.GM_RESOLUTION * 1.0)
    

    def u_corr_rh( u,  temp,  humidity,  u_corr, size):
      if (humidity <= 30.0):
        hum_idx1 = u_corr[1]
        hum_idx2 = u_corr[1]
        ref_hum1 = 30.0
        ref_hum1 = 60.0
      elif (humidity <= 60.0):
        hum_idx1 = u_corr[1]
        hum_idx2 = u_corr[2]
        ref_hum1 = 30.0
        ref_hum2 = 60.0
      elif (humidity <= 85.0):
        hum_idx1 = u_corr[2]
        hum_idx2 = u_corr[3]
        ref_hum1 = 60.0
        ref_hum2 = 85.0
      else:
        hum_idx1 = u_corr[3]
        hum_idx2 = u_corr[3]
        ref_hum1 = 60.0
        ref_hum2 = 85.0
      old_rsr01 = hum_idx1[0]
      old_rsr02 = hum_idx2[0]
      old_temp = u_corr[0][0]
      if (temp >= old_temp): 
        for  i in range(size):
          new_temp = u_corr[0][i]
          rsr01 = hum_idx1[i]
          rsr02 = hum_idx2[i]
          #//Serial.println("*i=" + String(i) + "  old_temp=" + String(old_temp, 2) + "  new_temp=" + String(new_temp, 2) + "  rsr01=" + String(rsr01, 2) + "  rsr02=" + String(rsr02, 2));
          if (temp <= new_temp):
            #Serial.println("-- " + String(temp - old_temp, 2) + "  " + String(new_temp - old_temp, 2) + "  " + String(rsr01 - old_rsr01, 2) + "  " + String(rsr02 - old_rsr02, 2));
            old_rsr01 += (temp - old_temp) / (new_temp - old_temp) * (rsr01 - old_rsr01);
            old_rsr02 += (temp - old_temp) / (new_temp - old_temp) * (rsr02 - old_rsr02);
            break;
          old_temp = new_temp;
          old_rsr01 = rsr01
          old_rsr02 = rsr02
      
      fact = (old_rsr01 + (humidity - ref_hum1) / (ref_hum2 - ref_hum1) * (old_rsr02 - old_rsr01))
      #//Serial.println("old_rsr01=" + String(old_rsr01, 2) + "  old_rsr02=" + String(old_rsr02, 2) + "  ref_hum1=" + String(ref_hum1, 2) + "  ref_hum2=" + String(ref_hum2, 2));
      #//Serial.println("fact=" + String(fact));
      return u / fact

    def u2ppm(u, u2gas, size): 
      old_ppm = u2gas[1][0]
      old_u = u2gas[0][0]
      if (u <= old_u):
        return old_ppm
      for i in range(size):
        new_u = u2gas[0][i]
        ppm = u2gas[1][i]
        #//Serial.println("i=" + String(i) + "  new_u=" + String(new_u, 2) + "  ppm=" + String(ppm, 2));
        if u <= new_u: 
          #//Serial.println("++ " + String(u - old_u, 2) + "  " + String(new_u - old_u, 2) + "  " + String(ppm - old_ppm, 2));
          return old_ppm + (u - old_u) / (new_u - old_u) * (ppm - old_ppm)
        old_u = new_u
        old_ppm = ppm
      return old_ppm

    def getNO2ppm(temp, humidity):
      no2_u = self.calc_vol(self.get_gm102b())
      no2_corr = u_corr_rh(no2_u, temp, humidity, self.gm102b_rh_offset, 7)
      return u2ppm(no2_corr, self.gm102b_u2gas, 12)

    def getC2H5OHppm(temp, humidity):
      c2h5oh_u = self.calc_vol(self.get_gm302b())
      c2h5oh_corr = u_corr_rh(c2h5oh_u, temp, humidity, self.gm302b_rh_offset, 13)
      return u2ppm(c2h5oh_corr, self.gm302b_u2gas, 11)

    def getVOCppm(temp, humidity):
      voc_u = self.calc_vol(self.get_gm502b())
      voc_corr = u_corr_rh(voc_u, temp, humidity, self.gm502b_rh_offset, 13)
      return u2ppm(voc_corr, self.gm502b_u2gas, 9)

    def getCOppm(temp, humidity):
      co_u = self.calc_vol(get_gm702b())
      co_corr = u_corr_rh(co_u, temp, humidity, self.gm702b_rh_offset, 7)
      return u2ppm(co_corr, self.gm702b_u2gas, 9)
    
