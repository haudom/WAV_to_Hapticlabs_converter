# Über
WAV_to_Hapticlabs_converter erlaubt es WAV-Audiodateien in von [Habticlabs](https://www.hapticlabs.io/hapticlabs-studio) lesbare Dateien zu konvertieren.

Dieser Konverter wurde für die [VibViz - Datenbank](https://github.com/derikon/VibViz-Dataset) optimiert. Die resultierenden Daten sind verlustbehaftet.

# Installation
1. [Installiere Python](https://www.python.org/downloads/)
2. Erstelle eine virtuelle Umgebung:
```bash
python -m venv /path/to/new/virtual/environment
```
3. Aktiviere diese Umgebung
```bash
/path/to/new/virtual/environment/Scripts/activate
```
4. Mit aktivierter Umgebung installiere die benötigten Pakete
```bash
 pip install -r requirements.txt
```

# Benutzung
Aktiviere die virtuelle Umgebung
```bash
/path/to/new/virtual/environment/Scripts/activate
```
Starte program.py mit aktivierter Umgebung
```bash
python /path/to/project/src/program.py <dict path | file path> [<JSON output path>]
# dict Path: Pfad zum Ordner mit WAV-Dateien
#   ODER file path: Pfad zur WAV-Datei
# output path: Pfad zum Ordner in dem JSON-Dateien gespeichert werden
```

# Meilensteine

- [x] Pausen erkennen
- [x] Frequenz erkennen
- [x] Amplituden erkennen
- [x] Estellung hlabs.json

# Optionale Meilensteine

- [ ] Signalform erkennen
- [ ] Fading
