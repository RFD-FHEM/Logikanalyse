void receiveInterrupt() {
  static unsigned long Time;
  static unsigned long lastTime = micros();
  static long duration;
  static int sDuration;
  Time = micros();
  bool state = digitalRead(PIN_RECEIVE);
  duration = Time - lastTime;
  lastTime = Time;
  if (duration >= pulseMin) {//kleinste zulässige Pulslänge
    if (duration <= (32000)) {//größte zulässige Pulslänge, max = 32000
      sDuration = int(duration/(float)scale); //das wirft bereits hier unnütige Nullen raus und vergrößert den Wertebereich
    }else {
      sDuration = 32001; // Maximalwert
    }
    if (state) { // Wenn jetzt high ist, dann muss vorher low gewesen sein, und dafür gilt die gemessene Dauer.
      sDuration=sDuration*-1;	  //sDuration |=  (1 << 15);

    }
    FiFo.addValue(&sDuration);
  } // else => trash
}

void enableReceive() {
  if (!enSender) {
    attachInterrupt(0,receiveInterrupt,CHANGE);
    enReceiver = true; // just for state info
  }
}

void disableReceive() {
  detachInterrupt(0);
  enReceiver = false; // just for state info
}


