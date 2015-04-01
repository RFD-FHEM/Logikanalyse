# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 09:20:36 2014

@author: norman
"""
from collections import deque
import numpy as np

class patternDecoder:
    
    def __init__(self):
        self.numbit = 2
        self.minlen = 10
        self.reset()

    def reset(self):
        self.sync=False
        self.msg=[]
        self.testClock = 1
        self.bitcnt = 1
        self.muster=[]
        self.midx=0
        #print 'reset'

    def chkPattern(self, seq):
        cnt = 0
        pulse = deque(2*[0])
        self.seq = seq
        for aktpulse in self.seq:
            #print cnt, bitcnt, sync
            cnt += 1
            trash = pulse.popleft()
            trash = pulse.append(aktpulse)
            if (self.sync == False): #suche Sync, Muster ist immer [1,n]*clock
                if (pulse[-2]!=0):
                    if ((10*pulse[-2]<=-pulse[-1])&(pulse[-2]>0)): #n>10 => langer Syncpulse
                        self.testClock = pulse[-2]
                        self.syncFact = np.round(pulse[-1]/self.testClock,1)
                        self.syncPulse = np.asarray(pulse)
                        synccnt = cnt-1
                        #print sync, syncFact
                        self.sync = True
                        bitcnt=1
                        tol = int(round(0.3 * self.testClock))
                        #print 'sync'
                #print pulse
            else: #dekodiere
                if (bitcnt == self.numbit):#nächster Satz vollständig
                    bitcnt = 1
                    #check = np.asarray(pulse)*np.array([1,-1])/float(testClock)
                    check = np.asarray(pulse)
                    #valides Muster prüfen:
                    #if (((abs(check[0]-1)<tol)&(0<check[1]<10))|((abs(check[1]-1)<tol)&(0<check[0]<10))):
                    if (((abs(check[0]-self.testClock)<tol)&(-10*self.testClock<check[1]<0))|((abs(check[1]+self.testClock)<tol)&(0<check[0]<10*self.testClock))):
                        newPat = np.round(check,-1) #auf Zehner
                        #wenn nicht vorhanden, aufnehmen
                        found = [all(abs(x-check)<tol) for x in self.muster]
                        if (any(found)):
                            self.msg.append(np.where(found)[0][0])
                        else:
                            self.muster.append(newPat)
                            self.msg.append(len(self.muster)-1)
                    else:
                        if (len(self.msg)>=self.minlen):
                                print 'synccnt: %d, Idx: %d, syncFact: %d, syncPulse:' %(synccnt, cnt, self.syncFact), self.syncPulse
                                print self.msg, len(self.msg)
                                print 'Pattern: ', self.muster[0], self.muster[1]
                                self.reset()
                else:
                    bitcnt +=1

if __name__ == '__main__':

    pd = patternDecoder()

    seq = np.load('Logilink.npy')# EV1527 18[512, -9192], 4[580, -1920], 8[520, -3880] #36
    #seq = np.load('OSV2.npy')
    #seq = np.load('IT.npy')# PT2262 -33[400, -13468], 3[430, -1300], 3[1300, -450] #24
    #seq = np.load('IT-Schalter onoff.npy')# ENV1527 -19[500, -9200], 4[570, -1930], 8[500, -3880] #36
    #seq = np.load('tcm.npy')# EV1527 -19[460, -8896], 4[490, -2000], 8[470, -3960] #36
    #seq = np.load('ManchesterAS.npy') # erkennt nicht

    pd.chkPattern(seq)
   


'''            
MusterA: ENV1527
	syncmuster: 	[1,-n]*clock, n=>10
	bitmuster: 	[1,-m], 10<=m
			es gibt nur zwei Bitmuster, der zweite Wert ist immer Low, also <0
	Bitfolge:	[1,-m1] => Bit=0
			[1,-m2] => Bit=1, mit m1<m2
MusterB: PT2262
	syncmuster: 	[1,31]*clock
	bitmuster: 	[1,-x]*clock, x
			[x,-1]*clock
			es gibt nur zwei Bitmuster, der zweite Wert ist immer Low, also <0
	Bitfolge:	[1,-x]*clock, [1,x]*clock => Bit=0
			[x,-1]*clock, [x,-1]*clock => Bit=1
			[1,-x]*clock, [x,-1]*clock => Bit=F
'''
