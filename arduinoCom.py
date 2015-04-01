# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
*   LogikAnalyse is a logic analyser for Arduino
*   LogikAnalyse has been written to analyse Signals from
*   rf-receivers to build a sender/receiver for sensors
*   and actuators for homeautomation.
*   
*   The package consists of a python GUI and an Arduino sketch.
*   To use the analyser, you have to upload the sketch to the Arduino, which 
*   is probably done best with the Arduino IDE, because I split the sketch into 
*   several files.
*   Afterwards, the recording and saving can be done from the GUI. Although the 
*   main functionality is shown on the GUI, there is a valuable output to the
*   interpreter shell, so make shure you'll have a look at it.
*   2014  N.Butzek
*
*   This program is free software: you can redistribute it and/or modify
*   it under the terms of the GNU General Public License as published by
*   the Free Software Foundation, either version 3 of the License, or
*   (at your option) any later version.
*
*   This program is distributed in the hope that it will be useful,
*   but WITHOUT ANY WARRANTY; without even the implied warranty of
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*   GNU General Public License for more details.
*
*   You should have received a copy of the GNU General Public License
*   along with this program.  If not, see <http://www.gnu.org/licenses/>.

commands:
?: help
pause30000           : length of the pause 30000, is used for pause detection
length400            : message length 400
scale10              : scale factor 10
pulseMin300          : minimal pulse length 300
pDetect0 /pDetect1   : pause detection

showData0 /showData1 : print data to serial port
writeBin0 /writeBin1 : print data to serial port as binary, note that this also sets
sync                 : send sync signal in binary mode
send1000             : send 1000 values
lineMode0 /lineMode1 : print data in lines(1) or in row(0)
receiver0 /receiver1 : enable/disable receiver
dump                 : dump values
reset                : reset to initial values
"""

import serial
from numpy import array, asarray, insert
from collections import deque
from time import sleep, time
import struct
import sys
import glob

class arduinoCom:
    
    def __init__(self, port, baud=250000):
        self.port = port
        self.baud = baud
        self.sleepTime = 1
        self.timeout = 3
        self.scale = 1
        self.pulseMin = 300
        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)# Nr= COM-1 => 12-> COM13
        sleep(self.sleepTime)        
        self.ser.flushInput()
        self.ser.flushOutput()
        print str(self.port) +" open at "+str(self.baud)+"baud"
        cmd = "reset\n";  self.ser.writelines(cmd)
        cmd = "lineMode0\n";  self.ser.writelines(cmd)
        cmd = "showData1\n";  self.ser.writelines(cmd)
        cmd = "scale"+str(self.scale)+"\n";  self.ser.writelines(cmd)
        cmd = "pulseMin"+str(self.pulseMin)+"\n";  self.ser.writelines(cmd)
        self.ser.flushInput()
           
    def closeSer(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.close()       
        print str(self.port)+" closed"

    def __del__(self):
        self.closeSer()  

    def sync(self):
        cmd = "showData0\n";  self.ser.writelines(cmd)
        self.ser.flushInput()
        sleep(0.1)
        cmd = "showData1\n";  self.ser.writelines(cmd)
               
    def switchReceive(self, scale=1, pulseMin=300): #Funktioniert gerade nicht
        self.ser.flushInput()
        self.ser.flushOutput()        
        self.scale = scale
        self.pulseMin = pulseMin
        cmd = "reset\n"; self.ser.writelines(cmd)
        cmd = "pDetect0\n"; self.ser.writelines(cmd)
        cmd = "lineMode0\n"; self.ser.writelines(cmd)
        cmd = "showData1\n"; self.ser.writelines(cmd)
        cmd = "writeBin1\n"; self.ser.writelines(cmd)
        cmd = "scale"+str(self.scale)+"\n"; self.ser.writelines(cmd)
        cmd = "pulseMin"+str(self.pulseMin)+"\n"; self.ser.writelines(cmd)
        self.ser.flushInput()

    def switchSend(self, numSamples, scale=1): #scale moentan ohne Funktion
        self.ser.flushInput()
        self.ser.flushOutput()        
        self.scale = scale
        cmd = "reset\n"; self.ser.writelines(cmd)
        cmd = "scale"+str(self.scale)+"\n"; self.ser.writelines(cmd)
        cmd = "send"+str(numSamples)+"\n"; self.ser.writelines(cmd)
        self.ser.flushInput()
        
    def switchQuiet(self):
        self.ser.flushInput()
        self.ser.flushOutput()        
        cmd = "reset\n"; self.ser.writelines(cmd)
        cmd = "showData0\n"; self.ser.writelines(cmd)
        self.ser.flushInput()
		
    def receive(self, numSamples):
        self.sync()
        sequence = []       
        for i in range(1,numSamples):
            try:
                aktRead = self.ser.read(2)
                #print aktRead
                if (len(aktRead) == 2):            
                    aktVal = struct.unpack('>h',aktRead)
                    #print aktVal
                    sequence.append(aktVal*self.scale)
                else:
                    print 'Fehler beim Lesen an der Seriellen Schnittstelle, %d bytes gelesen, aktRead ist String?: %s' % (len(aktRead), isinstance(aktRead, basestring))
      
            except KeyboardInterrupt:
                break #aussteigen/ Keyboard
        sequence = insert(asarray(sequence),0,0)
        return sequence

    def send(self, sequence):
        cnt = 0
        time = cumsum(abs(sequence))
        for aktSample in sequence:
            try:
                aktVal = struct.pack('<h', aktSample)
                #print cnt, aktSample
                self.ser.write(aktVal)
                buffsize = 100
                buff = floor(cnt/buffsize)
                if ((cnt%buffsize ==0) & (buff>1)): #immer bei 100 aber erst ab 200
                    sleep((time[buff*buffsize] - time[(buff-1)*buffsize])*1e-6)
                    print "Pause: buff %.1f time[%d]-time[%d] = %f s" % (buff, time[buff*buffsize], time[(buff-1)*buffsize], (time[buff*buffsize] - time[(buff-1)*buffsize])*1e-6)
                cnt +=1;
            except KeyboardInterrupt:
                break #aussteigen/ Keyboard
        return
                   
def serial_ports():
    """
	Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
                
if __name__ == '__main__':
    # This is for testing purpose:
    try:
        del pa
    except:
        pass
    aCom = arduinoCom('COM9',115200);
    sequence=array([])
    print("Konfiguriere empfangen")
    aCom.switchReceive(1, 300)
    print("Messung")
    sequence = aCom.receive(500)    
    aCom.switchQuiet()
    print sequence

    sequence = np.load('Daten/Logilink.npy')
    print("Konfiguriere senden")
    aCom.switchSend(len(sequence))
    print("Sende...")
    aCom.send(sequence)
    sleep(2)
    aCom.switchQuiet()
    print("Fertig")
    
    aCom.closeSer()
    #reload(sys.modules["arduinoCom"])