/*
*   LogicAnalyse v2.5 (201412) for Arduino
*   Sketch to use an arduino as a receiver device
*   The Sketch receives (RF, IR) signals on pin 2 and transmits
*   2014  N.Butzek, S.Butzek
*   This sketch focuses on retriving signals, sending it to the pythontool  LogikAnalyse 
*   to allow visual analysing.
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
*/

#define PROGNAME               "Protokoll Analyse"
#define PROGVERS               F("1.2")
#define PIN_RECEIVE            2
#define PIN_SEND               9
#define PIN_LED                13 // Message-LED
#define BAUDRATE               250000  //115200 
#define MSGMARK                32002 //Binary-Markierung für Meldungsende

#include <filtering.h>
#include <Timer1.h>

RingBuffer FiFo(350, 0); // FiFo Puffer
int pLaenge, mLaenge, maxLaenge, scale, pulseMin, writeBin, sendNum; //Beschreibung siehe resetValues()
volatile bool lineMode, showData, pDetect, enReceiver, enSender; //Beschreibung siehe resetValues()
volatile int sendCnt;
String cmdstring = "";

void resetValues(){
  maxLaenge = FiFo.getBuffSize();
  pLaenge = 1000; //Pausenlänge
  mLaenge = 10; // Meldungslänge, Wert muss kleiner sein als Pufferlänge
  maxLaenge = 0; //hängt später vom freien Speicher ab und wird in Setup()beschrieben
  scale = 1; //skalierungsfaktor
  pulseMin = 350; //Mindestpulsdauer
  pDetect = false; //Pausenerkennung
  lineMode = false; //Ausgabe in Zeile(t) oder Spalte/f)
  showData = false; //Ausgabe an Seriell EIN/AUS
  writeBin = false; //Binary an Serial: Reihenfolge: HighByte LowByte
  sendNum = 100; //Anzahl der Werte zu Senden
  enReceiver = false; //Zustandsvariable für Empfänger
  enSender = false; //Zustandsvariable für Sender
}

void blinken() {
  if (!enSender){
    digitalWrite(PIN_LED, true);
    startTimer1(15000L);
  }
}

void setup() {  
  Serial.begin(BAUDRATE);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
  pinMode(PIN_RECEIVE,INPUT);
  pinMode(PIN_LED,OUTPUT);
  pinMode(PIN_SEND,OUTPUT);
  cmdstring.reserve(20);
  printMemory();
  resetValues();  
  enableReceive();
}

void loop() {
  static int aktVal;
  static int oldVal;
  if (!enSender) {
    while (FiFo.getNewValue(&aktVal)) {
      if (pDetect) { // check for pause to determin messages
        if ((abs(aktVal) >= (pLaenge)) && !(aktVal == oldVal)) {// Pause erkannt => Meldung mit mLaenge Werte im Puffer
            printMsg();
            blinken();
        }
        oldVal = aktVal;
      } else { //print every value in the buffer
          printVal(&aktVal);
      }
    }
    if(Serial.available())  serialEvent();
  } else {
    delay(100);
  }
}
