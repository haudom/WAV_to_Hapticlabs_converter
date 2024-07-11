from main import *
from hlabs import *
from aiBasefrequency import *
import sys
import pathlib
import matplotlib.pyplot as plt


def program(audioFile : pathlib.Path, outputFolder : pathlib.Path):

    hlabsBlocks = []
    audioarr, sr = openFile(audioFile)

    breaklist = findBreaks(audioarr, sr)

    print(len(audioarr))
    print(breaklist)
    print("")

    # create blocks

    if not breaklist:
        #full audio file as block
        hlabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, 0, len(audioarr)))

        #frequency
        frequencies,_ = getFrequencies(audioarr, sr)
        frequencies = outputTooHz(frequencies)
        hlabsBlocks[0].frequency = rms(frequencies)   
        #amlitude
        amplitdues = getAmplitudes(audioarr, sr)
        hlabsBlocks[0].amplitude = rms(interpolate(amplitdues,len(audioarr)))
        #duration in ms
        hlabsBlocks[0].duration = hlabsBlocks[0].duration / sr * 1000
        toJson(hlabsBlocks, outputFolder / audioFile.with_suffix(".json").name)
        return



    if breaklist[0][0] == 0:
        hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, 0, breaklist[0][1]))
    else:
        hlabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, 0, breaklist[0][0]))
        hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, breaklist[0][0], breaklist[0][1]))

    for i in range(1,len(breaklist)):
        hlabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, breaklist[i-1][1], breaklist[i][0]))
        hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, breaklist[i][0], breaklist[i][1]))


    #last block
    if(breaklist[-1][1] != len(audioarr)-1):
        hlabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, breaklist[-1][1], len(audioarr)-1))

    #rms amplitude
    for block in hlabsBlocks:
        if block.type == HlabsType.SINUS:
            block.amplitude = rms(interpolate(getAmplitudes(block.sound_array, sr),len(block.sound_array)))

    #rms frequency
    for block in hlabsBlocks:
        if block.type == HlabsType.SINUS:
            frequencies, _  = getFrequencies(block.sound_array)
            frequencies = outputTooHz(frequencies)
            block.frequency = rms(frequencies)

    #duration to ms
    for block in hlabsBlocks:
        block.duration = block.duration / sr * 1000

    print(hlabsBlocks)

    #dump json
    toJson(hlabsBlocks, outputFolder / audioFile.with_suffix(".json").name)

    

#Plotten ausschalten, ansosten steigt speicherverbrauch ins undendliche wenn mehrere Dateien verarbeitet werden
PlotInterminResults(False)

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
    print("Usage: python program.py <AudioFile|Folder> [<OutputFolder>]")
    exit()

if not AudioPath.exists():
    print("Path", AudioPath, "does not exist")
    exit()
if OutputFolder.is_file():
    print("OutputFolder must be a Folder")
    exit()


# Konvertierung starten
if AudioPath.is_file():
    program(AudioPath, OutputFolder)
if AudioPath.is_dir():
    for file in AudioPath.iterdir():
        if file.is_file():
            if os.path.splitext(file)[1] == ".wav":
                program(file, OutputFolder)