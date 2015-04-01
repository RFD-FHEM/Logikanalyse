# Logikanalyse
Python Tool  + Arduino Sketch für Logik Analyse


hier Logik Analyse. Läuft auf dem nano/uno etc.

Für das Python Tool "LogikAnalyse"  pythonxy  und noch pyserial für Windows installieen.
Damit laufen die Programme und man kann mit dem Sketch kommunizieren   

Der Sketch kompiliert nur in der Arduino Ide und nennt sich auch LogikAnalyse. Er Läuft mit einer Baudrate von 250000, also nicht wundern wenn mit der IDE die serielle Ausgabe nix taugt.  

Wer die grundsätzliche Funktion des Sketches seriell ansehen möchte, musst Du das Kommando showData1 an den Arduino senden. Dann gibt er die gemessenen Pulse zeilenweise aus.  
Das Python Programm nutzt ein binäres format, also wieder umstellen oder einfach den Arduino resetten.

Das Aufzeichnen läuft für die eingestellte Anzahl "Samples". Es reicht meist gut, wenn man aufzeichnen startet und dann gleich den Sensor auch was senden lässt.  Es dauert meist noch 2 Sekunden bis dann im Python tool auch das Signal erscheint. Die Funktion Pruefe, untersucht das Signal auf valide high, low folgen.  

Per Default werden keine Pulse <300 us angenommen. Das kannst bei Bedarf über das Python Tool konfigurieren   

So viel Spaß. Hoffe  das tool funktioniert einigermaßen.
