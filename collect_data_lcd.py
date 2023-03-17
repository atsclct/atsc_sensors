from machine import Pin, UART, I2C
from get_gps import *
import sdcard
import uos
import sds011
import utime, time
import bme280
import ozone,sdc4x,gas_gmxx
from ssd1306 import SSD1306_I2C
# Initial
i2c=I2C(0,sda=Pin(20), scl=Pin(21), freq=400000)    #initializing the I2C method 
bme = bme280.BME280(i2c=i2c)
i2c1=machine.I2C(1,sda=machine.Pin(18),scl=machine.Pin(19))
i2c1.scan()
oled = SSD1306_I2C(128, 32, i2c1)
oled.fill(0)
oled.text('starting',8,20)
oled.show()
o3 = ozone.DFRobot_Ozone_IIC(i2c1 ,ozone.OZONE_ADDRESS_3)
o3.set_mode(ozone.MEASURE_MODE_AUTOMATIC)
gas = gas_gmxx.GAS_GMXXX (i2c1 ,0x08)
sd4x = sdc4x.SCD4X(i2c_bus=i2c1,address=0x62)
sd4x.temperature_offset = 5.4
sd4x.altitude = 15
sd4x.self_calibration_enabled = True
sd4x.persist_settings()
sd4x.start_periodic_measurement()
sdc_co2=0. ; sdc_t=0. ; sdc_rh=0.

gpsModule = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
buff = bytearray(255)
gpsdata={'TIMEOUT':False,
         'FIX_STATUS':False,
         'latitude':"",
         'altitude':"",
         'longitude':"",
         'satellites':"",
         'GPStime': ""}
pm25=""
pm10=""
# Assign chip select (CS) pin (and start it high)
cs = Pin(5, Pin.OUT)
led=Pin(25,Pin.OUT)
# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))

# Initialize SD card
sd = sdcard.SDCard(spi, cs)
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")
# Initialize SDS011
uart=UART(1,baudrate=9600,tx=Pin(8),rx=Pin(9),bits=8,stop=1)
dust_sensor=sds011.SDS011(uart)
dust_sensor.sleep()
files=uos.listdir('/sd/')
#print(files)
tic=files[-1].split('_')[1].split('.')[0]
file=open('/sd/data_'+str(int(tic)+1)+'.txt','w')
file.write('\n')
file.close()

while True:
  try:
    oled.fill(0)
    oled.text(bme.values[0],8,0)
    oled.text(bme.values[1],0,10)
    oled.text(bme.values[2],8,20)
    oled.show()
    print('Start fan for 6 seconds.')
    dust_sensor.wake()
    time.sleep(2)
    ozone_concentration = o3.get_ozone_data(20)/1000.
    g_no2 = gas.calc_vol(gas.get_gm102b())
    g_c2h5oh = gas.calc_vol(gas.get_gm302b())
    g_voc = gas.calc_vol(gas.get_gm502b())
    g_co = gas.calc_vol(gas.get_gm702b())
    oled.fill(0)
    oled.text('O3: %.3f'%ozone_concentration,8,0)
    oled.text('NO2:%.3f'%g_no2,0,10)
    if sd4x.data_ready:
        sdc_co2=sd4x.CO2
        sdc_t=sd4x.temperature
        sdc_rh=sd4x.relative_humidity
        oled.text('CO2:%dppmv'%sdc_co2,8,20)
    oled.show()
    time.sleep(2)
    oled.fill(0)
    oled.text('CO: %.3fppmv'%g_co,8,0)
    oled.text('VOC:%.3f'%g_voc,0,10)
    oled.text('C2H5OH:%.3f'%g_c2h5oh,8,20)
    oled.show()
    time.sleep(1)
    
    #Returns NOK if no measurement found in reasonable time
    status = dust_sensor.read()
    #Returns NOK if checksum failed
    pkt_status = dust_sensor.packet_status
    #Stop fan
    dust_sensor.sleep()
    if(status == False):
        print('Measurement failed.')
    elif(pkt_status == False):
        print('Received corrupted data.')
    else:
        pm25=dust_sensor.pm25
        pm10=dust_sensor.pm10
        print('PM25: ', dust_sensor.pm25)
        print('PM10: ', dust_sensor.pm10)
        oled.fill(0)
        oled.text('pm25:'+str(pm25),8,0)
        oled.text('pm10:'+str(pm10),0,10)
        oled.show()    
    led.on()
    gpsdata=getGPS(gpsModule,gpsdata)
    print(gpsdata)
    if(gpsdata['FIX_STATUS'] == True):
        print("Printing GPS data...")
        print(" ")
        print("Latitude: "+gpsdata['latitude'])
        print("Longitude: "+gpsdata['longitude'])
        print("Satellites: " +gpsdata['satellites'])
        print("Time: "+gpsdata['GPStime'])
        print("----------------------")               
        gpsdata['FIX_STATUS'] = False
        oled.fill(0)
        oled.text(gpsdata['longitude'],8,0)
        oled.text(gpsdata['latitude'],0,10)
        oled.text(gpsdata['altitude'],8,20)
        oled.show()
        time.sleep(1)
    if(gpsdata['TIMEOUT'] == True):
        print("No GPS data is found.")
        oled.fill(0)
        oled.text('No GPS',8,20)
        oled.show()
        gpsdata['TIMEOUT'] = False
    print('before str')
    dstr=gpsdata['GPStime']+','+gpsdata['longitude']+','\
          +gpsdata['latitude']+','+gpsdata['altitude']+\
          ',%.3f'%g_no2+',%.3f'%g_co+',%.3f'%g_voc+\
          ',%.3f'%g_c2h5oh+',%.3f'%ozone_concentration+',%d'%sdc_co2+\
          ',%.2f'%sdc_t+',%.2f'%sdc_rh+\
          ','+str(pm25)+','+str(pm10)+','+bme.values[0]+\
          ','+bme.values[1]+','+bme.values[2]+'\n'
    print(dstr)
    file=open('/sd/data_'+str(int(tic)+1)+'.txt','a')
    file.write(dstr)
    file.close()
    print('write data correctly')
    led.off()
  except:
    led.on()
    time.sleep(0.5)
    led.off()
    led.on()
    time.sleep(0.5)
    led.off()
    led.on()
    time.sleep(0.5)
    led.off()
    
    
 