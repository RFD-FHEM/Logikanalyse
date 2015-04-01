void HandleCommand(String cmd)
{
  int val;
  String strVal;
  // ?: Alle Kommandos anzeigen
  if (cmd.equals("?"))
  {
    Serial.println(F("?: Hilfe"));
    Serial.println(F("pause30000           : Pausenlaenge 30000"));
    Serial.println(F("length400            : Meldungslaenge 400"));
    Serial.println(F("pulseMin250          : Mindestpulslänge"));
    Serial.println(F("scale10              : Skalierungsfaktor 10"));
    Serial.println(F("pDetect0 /pDetect1   : pause detection"));
    Serial.println(F("showData0 /showData1 : print data to serial port"));
    Serial.println(F("writeBin0 /writeBin1 : print data to serial port as binary, note that this also sets lineMode0"));
    Serial.println(F("sync                 : send sync signal in binary mode"));
    Serial.println(F("send1000             : Sende 1000 Werte"));
    Serial.println(F("lineMode0 /lineMode1 : print data in lines(1) or in row(0)"));
    Serial.println(F("receiver0 /receiver1 : enable/disable receiver"));
    Serial.println(F("dump                 : Dump values"));
    Serial.println(F("reset                : Reset to initial values"));
    Serial.println();
    blinken();
  }
  // sendXXXX: sende (RF) Anzahl von Werte
  else if (cmd.startsWith("send")) {
    strVal = cmd.substring(4);
    if (strVal.length()>0){
      val = strVal.toInt();
      sendNum = constrain(val, 0, 32000);
      enableSender();
    }
  }
  // pauseXXXX: nur erkannte Meldungen senden. pause4000 => Meldungen erkennen mit Pause = (int)4000s
  else if (cmd.startsWith("pause")) {
    strVal = cmd.substring(5);
    if (strVal.length()>0){
      val = strVal.toInt();
      pLaenge = constrain(val, 0, 32000);
      if (pLaenge <=0)
        pDetect=false;// turn off pause-detection
    }
    blinken();
  }
  // lengthXXXX: Laenge für Meldungen setzen. L400 => Länge der Meldungen 400 Samples
  else if (cmd.startsWith("length")) {
    strVal = cmd.substring(6);
    if (strVal.length()>0){
      val = strVal.toInt();
      mLaenge = constrain(val, 0, maxLaenge);
    }
    blinken();
  }
  // scaleXXXX: Skalierungsfaktor
  else if (cmd.startsWith("scale")) {
    strVal = cmd.substring(5);
    if (strVal.length()>0){
      val = strVal.toInt();
      scale = constrain(val, 0, 1000);
    }
    blinken();
  }  
  // pulseMin: Mindestpulslänge
  else if (cmd.startsWith("pulseMin")) {
    strVal = cmd.substring(8);
    if (strVal.length()>0){
      val = strVal.toInt();
      pulseMin = constrain(val, 0, 1000);
    }
    blinken();
  }  
  // dataX: Data an Serial EIN/AUS
  else if (cmd.startsWith("showData")) { 
    strVal = cmd.substring(8);
    if (strVal.length()>0){
      val = strVal.toInt();
      if (val==1){
        showData = true;
      } else {
        showData = false;
      }
    }
    blinken();
  }
  // binaryX: Send binary data to serial
  else if (cmd.startsWith("writeBin")) { 
    strVal = cmd.substring(8);
    if (strVal.length()>0){
      val = strVal.toInt();
      if (val==1){
        lineMode = false;
        writeBin = true;
      } else {
        writeBin = false;
      }
    }
    blinken();
  }
  // pdetect: pause detection EIN/AUS
  else if (cmd.startsWith("pDetect")) { 
    strVal = cmd.substring(7);
    if (strVal.length()>0){
      val = strVal.toInt();
      if (val==1){
        pDetect = true;
      } else {
        pDetect = false;
      }
    }
    blinken();
  }
  // line: print data in lines(true) or in row(f)
  else if (cmd.startsWith("lineMode")) { 
    strVal = cmd.substring(8);
    if (strVal.length()>0){
      val = strVal.toInt();
      if (val==1){
        lineMode = true;
      } else {
        lineMode = false;
      }
    }
    blinken();
  }
  // receiverX: Receiver EIN/AUS
  else if (cmd.startsWith("receiver")) { 
    strVal = cmd.substring(8);
    if (strVal.length()>0){
      val = strVal.toInt();
      if (val==1){
        enableReceive();
      } else {
        disableReceive();
      }
    }
    blinken();
  }  
  // Dump
  else if (cmd.equals("dump")) {
    Serial.println(); 
    Serial.print(F("enReceiver:")); Serial.print(enReceiver);
    Serial.print(F(", enSender:")); Serial.print(enSender);
    Serial.print(F(", showData:")); Serial.print(showData);
    Serial.print(F(", lineMode:")); Serial.print(lineMode);
    Serial.print(F(", pDetect:")); Serial.print(pDetect);
    Serial.print(F(", writeBin:")); Serial.print(writeBin);
    Serial.println();    
    Serial.print(F("pause:")); Serial.print(pLaenge);
    Serial.print(F(", length:")); Serial.print(mLaenge);
    Serial.print(F(", scale:")); Serial.print(scale);
    Serial.print(F(", Buffersize:")); Serial.print(maxLaenge);
    Serial.print(F(", pulseMin:")); Serial.print(pulseMin);
    Serial.println();    
    blinken();
  }
  // reset: Reset values
  else if (cmd.equals("reset")) {
    resetValues();
    blinken();
  }
  // sync
  else if (cmd.equals("sync")) {
    for (int i = 1; i <= 4; ++i) {
      Serial.write((byte)0xFF);
    }
    Serial.write((byte)0);   
  }
  // sync
  else if (cmd.equals("test")) {
    for (int i = -2500; i <= 2500; i+=50) {
      Serial.write(highByte(i));
      Serial.write(lowByte(i));
    }
    Serial.write((byte)0);   
  }
  // reset: Reset values
  else if (cmd.equals("reset")) {
    resetValues();
    blinken();
  }
}
void serialEvent()
{
  while (Serial.available())
  {
    char inChar = (char)Serial.read();
    switch(inChar)
    {
    case '\n':
    case '\r':
    case '\0':
    case '#':
      HandleCommand(cmdstring);
      cmdstring = "";
      break;
    default:
      cmdstring += inChar;
    }
  }
}



