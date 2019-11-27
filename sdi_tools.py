import sys
import glob
import time
import serial


def find_ports():
    """ Lists serial port names
    
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    
    result = []
    for port in ports:
        try:
            ser = serial.Serial(port)
            ser.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def find_sdi_devices(ports=None):
    """
    finds devices connected to ports. if no ports are passed to the function, the
    program scans all available serial ports and tests them all for sdi devices.

    sdi devices are found by sending a wildcard acknowledge active command
    """
    results = []
    if not ports:
        ports = find_ports()
    for port in ports:
        try:
            ser = serial.Serial(port=port, baudrate=1200, timeout=1)
            ser.write(b'?!') #write wildcard acknowledge active command
            time.sleep(.5)
            response = ser.readline()
            response = response.rstrip("\r")
            response = response.rstrip("\n")
            response = response.rstrip("\r") # do it again to work both ways
            response = response.rstrip("\n")
            if response:
                response = int(response)
                results.append((port, response))
            else:
                pass
            ser.close()
        except (OSError, serial.SerialException):
            pass
    return results

class instrument:
    def __init__(self, port, address):
        self.port = port
        self.address = address
        self.connected = False
        self.comm = None
     
    def connect(self):
        self.comm = serial.Serial(port=self.port, baudrate=1200, timeout=.5)
        self.connected = True
    
    def disconnect(self):
        self.comm.close()
        self.connected = False
     
    def _sendCommand(self, command):
        if not self.connected:
            print("Device not connected. Connecting now...")
            self.connect()
            print("Connected!")
        else:
            pass
        
        command = bytes(command)
        self.comm.write(command)
        time.sleep(1)
        return self.comm.read(self.comm.in_waiting)

class SI400(instrument):
    def __init__(self, port, address):
        instrument.__init__(self, port, address)
    
    def getId(self):
        idCommand = "%sI!" % self.address
        return self._sendCommand(idCommand)
    
    def makeMeasurement(self):
        measCommand = "%sM!" % self.address
        return self._sendCommand(measCommand)
    
    def getData(self):
        dataCommand = "%sD0!" % self.address
        result = self._sendCommand(dataCommand)
        result = result[2:]
        return result
    
    def changeAddress(self, newAddress):
        changeAddress = "%sA%s!" % (self.address, newAddress)
        return self.sendCommand(changeAddress)


