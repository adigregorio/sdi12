import serial
import time
import sdi_tools
import datetime
import numpy as np
import matplotlib.pyplot as plt

devices = sdi_tools.find_sdi_devices()
port = devices[0][0]
devId = devices[0][1]
radiometer = sdi_tools.SI400(port, devId)
radiometer.connect()
start_t = time.time()
meas_t = start_t
meas_no = 1

x_data = []
y_data = []

try:
    with open("temp.csv", 'a') as outputfile:
        while meas_t <= start_t + 300:
            meas_t = float(time.time())
            radiometer.makeMeasurement()
            measurement = float(radiometer.getData())
            line = "%s,%s,%s" % (meas_no, meas_t, measurement)
            outputfile.write(line)
            meas_no = meas_no + 1
            x_data.append(meas_t)
            y_data.append(measurement)
            
except (SystemExit, KeyboardInterrupt):
    print "quit!"
    outputfile.close()
    radiometer.disconnect()

radiometer.disconnect()

print x_data
print y_data

plt.plot(x_data, y_data)
plt.show()

