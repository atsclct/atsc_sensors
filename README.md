# atsc_sensors - measuring gas and aerosol with raspberry pi and pico 
* This project uses a raspberry pico to drive a GPS module, a SDS011 PM25 PM10 sensor, a SDC41 co2 sensor, a grove multi gas sensor version 2, a gravity ozone sensor, bme280, a sdcard, and a ssd1306 oled display. The goal is to take CO, CO2, VOC, C2H5OH, NO2, O3, PM25, PM10, measurement with mobility provided by GPS. The data are automatically saved in sd card. 
* Some of the python codes were migrated from codes (xxx_pi.py) for raspberry pi python, or c++.
> * test_xxx.py: test code for individual sensors
> * xxx_pi.py: the driver code for raspberry pi instead of PICO 
> * ozone.py: GROVE ozone sensor driver
> * scd4x.py: SCD40/41 CO2/Temperature/Relative Humidity sensor driver
> * gas_gmxx.py: GROVE/GRAVITY multi gas sensor version 2 driver (CO VOC NO2 C2H5OH)
> * get_gps.py: GPS driver
> * sds011.py: NOVA SDS011 PM25/PM10 sensor driver
> * sdcard.py: sdcard driver
> * ssd1306.py: oled driver

Details of the project see wiki tab.

![](https://github.com/atsclct/atsc_sensors/blob/main/setup.jpeg)
