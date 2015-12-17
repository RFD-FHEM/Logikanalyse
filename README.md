# Logikanalyse
Python Tool  + Arduino Sketch für Logik Analyse


hier Logik Analyse. Läuft auf dem nano/uno etc.

Für das Python Tool "LogikAnalyse"  pythonxy  und noch pyserial für Windows installieen.
Damit laufen die Programme und man kann mit dem Sketch (Arduino) kommunizieren.   

Der Sketch kompiliert nur in der Arduino Ide und nennt sich auch LogikAnalyse. Er Läuft mit einer Baudrate von 250000, also nicht wundern wenn mit der IDE die serielle Ausgabe nix taugt.  

Wer die grundsätzliche Funktion des Sketches seriell ansehen möchte, musst Du das Kommando showData1 an den Arduino senden. Dann gibt er die gemessenen Pulse zeilenweise aus.  
Das Python Programm nutzt ein binäres format, also wieder umstellen oder einfach den Arduino resetten.

Das Aufzeichnen läuft für die eingestellte Anzahl "Samples". Es reicht meist gut, wenn man aufzeichnen startet und dann gleich den Sensor auch was senden lässt.  Es dauert meist noch 2 Sekunden bis dann im Python tool auch das Signal erscheint. Die Funktion Pruefe, untersucht das Signal auf valide high, low folgen.  

Per Default werden keine Pulse <300 us angenommen. Das kann bei Bedarf über das Python Tool konfiguriert werden.   

So viel Spaß. Hoffe  das tool funktioniert einigermaßen.


Wie compilere ich den Sketch?

Die Dateien aus dem git clonen oder als ZIP herunterladen.
Danach hat man einen Ordner Logikanalyse in dem sich die Arduino Dateien befinden.

Bevor der Sketch compiliert, ist es notwendig die Dateien aus dem lib Ordner in den Ordner der Arduino Librarys zu kopieren:
Dies liegen per default in folgendem Ordner: "My Documents\Arduino\libraries\"
Dort müssen die Ordner Timer1 und Filtering kopiert werden. Hat man dort eine der Libs schon, kann man diese überspringen.
Danach muss man die Arduino IDE neu starten, sonst werden die libs nicht erkannt.
Details zum Installieren der Libs unter: https://www.arduino.cc/en/Guide/Libraries 

