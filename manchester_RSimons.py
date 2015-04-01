# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 11:31:24 2014

@author: Norman
All I did was, that I transferred the c-code from R.Simons sensor-transmit and receive librarys to python.
Original text from R.Simons:
 * RemoteSensor library v1.0.2 (20130601) for Arduino 1.0
 * 
 * This library receives, decodes, decrypts and receives data of
 * remote weather sensors made by Hideki Electronics.
 * 
 * Copyright 2011-2013 by Randy Simons http://randysimons.nl/
 *
 * Parts of this code based on Oopsje's CrestaProtocol.pdf, for which
 * I thank him very much!
 *
 * For more details about the data format, see CrestaProtocol.pdf
 * 
 * License: GPLv3. See license.txt
"""
from numpy import load

class crestaReceiver(object): 

    def __init__(self): 
        self.halfBit = 0		     # 9 bytes of 9 bits each, 2 edges per bit = 162 halfbits for thermo/hygro
        self.isOne = False   		# true if the the last bit is a logic 1.
        self.packageLength = 0
        self.duration = 0		# Duration of current edge.
        self.data = 14*[0] 		# Maximum number of bytes used by Cresta
        self.clockTime=0
       
    """
    * I'll follow CrestaProtocol documentation here. However, I suspect it is inaccurate at some points:
    * - there is no stop-bit after every byte. Instead, there's a start-bit (0) before every byte.
    * - Conversely, there is no start-bit "1" before every byte.
    * - An up-flank is 0, down-flank is 1, at least with both my receivers.
    *
    * However, since the first start-bit 0 is hard to distinguish given the current clock-detecting
    * algorithm, I pretend there *is* a stop-bit 0 instead of start-bit. However, this means the
    * last stop-bit of a package must be ignored, as it simply isn't there.
    *
    * This manchester decoder is based on the principle that short edges indicate the current bit is the
    * same as previous bit, and that long edge indicate that the current bit is the complement of the
    * previous bit.
    """
    
    def process(self,duration):
        self.duration = duration            
        if (self.halfBit==0):
            # Automatic clock detection. One clock-period is half the duration of the first edge.
            self.clockTime = self.duration >>1
            # Some sanity checking, very short (<200us) or very long (>1000us) signals are ignored.
            if not(200<=self.clockTime<=1000):
                return
            self.isOne = True
        else:
            # Edge is not too long, nor too short?
            if ( not(0.5*self.clockTime) < self.duration < (3*self.clockTime)):
                # Fail. Abort.
                self.reset()
                return
        # Only process every second half bit, i.e. every whole bit.
        if (self.halfBit & 1 == 1):  
            currentByte = self.halfBit / 18
            currentBit = (self.halfBit >>1) % 9 # nine bits in a byte.
            if (currentBit < 8):
                if (self.isOne):
                    # Set current bit of current byte
                    self.data[currentByte] |= 1<<currentBit
                else:
                    # Reset current bit of current byte
                    self.data[currentByte] &= ~(1 << currentBit)
            else:
                # Ninth bit must be 0
                if (self.isOne):
                    # Bit is 1. Fail. Abort.
                    self.reset()
                    return
                if (self.halfBit == 17): # First byte has been received
                    # First data byte must be x75.
                    if not(self.data[0] == 0x75):
                        self.reset()
                        print 'Ich glaube, die Meldung ist nicht für uns, fängt jedenfalls nicht mit 0x75 an'
                        return
                elif (self.halfBit == 53): # Third byte has been received
                    # Obtain the length of the data
				decodedByte = self.data[2]^(self.data[2]*2)
				self.packageLength = (decodedByte >> 1) & 0x1f

				# Do some checking to see if we should proceed
				if not(6 <= self.packageLength <=11):
					self.reset()
					return
				halfBitCounter = (self.packageLength + 3) * 9 * 2 - 2 - 1 # 9 bits per byte, 2 edges per bit, minus last stop-bit (see comment above)
                # Done?
                if (self.halfBit >= halfBitCounter):
                    if (self.halfBit == halfBitCounter):
                         # Yes! Decrypt and print out
                         if (self.decryptAndCheck()):
                             # Meldung Ausgeben
                             print self.data
                             self.decodeAS()
                    # reset
                    self.halfBit = 0
                    return
        # Edge is long?
        if (self.duration > 1.5*self.clockTime): # read as: duration > 1.5 * clockTime
            # Long edge.
            self.isOne = not self.isOne
            # Long edge takes 2 halfbits
            self.halfBit +=1

        self.halfBit +=1

    
    def reset(self):
        self.halfBit = 1
        self.clockTime = self.duration /2
        self.isOne = True
        
    def decryptAndCheck(self):
        cs1=0
        cs2=0
        for i in range(self.packageLength+2): 
            cs1 = cs1^self.data[i]
            cs2 = self.secondCheck(self.data[i] ^ cs2)
            self.data[i] = self.data[i] ^ (self.data[i]*2)
        if (cs1):
            return False
        if not(cs2==self.data[self.packageLength+2]):
            return False
        return True
    
    def secondCheck(self,b): 
        if (b&0x80):
            b=b^0x95 
        c = b^(b/2)
        if (b&1):
            c=c^0x5f
        if (c&1):
            b=b^0x5f  
        return b^(c/2) 

    def decodeThermoHygro(data):
        channel = data[1] >> 5
        	
        # Internally channel 4 is used for the other sensor types (rain, uv, anemo).
        # Therefore, if channel is decoded 5 or 6, the real value set on the device itself is 4 resp 5.
        if (channel >= 5):
           channel-=1
        randomId = data[1] & 0x1f
        temp = 100 * (data[5] & 0x0f) + 10 * (data[4] >> 4) + (data[4] & 0x0f);
        # temp is negative?
        if (~(data[5] & 0x80)):
        	temp = -temp;
        humidity = 10 * (data[6] >> 4) + (data[6] & 0x0f);
        return  channel, randomId, temp, humidity

    def decodeAS(self):       
        device = self.data[3] & 0x0f;
        id = self.data[1];
        #numDataBytes = ((data[2]>>1) & 0x1f)-4;
        # numDataBytes muss 2 sein, sonst Fehler.
        value = word(self.data[5],self.data[4]);
        battery = (self.data[2] >> 6) & 3;
        trigger = data[2] & 1
        print 'AS-Sensor Dev: %d, ID: %d, Wert: %d, Bat: %d, Trigger: %d' %(device, id, value, battery, trigger)


"""
/*******************
 * Sensor base class
 ******************/
"""

class crestaTransmitter(object): 

    def __init__(self): 
        #self.halfBit = 0		     # 9 bytes of 9 bits each, 2 edges per bit = 162 halfbits for thermo/hygro
        #self.isOne = False   		# true if the the last bit is a logic 1.
        #self.packageLength = 0
        #self.duration = 0		# Duration of current edge.
        self.data = 14*[0] 		# Maximum number of bytes used by Cresta
        self.clockTime=500
        self.randomId = 4
        self.channel = 3

    # Encrypt data byte to send to station
    def encryptByte(self, b):
        for a in range(b):
            # (a=0; b; b<<=1)
            b<<=1
            a^=b
        return a

    # The second checksum. Input is OldChecksum^NewByte
    def secondCheck(self, b): 
        if (b&0x80):
            b^=0x95
        c = b^(b>>1) 
        if (b&1):
            c^=0x5f
        if (c&1):
            b^=0x5f 
        return b^(c>>1)
    """
     Example to encrypt a package for sending, 
     Input: Buffer holds the unencrypted data. 
     Returns the number of bytes to send, 
     Buffer now holds data ready for sending. 
    """
    def encryptAndAddCheck(self, buff):
        count=(buff[2]>>1) & 0x1f
        cs1=0
        cs2=0
        for i in range(1,1+count):
            buff[i]=self.encryptByte(buff[i])
            cs1^=buff[i]
            cs2 =self.secondCheck(buff[i]^cs2)
        buff[count+1]=cs1
        buff[count+2]=self.secondCheck(cs1^cs2)
        return count+3
        
    # Send one byte and keep the transmitter ready to send the next
    def sendManchesterByte(self, byte):
        low = -self.clockTime
        high = self.clockTime=500
        byteSequence = []
        # Send start-bit 0
        byteSequence.append(low)
        byteSequence.append(high)
    
        for i in range(16):
           if (byte&1):
               byteSequence.append(high)
           else:
               byteSequence.append(low)    
           byte=~byte; 
           if (i&1):
               byte>>=1
        return byteSequence
        
    # Send bytes (prepared by “encryptAndAddCheck”) and pause at the end. */
    def sendManchesterPackage(self,data,cnt):
        package = []
        for i in range(cnt):
            byte = self.sendManchesterByte(data[i])
            package+=byte 
        return package
            

    # Encrypts, adds checksums and transmits the data. The value of byte 3 in the data is ignored.
    def sendPackage(self, data):
        package = []
        for i in range(3): # Sends 3 packages
            buff = data #memcpy(buff, data,  ((data[2] >> 1) & 0x1f) + 1)
            temp = 0x5e+i*0x40       
            buff[3] = temp
            count = self.encryptAndAddCheck(buff) # Encrypt, add checksum bytes
            package += self.sendManchesterPackage(buff,count) # Send the package
            package += [6*self.clockTime];
        return package

    def sendTempHumi(self, temperature, humidity):
        buff=10*[0]
        # Note: temperature is 10x the actual temperature! So, 23.5 degrees is passed as 235.      	
        buff[0] = 0x75 	# Header byte
        buff[1] = (self.channel << 5) | self.randomId # Thermo-hygro at channel 1 (see table1)
        buff[2] = 0xce   # Package size byte for th-sensor 
        if (temperature<0):
            buff[5] = 0x4 << 4		# High nibble is 0x4 for sub zero temperatures...
            temperature = -temperature # Make temperature positive
        else:
            buff[5] = 0xc << 4		# ...0xc for positive        	
        # Note: temperature is now always positive!
        buff[4] = (((temperature % 100) / 10 ) << 4) | (temperature % 10)	#the "3" from 23.5 the "5" from 23.5
        buff[5] |= (temperature / 100) 					# the "2" from 23.5        	
        buff[6] = ((humidity / 10) << 4) | (humidity % 10) # BCD encoded      	
        buff[7]=0xff		# Comfort flag
        	
        package = self.sendPackage(buff)
        return package


if __name__ == '__main__':
     man =  crestaReceiver()
     seq = load('ManchesterASlong.npy')
     for pulse in seq:
         man.process(pulse)