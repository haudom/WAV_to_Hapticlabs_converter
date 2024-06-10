from JSONToWAV import *
import sys

# Abfrage der Eingabeparameter
OutputFolder = pathlib.Path().resolve()

if len(sys.argv) == 2:
    AudioPath = pathlib.Path(sys.argv[1])
elif len(sys.argv) == 3:
    AudioPath = pathlib.Path(sys.argv[1])
    OutputFolder = pathlib.Path(sys.argv[2])

    if not OutputFolder.exists():
        OutputFolder.mkdir()

    elif OutputFolder.is_file():
        print("OutputFolder must be a Folder")
        exit()

else:
    print("Usage: python program.py <JSON-File|Folder> [<OutputFolder>]")
    exit()

if not AudioPath.exists():
    print("Path", AudioPath, "does not exist")
    exit()
if OutputFolder.is_file():
    print("OutputFolder must be a Folder")
    exit()


# Konvertierung starten
if AudioPath.is_file():
    jsonToWav(AudioPath, OutputFolder)
if AudioPath.is_dir():
    for file in AudioPath.iterdir():
        if file.is_file():
            if os.path.splitext(file)[1] == ".json":
                jsonToWav(file, OutputFolder)