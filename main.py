from machine import Pin, UART
from get_gps import *
import sdcard
import uos
import sds011
import utime, time
# Initial 
gpsModule = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
buff = bytearray(255)
gpsdata={'TIMEOUT':False,
         'FIX_STATUS':False,
         'latitude':"",
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
while True:
  try:
    print('Start fan for 5 seconds.')
    dust_sensor.wake()
    time.sleep(5)
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
    led.on()
    gpsdata=getGPS(gpsModule,gpsdata)
    if(gpsdata['FIX_STATUS'] == True):
        print("Printing GPS data...")
        print(" ")
        print("Latitude: "+gpsdata['latitude'])
        print("Longitude: "+gpsdata['longitude'])
        print("Satellites: " +gpsdata['satellites'])
        print("Time: "+gpsdata['GPStime'])
        print("----------------------")               
        gpsdata['FIX_STATUS'] = False
    if(gpsdata['TIMEOUT'] == True):
        print("No GPS data is found.")
        gpsdata['TIMEOUT'] = False

    dstr=gpsdata['GPStime']+','+gpsdata['longitude']+','\
          +gpsdata['latitude']+','+gpsdata['satellites']+\
          ','+str(pm25)+','+str(pm10)+'\n'
    print(dstr)
    file.write(dstr)
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
    
    
