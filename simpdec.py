# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 18:05:16 2014

@author: Norman
"""

from collections import deque
import numpy as np

class genericDecoder:

    def __init__(self, name='1-31'):
        self.tolerance = 5
        self.reset()
        self.searchTyp = 'factor' # default if not defined other

        def initEV1527():
            self.typ = 'EV1527'
            self.pulse = deque(2*[0])
            self.minLength = 10
    
        self.name = name;
        if (self.name == '1-31'):
            initEV1527()
            #self.startFact = 31
            self.start_seq= [1,-31]
            self.high = [1,-3]
            self.low = [3,-1]
            self.searchTyp = 'sequence' # default if not defined other

        elif (self.name =='1-18'): 
            initEV1527()
            self.start_seq= [1,-18]            
            #self.startFact = 18
            self.high = [1,-8]
            self.low = [1,-4] 
            self.searchTyp = 'sequence' # default if not defined other

        elif (self.name =='PT2262'): 
            self.typ = 'PT2262'
            self.pulse = deque(4*[0])
            #self.start_seq= [1,31]            
            self.startFact = 31
            self.minLength = 10
            #self.searchTyp = 'sequence' # default if not defined other
            #high/low are hardcoded at the moment
        else:
            print'Decoder unbekannt.'
            # schould raise exception here
            return

        self.doDecode = {'EV1527':self.decEV1527, 'PT2262':self.decPT2262, 'Test':self.doTest}
        self.doSearch = {'factor':self.searchFact, 'sequence':self.searchSeq}
        self.doState = {'ready':self.doSearch[self.searchTyp], 'decoding':self.doDecode[self.typ]}

    
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

    def searchFact(self): # Suche Startsequenz nach factor 1/n *takt
        #print self.pulse
        try:
            if (abs(self.pulse[1]+self.startFact*self.pulse[0]) < self.tolerance*self.pulse[0]): # Startsequenz 1/31
                #print 'Frac %d, abs(%d/%d)' %(abs(self.pulse[1]/float(self.pulse[0])), self.pulse[1], self.pulse[0])
                self.synccnt+=1
                if (self.synccnt>1):# 2. Sync
                    self.synccnt=0 # nächste Meldung vorbereiten
                    self.takt = abs(self.pulse[0]) # der erste ist der Takt
                    self.state = 'decoding'
                    self.bitcnt=3
                    #print self.state
                    #print self.pulse
        except:
            #division by zero in 1st run?
            print'searchStart fact exceptVal = 0*pulse'
            return

    def checkSeq(self, seqIn, tolIn=0.1):
        #print self.pulse
        #if (len(self.message)>=24):
        #    print "check"
        pulse = np.asarray(self.pulse)
        seq = np.asarray(seqIn)
        if (self.takt!=0):
            Val=(pulse/float(self.takt))
        else:
            return False
        #print Val
        tol = tolIn*abs(seq)
        if (np.all(abs(Val-seq)<tol)):
            return True
        else:
            return False

    def searchSeq(self): # Suche Startsequenz nach Muster [1 n]*takt
        #print 'searchStart'
        #print self.pulse[1], self.pulse[0]
        try:
            self.takt = self.pulse[-2]
            if (self.checkSeq(self.start_seq)):
                self.state = 'decoding'
                #print self.state
        except:
            #division by zero in 1st run?
            print'searchStart except'
            return
                        
    def decEV1527(self): #EVOOK decoder
        if (self.bitcnt<2):# we'll check 2 bits together
            self.bitcnt +=1 
        else:
            self.bitcnt=1
            # store normalized values
            try:
                #Val=[int(round(x/float(self.takt))) for x in list(self.pulse)]
                #print Val
                if (self.checkSeq(self.low,0.3)):
                    self.message.append(0) # 0 detected
                elif (self.checkSeq(self.high,0.3)):
                    self.message.append(1) # 1 detected
                else: # no bit detected, could be the end of the message 
                    if (len(self.message)>=self.minLength):
                        print self.typ, self.name, len(self.message)
                        print self.message
                    self.reset()
            except:
                self.reset()               

    def decPT2262(self): #PT2262 decoder
        #print 'decEV1527'
        #print self.bitcnt
        if (self.bitcnt<4):# we'll check 4 bits together
            self.bitcnt +=1 
        else:
            self.bitcnt=1;
            # store normalized values
            try:
                #Val=[int(round(x/float(self.takt))) for x in list(self.pulse)]
                #print Val
                tol=0.5
                if (self.checkSeq([1,-3,1,-3],tol)):
                    self.message.append(0) # 0 detected
                elif (self.checkSeq([3,-1,3,-1],tol)):
                    self.message.append(1) # 1 detected
                elif (self.checkSeq([1,-3,3,-1],tol)):
                    self.message.append(2) # F detected
                else: # no bit detected, could be the end of the message 
                    if (len(self.message)>=self.minLength):
                        print self.name, len(self.message)
                        if (np.any(self.message>2)):
                            print 'message contains floating states => decoder not valid'
                        else:
                            print self.message
                    self.reset()
                #print self.pulse
                #print self.message
            except:
                self.reset()
            
    def doTest(self):
        print 'TestDecoder'

if __name__ == '__main__':

    ev = genericDecoder('1-31')
    tcm = genericDecoder('1-18')
    pt = genericDecoder('PT2262')

    seq = np.load('Logilink.npy')
    #seq = np.load('IT-Schalter onoff.npy')
    #seq = np.load('IT.npy')
    #seq = np.load('tcm.npy')
    #seq = np.load('OSV2.npy')
    #seq = np.load('ManchestarAS.npy')
    cnt=0
    for pulse in seq:
        #print cnt
        #cnt +=1
        ev.decode(pulse)
        tcm.decode(pulse)
        pt.decode(pulse)

#reload(sys.modules["decoder"])
        
