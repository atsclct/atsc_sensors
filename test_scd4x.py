# SPDX-FileCopyrightText: 2020 by Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
from machine import I2C, Pin
import sdc4x
i2c1=machine.I2C(1,sda=machine.Pin(18),scl=machine.Pin(19))
i2c1.scan()

print(i2c1.scan())

# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
scd4x = sdc4x.SCD4X(i2c_bus=i2c1,address=0x62)
print("Serial number:", [hex(i) for i in scd4x.serial_number])

# The reinit command reinitializes the sensor by reloading user settings
# from EEPROM.
# scd4x.reinit()

# The perform_factory_reset command resets all configuration settings
# stored in the EEPROM and erases the FRC and ASC algorithm history.
# scd4x.factory_reset()

# The perform_self_test feature can be used as an end-of-line test to
# check sensor functionality and the customer power supply to the sensor.
# scd4x.self_test()

# You can set the temperature offset (default hardware is 4*C)
scd4x.temperature_offset = 5.4

# You can set the altitude offset (default hardware is 0m)
scd4x.altitude = 15

# Set the current state (enabled / disabled) of the automatic self-calibration.
# By default, ASC is enabled
scd4x.self_calibration_enabled = True

# Once set, you may want to permanently write these settings to EEPROM
scd4x.persist_settings()

print("Temperature offset:", scd4x.temperature_offset)
print("Self-calibration enabled:", scd4x.self_calibration_enabled)
print("Altitude:", scd4x.altitude, "meters above sea level")

print("")

scd4x.start_periodic_measurement()
print("Waiting for first measurement....")
#scd4x.self_test()

while True:
    if scd4x.data_ready:
        print("CO2: %d ppm" % scd4x.CO2)
        print("Temperature: %0.1f *C" % scd4x.temperature)
        print("Humidity: %0.1f %%" % scd4x.relative_humidity)
        print()
    time.sleep(1)