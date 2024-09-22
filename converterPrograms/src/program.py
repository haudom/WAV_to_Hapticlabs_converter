from main import *
from hlabs import *
from aiBasefrequency import *
import sys
import pathlib
import matplotlib.pyplot as plt



def createSinusBlocks(audioarr,start,stop,sr, halabsBlocks, rawAmplitudes,frequencies):
    i = 0
    _ , blocks = simpleBlockByAmplitude(audioarr, rawAmplitudes, sr, start, stop)
    for block in blocks:
        print("block",block)
        subBlocks = simpleBlockByFrequency(frequencies, sr, block[0], block[1])
        subBlocks[-1][1] +=1 #vermeiden dass index am Ende vom Amplitudenblock 2 mal abgezogen wird
        for subBlock in subBlocks:
            i = i+1
            print("i",i)
            print("sub",subBlock)
            halabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, subBlock[0], subBlock[1]))



def program(audioFile : pathlib.Path, outputFolder : pathlib.Path):

    PlotInterminResults(False)

    hlabsBlocks = []
    audioarr, sr = openFile(audioFile)
    frequencies, _ = getFrequencies(audioarr)
    frequencies = outputTooHz(frequencies)
    frequencies = numpy.interp(range(0,len(audioarr)), numpy.arange(0,len(frequencies)*512,512),frequencies,right=frequencies[-1])
    rawAmplitudes = getAmplitudes(audioarr, sr)
    amplitdues = interpolate(rawAmplitudes, len(audioarr))

    breaklist = findBreaks(audioarr, sr)

    print(len(audioarr))
    print(breaklist)
    print("")

    # create blocks

    if not breaklist:
        #full audio file as block
        createSinusBlocks(audioarr,0,len(audioarr),sr,hlabsBlocks,rawAmplitudes,frequencies)


    else:
        if breaklist[0][0] == 0:
            hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, 0, breaklist[0][1]))
        else:
            createSinusBlocks(audioarr,0,breaklist[0][0],sr,hlabsBlocks,rawAmplitudes,frequencies)
            hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, breaklist[0][0], breaklist[0][1]))

        for i in range(1,len(breaklist)):
            createSinusBlocks(audioarr,breaklist[i-1][1],breaklist[i][0],sr,hlabsBlocks,rawAmplitudes,frequencies)
            hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, breaklist[i][0], breaklist[i][1]))


        #last block
        if(breaklist[-1][1] != len(audioarr)-1):
            createSinusBlocks(audioarr,breaklist[-1][1],len(audioarr),sr,hlabsBlocks,rawAmplitudes,frequencies)

    #Block amplitudes and frequencies
    for block in hlabsBlocks:
        if block.type == HlabsType.SINUS:
            block.amplitude = rms(amplitdues[block.start_time:block.end_time])
            block.frequency = rms(frequencies[block.start_time:block.end_time])


    #duration to ms
    for block in hlabsBlocks:
        block.duration = block.duration * 1000 / sr

    print(hlabsBlocks)

    #dump json
    toJson(hlabsBlocks, outputFolder / audioFile.with_suffix(".json").name)

    




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