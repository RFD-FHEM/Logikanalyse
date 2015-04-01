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
"""

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

import Tkinter as Tk
from tkFileDialog import askopenfilename, asksaveasfilename

#from pygraphics import media
#import images
from media import load_image

from arduinoCom import *
from time import sleep, time
import numpy as np
#from pylab import *
from collections import deque
import ConfigParser

__version__ = '2.0'
       
class sequenzAnalyse(object):
 
    def __init__(self, root):
        self.images = []
        self.axes = []
        self.filename = ''
        self.sequenz = Daten()
        self.serialState = ''
        self.decstart = 0
        self.decend = 1500
        #GUI
        self.config = ConfigParser.RawConfigParser()
        self.configfile = 'LogikAnalyse.cfg'
        self.defaultDir = "Daten"
        try:
            self.loadConfig()
        except:
            print 'Kein Configfile gefunden, nehme Anfangswerte'
            #initial defaults
            self.pulseMin = 300
            self.samples = 1500
            self.comPortSelect = 'COM9'
            self.messTyp = 'pulse'

        self.root = root
        self.root.title('Logik Analyse')
        self.root.protocol("WM_DELETE_WINDOW", self.exit_)
        
        self.fig = matplotlib.figure.Figure()
        self.axes = self.fig.add_subplot(1, 1, 1)

        figframe = Tk.Frame(root)
        figframe.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        canvas = FigureCanvasTkAgg(self.fig, master=figframe)
        toolbar = NavigationToolbar2TkAgg(canvas, figframe)
        toolbar.pack(side=Tk.TOP, fill=Tk.BOTH)  # expand=1)
        self.modify_toolbar()
        
        self.scaleY()
        self.add_menu()

        configframe = Tk.Frame(root)
        configframe.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=1)
        
        self.samplesSpinboxVal = Tk.StringVar()
        self.samplesSpinboxVal.set(str(self.samples))
        self.samplesSpinboxLabel = Tk.Label(configframe, text='Samples').pack(side=Tk.LEFT, anchor=Tk.E)
        self.samplesSpinbox = Tk.Spinbox(configframe, from_=500, to=5000, increment=500, width=5, textvariable = self.samplesSpinboxVal)
        self.samplesSpinbox.pack(side=Tk.LEFT)
        self.pulseMinSpinboxVal = Tk.StringVar()
        self.pulseMinSpinboxVal.set(str(self.pulseMin))
        self.pulseMinSpinboxLabel = Tk.Label(configframe, text='pulseMin').pack(side=Tk.LEFT, anchor=Tk.E)
        self.pulseMinSpinbox = Tk.Spinbox(configframe, from_=100, to=500, increment=50, width=5, textvariable = self.pulseMinSpinboxVal)
        self.pulseMinSpinbox.pack(side=Tk.LEFT)
        self.comPortSpinboxVal = Tk.StringVar()
        self.comPortSpinboxVal.set(str(self.comPortSelect))
        #print self.comPortSpinboxVal.get()
        self.comPorts = tuple(serial_ports())
        self.comPortSpinboxLabel = Tk.Label(configframe, text='Port').pack(side=Tk.LEFT, anchor=Tk.E)
        self.comPortSpinbox = Tk.Spinbox(configframe, command=self.switchconnectSer(), values=self.comPorts, textvariable=self.comPortSpinboxVal, width=14)
        self.comPortSpinbox.pack(side=Tk.LEFT)
        self.messTypRadioVal = Tk.StringVar()
        self.messTypRadioVal.set(self.messTyp)
        self.messTypDtRadio = Tk.Radiobutton(configframe, text='dt', padx = 0, variable=self.messTypRadioVal, value='dt')
        self.messTypDtRadio.pack(side=Tk.LEFT, anchor=Tk.W)
        self.messTypPulseRadio = Tk.Radiobutton(configframe, text='Pulse', padx = 0, variable=self.messTypRadioVal, value='pulse')
        self.messTypPulseRadio.pack(side=Tk.LEFT, anchor=Tk.W)

        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        self.root.bind('<Control-y>', lambda e: self.scaleY())
        self.root.bind('<Control-m>', lambda e: self.aufnahme())

        # implement the default mpl key bindings
        def on_key_event(event):
            #if (event.key=='y'):
            #    self.scaleY()
            key_press_handler(event, canvas, toolbar)
        self.tmp_cid1 = canvas.mpl_connect('key_press_event', on_key_event)
        def on_button_event(event):
            self.scaleY()
        self.tmp_cid2 = canvas.mpl_connect('button_release_event', on_button_event)

    def modify_toolbar(self):
        # Modify Toolbar
        def add_icon(text='Button', command=None, image=None):
            self.images.append(Tk.PhotoImage(data=image))
            b = Tk.Button(self.fig.canvas.toolbar,
                          text=text, command=command, image=self.images[-1],
                          height=40, compound="top")
            b.pack(side=Tk.LEFT)
            return b
    
        def add_separator(width=10):
            Tk.Frame(self.fig.canvas.toolbar, width=width).pack(side=Tk.LEFT)
    
        add_separator()
        add_icon('Lade', lambda: self.ladeSequenz(), load_image('icon_open.gif'))
        add_icon('Speichere', lambda: self.speichereSequenz(), load_image('icon_save.gif'))
        add_separator()
        self.verbindungButton = add_icon('Verbindung', lambda: self.verbindungToggleButton(),
                 load_image('icon_laptop.gif'))
        self.aufnahmeButton = add_icon('Aufnahme', lambda: self.aufnahme(),
                                               load_image('icon_oszi.gif'))
        add_icon('Messung', lambda: self.messung(),
                 load_image('icon_measure.gif'))
        #add_icon('Analyse', lambda: self.analyse(),
        #         load_image('icon_calculator.gif'))
        add_icon('Pruefe', lambda: self.pruefeDaten(),
                 load_image('icon_abacus.gif'))
        add_icon('Bereinigen', lambda: self.plot(),
                 load_image('icon_close.gif'))
        add_separator()

    def add_menu(self):
        def enable_function(menu, idx):
            def fun(enable=True):
                if enable:
                    menu.entryconfig(idx, state='normal')
                else:
                    menu.entryconfig(idx, state='disabled')
            return fun
    
        def add_command(menu, label, underline=None, command=None,
                        accelerator=None):
            menu.add_command(label=label, command=command, underline=underline,
                             accelerator=accelerator)
            enable_fun = enable_function(menu, cnt[0])
            cnt[0] = cnt[0] + 1
            return enable_fun
    
        def add_separator(menu):
            menu.add_separator()
            cnt[0] = cnt[0] + 1
        cnt = [0]
    
        menubar = Tk.Menu(self.root)
        # FILE
        filemenu = Tk.Menu(menubar, tearoff=0)
        cnt[0]=0
        self.menuitem_open_enable = add_command(filemenu, u'Öffnen', 0, self.ladeSequenz, 'Strg+O')
        self.menuitem_save_enable = add_command(filemenu, u'Speichern unter...', 0, self.speichereSequenz, 'Strg+S')
        add_separator(filemenu)
        add_command(filemenu, 'Beenden', 0, self.exit_, 'Escape')
        menubar.add_cascade(label='Datei', menu=filemenu, underline=0)
        # HELP
        helpmenu = Tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='Hilfe', underline=0, command=self.zeigeHilfe)
        menubar.add_cascade(label='Hilfe', menu=helpmenu, underline=0)
        # display the menu
        self.root.config(menu=menubar)
    
    def updateSettings(self):
        self.pulseMin = self.pulseMinSpinboxVal.get()
        self.samples = self.samplesSpinboxVal.get()
        self.comPortSelect = self.comPortSpinboxVal.get()
        self.messTyp = self.messTypRadioVal.get()
        
        
    def zeigeHilfe(self):
        print'Hilfe muss man noch einprogrammieren.'

    def verbindungToggleButton(self):
        if (self.serialState=='connect'):
            self.serialState = ''
            self.disconnectSer()
        else:
            self.serialState = 'connect'
            self.connectSer()
        
    def switchconnectSer(self):
        if (self.serialState=='connect'):
            self.disconnectSer()
        self.comPortSelect=self.comPortSpinboxVal.get()
        
    def disconnectSer(self):
        try:
            del self.pa
            self.fig.canvas.draw()                
            self.serialState = ''
            self.verbindungButton.configure(relief=Tk.RAISED)
        except:
            pass

    def connectSer(self):           
        try:
            self.arduino = arduinoCom(self.comPortSpinbox.get(),250000)
            self.arduino.switchQuiet() # turn off serial output of arduino to keep comport clean
            self.serialState = 'connect'
            self.verbindungButton.configure(relief=Tk.SUNKEN)
            self.fig.canvas.draw()                
        except:
            print u'Fehler beim Öffnen des ComPorts'
            return

    def ladeSequenz(self, fname=None):
        print'ladeSequenz'
        if fname is None:
            fname = askopenfilename(
                parent=self.root,
                initialfile=self.filename,
                initialdir=self.defaultDir,
                filetypes=(('numpy data', '*.npy'),),
                title='SequenzAnalyse: Sequenz laden')
            if not fname:
                return None
        # load DATA
        self.filename = fname
        self.sequenz.load(fname)
        self.decstart = 0
        self.decend = len(self.sequenz)    
        self.root.title(fname)
    
        self.root.update()
        self.plot()
        return fname
                
    def speichereSequenz(self):
        print'speichereSequenz'
        self.updateSettings()
        fname = asksaveasfilename(
            parent=self.root,
            initialfile=self.filename,
                initialdir=self.defaultDir,
                filetypes=(('numpy data', '*.npy'),),
                title='SequenzAnalyse: Sequenz speichern')
        if not fname:
            return None
        self.sequenz.save(fname)
	self.root.title(fname)
        
    def plot(self):
        self.axes.cla()
        self.axes.step(self.sequenz.t,self.sequenz.sig)
        self.scaleY()
        self.axes.set_ylabel('Signal')
        self.axes.set_xlabel('time /mikros')
        self.fig.canvas.draw()
        self.root.update()
        #stpPlot.draw()        
        #show()

    def scaleY(self):
        self.axes.set_ylim(-0.1,1.1)
        
    def messung(self):           
        def measDist(tmin, tmax):
            self.updateSettings()
            t = self.sequenz.t
            pulse = self.sequenz.pulse
            dT = (tmax-tmin)       
            tminIdx = np.where (t>tmin)[0][0]
            tmaxIdx = np.where (t<tmax)[0][-1]+1
            print 'dT: %d mikros, Tmin(%d): %d ms, Tmax(%d): %d ms' %(dT, tminIdx, tmin/1000, tmaxIdx, tmax/1000)
            pulseTmin = pulse[tminIdx]
            pulseTmax = pulse[tmaxIdx]
            if (tminIdx==tmaxIdx):
                print 'P: %d mikros, Pidx: %d, T: %.3f ms' % (pulseTmin, tminIdx, t[tminIdx]/1000)
            else:            
                print 'P1: %d mikros, P2: %d mikros, P2/P1: %.1f' % (pulseTmin, pulseTmax, abs(pulseTmax)/float(abs(pulseTmin)))
            if (self.messTyp=='dt'):
                self.axes.set_title("dT: %d mikros" % dT)
            else:
                if (tminIdx==tmaxIdx):
                    self.axes.set_title("P: %d mikros, Pidx: %d, T: %.3f ms" % (pulseTmin, tminIdx, t[tminIdx]/1000))
                else:            
                    self.axes.set_title("P1: %d mikros, P2: %d mikros, P2/P1: %.1f" % (pulseTmin, pulseTmax, abs(pulseTmax)/float(abs(pulseTmin))))
            self.fig.canvas.draw()

        self.spanMeas = matplotlib.widgets.SpanSelector(self.axes, measDist, 'horizontal', useblit=True,
                                rectprops=dict(alpha=0.5, facecolor='red') )

    def analyse(self):
        #Decoder init
        self.updateSettings()
        try:
            reload(sys.modules["decoder"])        
        except:
            pass
        from decoder import genericDecoder
        from musterdec import patternDecoder

        pattDec = patternDecoder()
        """
        EV = genericDecoder('EV1527')
        PT = genericDecoder('PT2262')
        TST = genericDecoder('Test')
        TCM = genericDecoder('TCM')        
        Logi = genericDecoder('Logilink')        
        osv2 = genericDecoder('OSV2')        
        cresta = genericDecoder('CRESTA')        
        print'analyse'      
        for idx in range(len(self.sequenz.pulse)-1):
            frac = self.sequenz.pulse[idx+1]/self.sequenz.pulse[idx]
            if ((frac<-10) and (frac>-40)):
                print 'Frac %d, abs(%d/%d) bei T(%d)= %d ms' %(np.abs(frac), self.sequenz.pulse[idx+1], self.sequenz.pulse[idx], idx, self.sequenz.t[idx]/1000)
        
        print 'Starte EV1527 Decoder'
        for pulse in self.sequenz.pulse:
            EV.decode(pulse)
        EV.reset()
        print 'Starte PT2262 Decoder'
        for pulse in self.sequenz.pulse:
            PT.decode(pulse)
        PT.reset()
        
        print 'Starte TCM Decoder'
        for pulse in self.sequenz.pulse:
            TCM.decode(pulse)
        TCM.reset()

        print 'Starte Logilink Decoder'
        for pulse in self.sequenz.pulse:
            Logi.decode(pulse)
        TCM.reset()

        print "Starte OSV2 Decoder bei {} ende bei {}".format(self.decstart,self.decend)
        for cnt in range(self.decstart,self.decend):
            osv2.decode(self.sequenz.pulse[cnt])
        osv2.reset()

        print "Starte Cresta Decoder bei {} ende bei {}".format(self.decstart,self.decend)
        for cnt in range(self.decstart,self.decend):
            cresta.decode(self.sequenz.pulse[cnt])
        cresta.reset()

        # Ausgabe der Pulse, kommagetrennt        
        #for cnt in range(self.decstart,self.decend):
        #     print '{},'.format(self.sequenz.pulse[cnt]),
        """
        print 'Starte Musterdecoder'
        pattDec.chkPattern(self.sequenz.pulse)
        """
        try:
            TST.doTest()
        except:
            print 'Fehler beim Ausführen des Testdecoders.'
        """
        print "Analyse beendet."

    def pruefeDaten(self):
        inconsist = np.where(np.diff(np.sign(self.sequenz.pulse))==0)
        if (not np.size(inconsist)==0):
            print 'Daten sind inkonsistent bei Index' +str(inconsist)
            for xpos in inconsist:
                self.axes.plot((self.sequenz.t[xpos], self.sequenz.t[xpos]), (self.axes.get_ylim()[0], self.axes.get_ylim()[1]), 'r-')
            self.fig.canvas.draw()
        else:
            print u'Daten sind vollständig konsistent'

    def aufnahme(self):
        if (self.serialState == 'connect'):
            self.updateSettings()
            self.aufnahmeButton.configure(relief=Tk.SUNKEN)
            self.fig.canvas.draw()
            self.arduino.switchReceive(1,int(self.pulseMin)) # (scale, pulseMin)
            self.sequenz.setPulse(self.arduino.receive(int(self.samples)))
            self.arduino.switchQuiet() # turn off serial output of arduino to keep comport clean
            sleep(1)
            self.decstart = 0
            self.decend = len(self.sequenz)    
       
            self.aufnahmeButton.configure(relief=Tk.RAISED)
            self.fig.canvas.draw()
            
            self.plot()
        else:
            print 'ComPort nicht geoeffnet.'

    def printSamples(self):
        print self.samplesSpinbox.get()

    def exit_(self):
        self.updateSettings()
        try:
            del self.pa
        except:
            pass
        try:
            self.saveConfig()
        except:
            pass
        print "exit"
        self.root.destroy()

    def saveConfig(self):
        # When adding sections or items, add them in the reverse order of
        # how you want them to be displayed in the actual file.
        # In addition, please note that using RawConfigParser's and the raw
        # mode of ConfigParser's respective set functions, you can assign
        # non-string values to keys internally, but will receive an error
        # when attempting to write to a file or when you get it in non-raw
        # mode. SafeConfigParser does not allow such assignments to take place.
        try:
            self.config.add_section('GUI')
        except: #should catch only duplicates, but don't know how
            pass
        self.config.set('GUI', 'pulsemin', self.pulseMinSpinbox.get())
        self.config.set('GUI', 'samples', self.samplesSpinbox.get())
        self.config.set('GUI', 'comport', self.comPortSpinbox.get())
        self.config.set('GUI', 'messtyp', self.messTyp)
    
        # Writing our configuration file to 'example.cfg'
        try:
            with open(self.configfile, 'wb') as configfile:
                self.config.write(configfile)
        except:
            print 'Fehler beim schreiben des Configfiles, breche ab.'
        
    def loadConfig(self):        
        ret = self.config.read(self.configfile)
        if (ret==[]):
            raise NameError('Keine Configdatei gefunden')           
        # getfloat() raises an exception if the value is not a float
        # getint() and getboolean() also do this for their respective types
        try:
            self.pulseMin = self.config.getint('GUI', 'pulsemin')
            self.samples = self.config.getint('GUI', 'samples')
            self.comPortSelect = self.config.get('GUI', 'comport')
            self.messTyp = self.config.get('GUI', 'messtyp')
        except:
            print 'Fehler im Configfile, breche ab.'
    
class Daten(object):
    def __init__(self):
        self.pulse = np.array([])
        self.t = np.array([])
        self.sig = np.array([])

    def __len__(self):
        return len(self.pulse)        
            
    def save(self, fname):
        np.save(fname, self.pulse)
    
    def exportExcel(self):
        np.savetxt(fname, a, fmt='%d', delimiter=' ', newline='\n', header=fname)
    
    def load(self, fname):
        self.pulse = np.load(fname)
        self.gettsig()
    
    def setPulse(self, pulse):
        self.pulse = pulse
        self.gettsig()
    
    def gettsig(self):
        # Berechnet den Zeitlichen Verlauf aus den gegebenen Pulsweiten
        self.t=np.cumsum(np.abs(self.pulse))
        self.sig = (np.sign(self.pulse)+1)/2
        
# *****************************************************************************

if __name__ == '__main__':
    root = Tk.Tk()
    gui = sequenzAnalyse(root)
    root.mainloop()
    
