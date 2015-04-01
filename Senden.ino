void enableSender(){
  disableReceive();
  FiFo.resetBuffer();
  enSender = true; 
  int receiveNum = sendNum;
  sendCnt = 0;
  while (receiveNum > 0){
    if (Serial.available()>=2){
      byte hByte = Serial.read();
      byte lByte = Serial.read();
      int val = (hByte<<8) | lByte;
      FiFo.addValue(&val);
      receiveNum--;
    }
    if ((receiveNum-sendCnt)>200 | receiveNum==0) { // Puffer halb voll oder alle Daten empfangen
      digitalWrite(PIN_SEND,LOW); //Sender ausschalten
      startTimer1(1L); // Sendevorgang starten
    }
  }  
}

ISR(timer1Event) // Wenn enSender==frue, sendet die Daten im FiFo-Puffer, wenn enSender==false, Blink-LED ausschalten
{
  static int aktVal;
  if (FiFo.getNewValue(&aktVal) & enSender){
    (aktVal>0) ? digitalWrite(PIN_SEND,HIGH) : digitalWrite(PIN_SEND,LOW);
    (aktVal>0) ? digitalWrite(PIN_LED,HIGH) : digitalWrite(PIN_LED,LOW);
    startTimer1((unsigned long)aktVal);
    sendCnt++;
    if (sendCnt > sendNum)
      enSender = false; //Alle Werte gesendet, sende(Verarbeitung) beenden
  } else {
    digitalWrite(PIN_SEND,LOW); //Sender ausschalten
    digitalWrite(PIN_LED,LOW); //LED ausschalten
    enSender = false; //break sending operation
  }  
}
