void printMemory(){
  Serial.println(F("Startup:"));
  Serial.print(F("# Bytes / Puffer: "));
  Serial.println(sizeof(int)*FiFo.getBuffSize());
  Serial.print(F("# Len Fifo: "));
  Serial.println(FiFo.getBuffSize());
}

void printMsg(){
  if (showData){
    int *sendVal;
    FiFo.setFReadPointerToRead(-mLaenge); //Freien Lesezeiger auf den ersten Wert (-mLänge) der gewünschten Sequenz setzen
    for (int i = 1; i <= mLaenge; ++i) {
      sendVal = FiFo.getNextValue();
      printVal(sendVal);
    }
    if (writeBin){
      Serial.write(highByte(MSGMARK));
      Serial.write(lowByte(MSGMARK));
    } else {
      Serial.println(".");
    }
  }
}

void printVal(int *sendVal){
  if (showData){ //Pufferinhalt anzeigen 
    if (lineMode) {// in line
      Serial.print(*sendVal);
      Serial.print(", ");
    } else { //or row
      if (writeBin){
        if (*sendVal==0){
          *sendVal =1;
        }
        Serial.write(highByte(*sendVal));
        Serial.write(lowByte(*sendVal));
      } else {
        Serial.println(*sendVal);
      }
    }
  }
}

