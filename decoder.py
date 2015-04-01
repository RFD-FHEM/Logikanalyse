# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 18:05:16 2014

@author: Norman
"""

from collections import deque

class genericDecoder:

    def __init__(self, name='EV1527'):
        self.tolerance = 5
        self.reset()

        def initOOK():
            self.typ = 'OOK'
            self.pulse = deque(2*[0])
            self.minLength = 10

        self.name = name;
        if (self.name == 'EV1527'):
            initOOK()
            self.startFact = 31
            self.start_seq= [1,31]
            self.high = [1,-3]
            self.low = [3,-1]

        elif (self.name =='Logilink'): 
            #initOOK()
            self.typ = 'OOK2'
            self.pulse = deque(4*[0])
            self.minLength = 10

            self.startFact = 18
            self.start_seq= [16,1]
            self.high = [-7,1]
            self.low = [-3,1]

        elif (self.name =='TCM'): 
            initOOK()
            self.start_seq= [18,1]            
            self.startFact = 19
            self.high = [-8,1]
            self.low = [-4,1] 

        elif (self.name =='OSV2'): 
            #initOOK()
            #self.halfBit = 0		     
            self.typ = 'Manchester'
            self.pulse = deque(32*[0])
            self.minLength = 32
            self.start_seq= [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]            
            #self.start_seq = [[2]] * 32
            #self.startFact = 19
            #self.high = [-8,1]
            #self.low = [-4,1] 
            self.currentbit= -1

        elif (self.name =='CRESTA'): 
            #initOOK()
            self.halfBit = 0		     # 9 bytes of 9 bits each, 2 edges per bit = 162 halfbits for thermo/hygro
            self.isOne = False   		# true if the the last bit is a logic 1.
            #self.clockTime=0
            self.typ = 'Manchester'
            self.pulse = deque(5*[0])
            self.minLength = 10
            self.start_seq= [2,2,2,2,2]            
            self.currentbit= -1            
            #self.startFact = 19


        elif (self.name =='PT2262'): 
            self.typ = 'PT2262'
            self.pulse = deque(4*[0])
            self.start_seq= [1,31]            
            self.startFact = 31
            self.minLength = 10
            #high/low are hardcoded at the moment
        else:
            print'Decoder unbekannt.'
            # schould raise exception here
            return

        self.doDecode = {'OOK':self.decOOK, 'OOK2':self.decOOK2, 'Manchester':self.decManchester, 'PT2262':self.decPT2262, 'Test':self.doTest}
        #self.doState = {'ready':self.searchStart, 'decoding':self.doDecode[self.typ]}
        self.doState = {'ready':self.searchStart2, 'decoding':self.doDecode[self.typ]}

    
    def decode(self, pulse):
        self.pulse.popleft()
        self.pulse.append(pulse)
        self.doState[self.state]()
        return True
           
    def reset(self):
        #print 'reset'
        self.message=[]
        self.takt=0
        self.bitcnt=1
        self.synccnt=0
        self.state='ready'
        self.currentbit= -1            




    def searchStart(self): # Suche Startsequenz 1/31 *takt
        #print 'searchStart'
        #print self.pulse[1], self.pulse[0]
        try:
            if (abs(self.pulse[1]+self.startFact*self.pulse[0]) < self.tolerance*self.pulse[0]): # Startsequenz 1/31
                #print 'Frac %d, abs(%d/%d)' %(abs(self.pulse[1]/float(self.pulse[0])), self.pulse[1], self.pulse[0])
                self.synccnt+=1
                if (self.synccnt>1):# 2. Sync
                    self.synccnt=0 # nächste Meldung vorbereiten
                    self.takt = abs(self.pulse[0]) # der erste ist der Takt
                    self.state = 'decoding'
        except:
            #division by zero in 1st run?
            print'searchStart except'
            return

    def rangecomp(self,tstval, minval,maxval):
        
        if minval<= tstval <= maxval:
            return True
        else:
            return False
            

    def searchStart2(self): # Suche Startsequenz anhand von Parametern a z.B. 31/1
        #print 'searchStart'
        #print self.pulse[0], self.pulse[1]
        #print sequenz[0], sequenz[1]
        if (len(self.pulse) < len(self.start_seq)):
           return
       
        min_val, min_idx = min((val, idx) for (idx, val) in enumerate(self.start_seq))
        self.takt = abs(self.pulse[min_idx])/min_val        
        
        if self.takt == 0:
            return
        
        
        #max_val, max_idx = max((val, idx) for (idx, val) in enumerate(self.start_seq))
        #print min_val, max_val    
        #print 'Pruefe {} gegen {} +-200 mit Takt {} (multiplikator = {})'.format(abs(self.pulse[max_idx]),abs(self.takt*max_val),self.takt,max_val)
        cnt=0
        for cnt in range(0,len(self.start_seq)):
            #print '# {}: Pruefe {} gegen {} +-200 mit Takt {} (multiplikator = {})'.format(cnt,abs(self.pulse[cnt]),abs(self.takt*self.start_seq[cnt]),self.takt,self.start_seq[cnt])            
            if not self.rangecomp(abs(self.pulse[cnt]),abs(self.takt*self.start_seq[cnt])-220,abs(self.takt*self.start_seq[cnt])+240):        
                break
            #if self.rangecomp(abs(self.pulse[max_idx]),abs(self.takt*max_val)-200,abs(self.takt*max_val)+200):
               
                #print self.takt
                #print min_takt, max_takt
               
        else:
            print "Sync gefunden"
            self.state = 'decoding'
            #for cnt in range(0,len(self.start_seq)-3):            
            #    self.pulse.popleft()
            #self.pulse.appendleft(0) ## Append one entry to the queue, because we want two entries
            
            # Takt für Manchester
            if self.typ == "Manchester":
                self.manchesterClock(len(self.pulse))  
                
            while len(self.pulse) > 2:
                 self.pulse.popleft()
            self.bitcnt=2
                 #self.halfBit=1
            return
                
            
            
    def decOOK(self): #EVOOK decoder
        if (self.bitcnt<2):# we'll check 2 bits together
            self.bitcnt +=1 
        else:
            self.bitcnt=1
            # store normalized values
            try:
                Val=[int(round(x/float(self.takt))) for x in list(self.pulse)]
                #print Val
                if (Val==self.low):
                    self.message.append(0) # 0 detected
                elif (Val==self.high):
                    self.message.append(1) # 1 detected
                else: # no bit detected, could be the end of the message 
                    if (len(self.message)>=self.minLength):
                        print self.name, self.typ
                        print self.message
                    self.reset()
            except:
                self.reset()               

    def decOOK2(self): #decoder, der mit einer längeren queue als self.low / self.high arbeiten kann
        print "Starte decodierung"        
        if (self.bitcnt<2):# we'll check 2 bits together
            self.bitcnt +=1 
        else:
            self.bitcnt=1

            #  LOW-hIGH transition = 1
            #  High-Low transistion = 0
            #
            cnt=0            
            for cnt in range(0,len(self.low)):
                if not self.rangecomp(abs(self.pulse[cnt]),abs(self.takt*self.low[cnt])-200,abs(self.takt*self.low[cnt])+200):        
                    break
            else:
                self.message.append(0) # 0 detected
                return ## Funktion beenden
            
            cnt=0            
            for cnt in range(0,len(self.high)):
                if not self.rangecomp(abs(self.pulse[cnt]),abs(self.takt*self.high[cnt])-200,abs(self.takt*self.high[cnt])+200):        
                    break
            else:
                self.message.append(1) # 1 detected
                return ## Funktion beenden

            if (len(self.message)>=self.minLength):
                print self.name, self.typ
                print self.message
            self.reset()

    def printosv2(self):
        pos=0
        val=0
        for cnt in range(0,len(self.osvbit)):
            if (pos == 4):
                if (cnt % 8 == 0):
                    print hex(val)&0x0F # Higher nibble
                else:
                    print hex(val)
                val=0
                pos=0
            val = val >> pos & self.osvbit[cnt]
            pos=+1            

    def decManchester(self):
#1. Set up timer to interrupt on every edge (may require changing edge trigger in the 
#ISR)
#2. ISR routine should flag the edge occurred and store count value
#3. Start timer, capture first edge and discard this.
#4. Capture next edge and check if stored count value equal 2T (T = ½ data rate)
#5. Repeat step 4 until count value = 2T (This is now synchronized with the data clock)
#6. Read current logic level of the incoming pin and save as current bit value (1 or 0)
#7. Capture next edge
#  a. Compare stored count value with T
#  b. If value = T
#  i. Capture next edge and make sure this value also = T (else error)
#  ii. Next bit = current bit
#  iii. Return next bit
#  c. Else if value = 2T
#  i. Next bit = opposite of current bit
#  ii. Return next bit
#  d. Else
#  i. Return error 
#8. Store next bit in buffer
#9. If desired number of bits are decoded; exit to contin
        if (self.bitcnt<2):# we'll check 2 bits together
            self.bitcnt +=1 
            return
        else:
            self.bitcnt=1
        
        if self.currentbit == -1:
            self.manchesterSync()
            self.bitcnt=2
            return
        
        print 'Puls0={},Puls1={},takt={}'.format(self.pulse[0],self.pulse[1],self.takt)                        

            
        #if (self.halfBit == 0):
        #    self.halfBit=0

        
        ## Der empfangene Puls passt nicht mehr zum Takt, also geben wir alles aus und brechen ab
        # Entweder ist er viel zu lang oder wir haben einen langen Puls, der über das Taktsignal geht
        if (abs(self.pulse[0]) > 2.5*self.takt):
            
            print self.name, self.typ
            self.osvbit=[]
            self.osvbit = self.message[1::2]            
            print self.osvbit
            print self.message
            self.printosv2()
            ## Für OSV2 müsste nun jedes 2. Bit aus der Nachricht extrahiert werden, damit wir die gesendeten Bits haben
            self.reset()        
            print 'Reset'            
            return
        
        if self.rangecomp(abs(self.pulse[0]),self.takt*1.5,self.takt*2.5):
            self.currentbit=self.currentbit ^ 1
            self.bitcnt=2
        elif self.rangecomp(abs(self.pulse[0]),self.takt*0.5,self.takt*1.5):            
            if not self.rangecomp(abs(self.pulse[1]),self.takt*0.5,self.takt*1.5):            
                print 'Error - race condition long after short'
                self.currentbit = -1
                return
        else:
             print "Error - race condition out of range"
             self.currentbit = -1
             return
        
        print "Add {}".format(self.currentbit)
        self.message.append(self.currentbit) 
        return


        # Get bit value from first puls
        #if (self.pulse[0] > 0):
        #    self.currentbit=1
        #elif (self.pulse[0] < 0):
        #    self.currentbit=0
        #else:
        #    print "Error condition, pulse is 0"
              

        # Edge is long?
        if (abs(self.pulse[1]) > 1.5*self.takt): # read as: duration > 1.5 * clockTime
            # Long edge takes 2 halfbits

            print 'Pruefe long {} Takt {}, halfbit {}'.format(self.pulse[1],self.takt,self.halfBit)            
            if (self.halfBit & 1):
                print "race condition"
                return
            else:
                # Long Puls flips the current bit            
                self.currentbit=self.currentbit ^ 1
                self.halfBit +=1
        else:
            self.halfBit+=1            
            print 'Pruefe short {} Takt {}, halfbit {}'.format(self.pulse[1],self.takt,self.halfBit)            
            

        if not (self.halfBit & 1): #Prüfen ob gerade oder ungerade:
            self.message.append(self.currentbit) 
            print "Add {}".format(self.currentbit)
            
        self.halfBit +=1
            
        # Only process every second half bit, i.e. every whole bit.
        #if (self.halfBit & 1 == 1):  # Prüfen ob gerade oder ungerade
            #currentByte = self.halfBit / 18
            #currentBit = (self.halfBit >>1) % 9 # nine bits in a byte.
        #    if (self.isOne):
                    # Set current bit of current byte
        #        self.message.append(1) # 1 detected
                    #self.data[currentByte] |= 1<<currentBit
        #    else:
        #        self.message.append(0) # 1 detected
                   # Reset current bit of current byte
                    #self.data[currentByte] &= ~(1 << currentBit)
        
    def manchesterSync(self):
        sample=0        
        
        print 'Syncing to Manchester'                                
        while (sample < len(self.pulse)):
            print 'Sync Puls={}'.format(self.pulse[sample])                        
            if self.rangecomp(abs(self.pulse[sample]),self.takt*1.5,self.takt*2.5):
                if (abs(self.pulse[sample]) > 0):
                    self.currentbit=1
                    return
                else:
                    self.currentbit=0
                    return
            sample = sample + 1

    def manchesterClock(self,numSamples):
        sample=0
        average=0
        #print 'suche takt'
        while(sample < numSamples):
            #print 'takt={}, sample={}'.format(self.takt,sample)
            if (abs(self.pulse[sample]) < self.takt*0.5):
                self.takt = abs(self.pulse[sample])
            elif (abs(self.pulse[sample]) >= (self.takt*0.5) and (abs(self.pulse[sample]) <= self.takt*1.5)):
                average =average+abs(self.pulse[sample])
                sample=sample+1
                self.takt=average/sample
            elif (abs(self.pulse[sample]) >= self.takt*1.5) and (abs(self.pulse[sample]) <= self.takt*2.5):
                average += abs(self.pulse[sample])/2
                sample=sample+1
                self.takt=average/sample
            else:
                self.takt = 128
    
    

    
    def decPT2262(self): #PT2262 decoder
        #print 'decEV1527'
        #print self.bitcnt
        if (self.bitcnt<4):# we'll check 4 bits together
            self.bitcnt +=1 
        else:
            bitcnt=1;
            # store normalized values
            try:
                Val=[int(round(x/float(self.takt))) for x in list(self.pulse)]
                #print Val
                if (Val==[1,-3,1,-3]):
                    self.message.append(0) # 0 detected
                elif (Val==[3,-1,3,-1]):
                    self.message.append(1) # 1 detected
                elif (Val==[1,-3,3,-1]):
                    self.message.append(2) # 1 detected
                else: # no bit detected, could be the end of the message 
                    if (len(self.message)>=self.minLength):
                        print self.name, self.typ
                        print self.message
                    self.reset()
            except:
                self.reset()
            
    def doTest(self):
        print 'TestDecoder'

if __name__ == '__main__':

    ev = genericDecoder('EV1527')
    logi = genericDecoder('Logilink')
    tcm = genericDecoder('TCM')
    pt = genericDecoder('PT2262')
    osv2 = genericDecoder('OSV2')

    seq = load('OSV2.npy')
    for pulse in seq:
        #ev.decode(pulse)
        #logi.decode(pulse)
        osv2.decode(pulse)
        #tcm.decode(pulse)
        #pt.decode(pulse)

#reload(sys.modules["decoder"])
        