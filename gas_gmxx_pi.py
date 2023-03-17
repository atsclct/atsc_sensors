'''
  @brief  implementation of underlying methods
  @copyright 
  @license The MIT License (MIT)
  @author Chuntao Liu (chuntao.liu@tamucc.edu)
  @version V1.0
  @date 2023-03-06
'''
import time
import smbus
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

    def __init__(self, bus, address):
        self.bus = smbus.SMBus(bus)
        #time.sleep(1)
        self.address = address
        self.is_preheated = False

    def write_byte(self, addr, cmd):
            try:
                self.bus.write_i2c_block_data(self.address, addr, cmd)
                return
            except:
                print('writing error, check connection')

    def read_32(self,addr):
        while True:
            try:
                data = self.bus.read_i2c_block_data(self.address, addr, 4)
                #print(data)
                newdata=(data[3]<<24)+(data[2]<<16)+(data[1]<<8)+data[0]
                #newdata=struct.unpack('>I', bytes(newdata))[0]
                return newdata
            except:
                print('reading error, check connection')

    def preheat(self):
        self.write_byte(GAS_GMXXX.WARMING_UP,[0x01])
        self.is_preheated = True

    def un_preheat(self):
        self.write_byte(GAS_GMXXX.WARMING_DOWN,[0x01])
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
        self.write_byte(GAS_GMXXX.CHANGE_I2C_ADDR,new_address)
        self.address = new_address

    def calc_vol(self, adc):
        return adc * self.GM_VERF / (self.GM_RESOLUTION * 1.0)