### Installation
1. Dateien aus GitHub herunterladen und in gewünschtem Verzeichnis ablegen
2. Konsole öffnen
   - Unter Windows: 
     - Windows + R
     - In eingabefeld "cmd" eingeben und bestätigen
   - Unter Mac OS:
     - Command + Leertaste
     - In Eingabefeld "terminal" eingeben und bestätigen
3. Prüfen ob Python installiert ist
```bash
python --version
```
oder 
```bash
python3 --version
```
Wenn Python vorhanden ist, dann wird die entsprechende Version ausgegeben. 
Sollte Python nicht erkannt werden, dann können Sie unter [python.org](https://www.python.org)
die neueste Version von Python herunterladen und installieren.
Nach erfolgreicher Installation können Sie durch Eingabe des oben aufgeführten
Befehls prüfen ob Python erfolgreich installiert wurde.
4. Prüfen ob pip installiert ist. Dies sollte automatisch mit Python installiert werden.
```bash
pip --version
```
oder
```bash
pip3 --version
```
Wenn pip vorhanden ist, dann wird die entsprechende Version ausgegeben.
5. In Konsole zum Verzeichnis navigieren, in dem die setup.py Datei liegt.
Zur Navigation den Befehl "cd" benutzen.
```bash
#unter Windows
cd C:\Pfad\zum\Verzeichnis\AtemzugValidierungPYTHON-master

#unter Mac
cd /Users/Benutzername/Pfad/zum/Verzeichnis/AtemzugValidierungPYTHON-master
```
6. Mit dem Befehl "dir" (unter Windows) oder "ls" (unter Mac) können Sie prüfen, ob Sie sich in dem Verzeichnis mit der
setup.py Datei befinden. Der Befehl listet alle Dateien im Verzeichnis auf.
```bash
#unter Windows
dir

#unter Mac
ls
```
7. Wenn Sie sich im richtigen Verzeichnis befinden,
dann führen Sie die Installation mit dem "pip" Befehl durch. 
```bash
pip install .
```
8. Jetzt ist das Programm einsatzbereit. 
Sie können das Programm mit folgendem Befehl in der Konsole starten:
```bash
runazv
```