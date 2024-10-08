# Version 1.6 - 16.08.2024
1. Peak Ermittlung der einzelnen Atemzüge wurde um 1 Index erhöht, um gesamten Atemzug 
zu betrachten

# Version 1.5.1 - 08.08.2024
1. Code Anpassungen (keine funktionalen Änderungen)

# Version 1.5 - 08.08.2024
1. Code Anpassungen 
   - Plot-Größe wurde erweitert

# Version 1.4 - 08.08.2024
1. Code Anpassungen 
   - Plot-Fenster Breite passt sich der Breite des Hauptfensters an.
   - Plot-Größe wurde erweitert

# Version 1.3.6 - 07.08.2024
1. Code Anpassungen (keine funktionalen Änderungen)

# Version 1.3.5 - 06.08.2024
1. Code Anpassungen (keine funktionalen Änderungen)

# Version 1.3.4 - 05.08.2024
1. Code Anpassungen (keine funktionalen Änderungen)

# Version 1.3.3 - 03.08.2024
1. Code Anpassungen (keine funktionalen Änderungen)

# Version 1.3.2 - 01.08.2024
1. Code Anpassungen (keine funktionalen Änderungen)

# Version 1.3.1 - 29.07.2024
1. Code Anpassungen (keine funktionalen Änderungen)
2. README Anpassung

# Version 1.3 - 27.07.2024
1. GUI für Windows angepasst
   - GUI Elemente werden auf Windows Systemen speziell angepasst

# Version 1.2 - 26.07.2024
1. Fokus wird von Eingabefeldern durch Klicken auf Buttons "Intervall anzeigen" und "Intervall speichern" entfernt
   - Navigation mit den buttons funktioniert direkt nach Bestätigung der Eingaben

2. Eingabefeld für Intervalldauer kann auch leer gelassen und bestätigt werden. Keine Aktion wird ausgeführt und kein Fehler generiert.

3. README angepasst.
   - Sektion zum Aktualisieren des Projekts ohne eine vollständige Installation eingefügt.
     - Projekt kann mit folgendem Befehl aktualisiert werden:
   ```bash
   pip install --upgrade git+https://github.com/LordYev/AtemzugValidierungPYTHON
   ```
   - Darstellung des Fensters zur erneuten Berechnung des Beatmungsbereiches eingefügt.

# Version 1.1 - 25.07.2024
1. Info-Label mit Grenzwerten angepasst:
    - Altes Label wird gelöscht bevor ein neues erzeugt wird (keine Überlappung mehr)
  
2. Intervall plotten
    - Intervall wird jetzt nur geplottet, 
  wenn das Eingabefeld gefüllt ist. 
  Kein Fehler mehr, wenn Eingabefeld leer ist.

3. Navigation vorwärts & rückwärts
    - Die Navigation mit den Pfeiltasten funktioniert jetzt nur, 
  wenn man sich in einem Intervall befindet. 
  Wenn der gesamte Datensatz angezeigt wird, passiert nichts mehr → 
  kein Fehler wird erzeugt
    - Navigation funktioniert nicht mehr, 
  wenn ein Eingabefeld ausgewählt ist. 
  Zeiger im Eingabefeld kann jetzt mit Pfeiltasten bewegt werden, 
  ohne den Plot zu ändern.

# Version 1.0 - 23.07.2024
- Programm zur Installation freigegeben