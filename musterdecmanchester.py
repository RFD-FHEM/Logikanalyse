# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 

@author: norman
@author: sven
"""
from collections import deque
import numpy as np


def reset():
    global sync
    global msg
    global testClock
    global bitcnt
    global muster
    global midx
    global average    
    global sample    
    global mcount   
    global cntstart
    sync=False
    msg=[]
    testClock = 0
    bitcnt = 1
    muster=[]
    midx=0
    average=0
    sample=0
    cntstart=0
    
    #print 'reset'

def chkPattern():
    global pulse
    global testClock
    
def rangecomp(tstval, minval,maxval):
    if minval<= tstval <= maxval:
        return True
    else:
        return False

def manchesterClock(pulse):
        global testClock
        if testClock == 0:
            manchesterClock.sample=0
            manchesterClock.average=0
        #print 'suche takt'
        if (abs(pulse) < testClock*0.5):
            testClock = abs(pulse)
        elif (abs(pulse) >= (testClock*0.5) and (abs(pulse) <= testClock*1.5)):
            manchesterClock.average =manchesterClock.average+abs(pulse)
            manchesterClock.sample=manchesterClock.sample+1
            testClock=manchesterClock.average/manchesterClock.sample
        elif (abs(pulse) >= testClock*1.5) and (abs(pulse) <= testClock*2.5):
            manchesterClock.average += abs(pulse)/2
            manchesterClock.sample=manchesterClock.sample+1
            testClock=manchesterClock.average/manchesterClock.sample
        else:
            testClock = abs(pulse)/2
    

#seq = np.load('Logilink.npy')
seq = np.load('OSV2.npy')
#seq = np.load('IT.npy')
#seq = np.load('tcm.npy')
#seq = np.load('ManchesterAS.npy') # erkennt nicht

pulse = deque(2*[0])
numbit = 2
minlen = 10
cnt = 0
sync=False
testClock=5000
average=0
sample=0
bitcnt=1
mcount=0
cntstart=0
skip=False
reset()


for aktpulse in seq:
    #print cnt, bitcnt, sync
    cnt += 1
    trash = pulse.popleft()
    trash = pulse.append(aktpulse)
    if skip:
        skip=False
        continue
    #print 'Puls0={},Puls1={}'.format(pulse[-2],pulse[-1])                        
    #continue


    if (sync == False): #suche Sync, Muster ist immer [1,n]*clock

        if (mcount >= 15):
            print "Valid manchester was found from {} till {} with clock {}".format(cntstart,cnt-3,testClock)
            print cntstart, cnt, testClock, muster, msg, len(msg)
        mcount=0
        reset();            
        
        if not ((pulse[-2] > 0 > pulse[-1]) or (pulse[-1] > 0 > pulse[-2])):                 
            #print 'Puls0={},Puls1={},takt={}'.format(pulse[-2],pulse[-1],testClock)                        
            sync=False
            continue


        if (pulse[-2]!=0):
            manchesterClock(pulse[-2])            
            #manchesterClock(pulse[-1])  # Anhand von zwei Pulsen versuchen eine Clock zu bestimmen
            
            #if (abs(pulse[-2]) < testClock*0.5):
            #    testClock = abs(pulse[-2])  #Init Testclock
            #elif (abs(pulse[-2]) >= (testClock*0.5) and (abs(pulse[-2]) <= testClock*1.5)):
            #    average = average+abs(pulse[-2])
            #    sample=sample+1
            #    testClock=average/sample
            #elif (abs(pulse[-2]) >= testClock*1.5) and (abs(pulse[-2]) <= testClock*2.5):
            #    average += abs(pulse[-2])/2
            #    sample=sample+1
            #    testClock=average/sample
            #else:
            #    #testClock = abs(pulse[-2])
            #    reset();
            #    synccnt = cnt-1
            #    continue
            #    #print 'Reset'
            
            #print 'Puls0={},Puls1={},takt={}'.format(pulse[-2],pulse[-1],testClock)                        
            if rangecomp(abs(pulse[-1]),testClock*1.5,testClock*2.5):
                #print "Valid manchester seq"
                sync = True
            elif rangecomp(abs(pulse[-1]),testClock*0.5,testClock*1.5):            
                #print "Valid manchester seq"
                sync = True
            else:
                #print "Error - race condition out of range {}".format(pulse[1])
                sync = False             
                reset()
                continue
            
            manchesterClock(pulse[-1])  
            cntstart=cnt
            tol = int(round(0.3 * testClock))

            #print "Beginning of valid manchester seq at idx {} with takt {}".format(cnt-2,testClock)

        #print pulse
    else: #clock gefunden jetzt suchen wir mit dieser clock auf manchester codierung

        if not ((pulse[-2] > 0 > pulse[-1]) or (pulse[-1] > 0 > pulse[-2])):                 # Hier ist noch was falsch, es geht darum heraus zu bekommen ob zwei positive oder negative folgem
            #print 'same state at idx {} Puls0={},Puls1={},takt={}'.format(cnt-2,pulse[-2],pulse[-1],testClock)                        
            sync=False
            continue

        
        
        if rangecomp(abs(pulse[-2]),testClock*1.5,testClock*2.5):
            #print "Valid manchester seq"
            #sync = True
            check = np.asarray(pulse[-2])        
            newPat = np.round(check,-1) #auf Zehner
            newPat = np.array(newPat)

        elif rangecomp(abs(pulse[-2]),testClock*0.5,testClock*1.5):            
            check = np.asarray(pulse)                    
            #print "Valid manchester seq"
            #sync = True
            if not rangecomp(abs(pulse[-1]),testClock*0.5,testClock*1.5):            
                #print 'Error - race condition long after short at idx {}  Pulse={}'.format(cnt-2,pulse[-1])
                sync = False   
                #reset()
                continue
            skip=True
            newPat = np.round(check,-1) #auf Zehner
        else:
           # print "Error - race condition out of range at idx {}  Pulse={}".format(cnt,pulse[-1])
            sync = False
            #reset()
            continue
        manchesterClock(pulse[-2]) ## Clock bei jedem Durchlauf anpassen
        mcount+= 1
        found = [all(abs(x-check)<tol) for x in muster]
        if (any(found)):
            msg.append(np.where(found)[0][0])
        else:
            muster.append(newPat)
            msg.append(len(muster)-1)







  

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
