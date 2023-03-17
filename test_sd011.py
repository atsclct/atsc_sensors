import sds011
import time
sensor=sds011.SDS011('/dev/tty.usbserial-14220', use_query_mode=True)
for i in range(10):
    sensor.sleep(sleep=False)
    time.sleep(5)
    print(sensor.query())
    sensor.sleep()
    