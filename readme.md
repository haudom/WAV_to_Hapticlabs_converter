# Über
Dieses Repository ist im Rahmen meiner Bachelorarbeit entstanden.
Es enthält:
- Ein Programm um WAV-Dateien in ein Hapticlabs kompatibles Format umzuwandeln und zurück
- Von der [VibViz - Datenbank](https://github.com/derikon/VibViz-Dataset) umgewandelte Daten
- Jupyter Notebook zum Trainieren eines Llama3 Modelles zum Generieren von mit Hapticlabs kompatiblen vibrotaktilen Mustern
- Jupyter Notebook zum Evaluieren der Trainiereten Modelle
- Jupyter Notebook zum Evaluieren des Umwandlungsprogrammes
- Jupyter Notebook zum Evaluieren der konverteirten Daten
- Von Modellen gemeroerte Daten zur Evaluierung

WAV_to_Hapticlabs_converter erlaubt es WAV-Audiodateien in von [Habticlabs](https://www.hapticlabs.io/hapticlabs-studio) lesbare Dateien zu konvertieren.

Dieser Konverter wurde für die [VibViz - Datenbank](https://github.com/derikon/VibViz-Dataset) optimiert. Die resultierenden Daten sind verlustbehaftet.

# Aufbau des Repository
```
+---converterPrograms
|   \---src
|           program.py - wav zu Json konvertierer
|           jsonToWAV.py - Json zu wav konvertierer
\---Datenanalyse
|       analyseData.ipynb - Analyser der VibViz Datenbank mit hilfe von Netzwerkgraphen auf verschiedene Eigenschaften
|       übersichtVibViz.ipynb - Einfache Tabelle mit Blockanzahl, Anuzahl der Pausen, Anuahl der Sinusblöcke und Dauer des Signals
\---Evaluierung
|   \---compareSignals
|   |           comparAllSignals.ipynb - Evaluierung der Umwandlung mittels mean absolute error und Standartabweichung
|       auswertungLLM.ipynb - Vergleich der generierten mit den originalen Signalen bezüglich Wahrscheinlichkeitsdichtefunktion und Abstand
|       AuswertungBegriffe.xlsx - Exceltabellen mit loss daten und Auswertungsergebnisse anhand von Begriffen
|       DatenFürVerteilungsUndAbstandsBerechnung.json - Generierte Daten für die Evaluierung mittels Wahrscheinlichkeitsdichtefunktion und Abstand
|       one-shot-instructed.json - Mittels In-Context learning generierte Daten für Auswertung an Begriffen
\---model training
|       TrainData - Umgewandelte viblib Dateien und Version 1 und Version 2
|        Kopie von Alpaca + Llama-3 8b Unsloth 2x faster finetuning.ipynb - Training der Modelle
|       prompts.json - Sätze/Eingaben, mit denen das Modell trainiert wurde.
|       untrainedPromt.txt - Prompt, mit dem das Modell per In-Context Learning zum Genereiren von Vibraionsmustern gebracht wurde
```

# Umwandlungsprogramm / WAV_to_Hapticlabs_converter

## Installation
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

## Benutzung
Die Umwandlung ist in beide Richtungen möglich:
### Umwandlung von .wav zu .json
Wenn noch nicht getan, aktiviere die virtuelle Umgebung
```bash
/path/to/new/virtual/environment/Scripts/activate
```
Starte program.py mit aktivierter Umgebung
```bash
python /path/to/project/converterPrograms/src/program.py <WAV dict path | WAV file path> [<JSON output path>]
# WAV dict Path: Pfad zum Ordner mit WAV-Dateien
#   ODER WAV file path: Pfad zur WAV-Datei
# output path: Pfad zum Ordner in dem JSON-Dateien gespeichert werden
```
### Umwandlung von .json zu .wav
Zur Umwanldung von JSON zu WAV kann jsonTOWavProgram.py verwendet werden:
Wenn noch nicht getan, aktiviere die virtuelle Umgebung:
```bash
/path/to/new/virtual/environment/Scripts/activate
```

Starte jsonToWavProgram.py mit aktivierter Umgebung
```bash
python /path/to/project/converterPrograms/src/jsonToWavProgram.py <JSON dict path | JSON file path> [<WAV output path>]
# dict Path: Pfad zum Ordner mit WAV-Dateien
#   ODER file path: Pfad zur WAV-Datei
# output path: Pfad zum Ordner in dem JSON-Dateien gespeichert werden
```


## Meilensteine

- [x] Pausen erkennen
- [x] Frequenz erkennen
- [x] Amplituden erkennen
- [x] Estellung hlabs.json

## Optionale Meilensteine

- [ ] Signalform erkennen
- [ ] Fading
