from machine import Pin, UART, I2C
import utime, time
def getGPS(gpsModule,gpsdata):
    timeout = time.time() + 8 
    while True:
        gpsModule.readline()
        buff = str(gpsModule.readline())
        #print(buff)
        parts = buff.split(',')
        #print(parts)
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                print(buff) 
                gpsdata['latitude'] = convertToDegree(parts[2])
                if (parts[3] == 'S'):
                    gpsdata['latitude'] = '-'+gpsdata['latitude']
                gpsdata['longitude'] = convertToDegree(parts[4])
                if (parts[5] == 'W'):
                    gpsdata['longitude'] = '-'+gpsdata['longitude']
                gpsdata['altitude']=parts[6]
                gpsdata['satellites'] = parts[7]
                gpsdata['GPStime'] = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                gpsdata['FIX_STATUS'] = True
                break
                
        if (time.time() > timeout):
            gpsdata['TIMEOUT'] = True
            break
        utime.sleep_ms(500)
    return gpsdata
        
def convertToDegree(RawDegrees):
    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)
    
    
