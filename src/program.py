from main import *
from hlabs import *
from aiBasefrequency import *
import sys
import pathlib

def rms(arr):
    return numpy.sqrt(numpy.mean([value ** 2. for value in arr]))


PLOT_INTERMIN_RESULTS=False

AudioFile = r"viblib/v-09-18-2-7.wav"
OutputFolder = pathlib.Path().resolve()

if len(sys.argv) == 2:
    AudioFile = sys.argv[1]
elif len(sys.argv) == 3:
    AudioFile = sys.argv[1]
    OutputFolder = pathlib.Path(sys.argv[2])
else:
    print("Usage: python program.py <AudioFile> [<OutputFolder>]")
    exit()

audioarr, sr = openFile(AudioFile)

load_model()

breaklist = findBreaks(audioarr, sr)

if not breaklist:
    # TODO
    exit()



if breaklist[0][0] == 0:
    hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, 0, breaklist[0][1]))
else:
    hlabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, 0, breaklist[0][0]))
    hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, breaklist[0][0], breaklist[0][1]))

for i in range(1,len(breaklist)):
    hlabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, breaklist[i-1][1], breaklist[i][0]))
    hlabsBlocks.append(HlabsBlock(HlabsType.BREAK, audioarr, breaklist[i][0], breaklist[i][1]))


#last block
if(breaklist[-1][1] != len(audioarr)):
    hlabsBlocks.append(HlabsBlock(HlabsType.SINUS, audioarr, breaklist[-1][1], len(audioarr)))

#rms amplitude
for block in hlabsBlocks:
    if block.type == HlabsType.SINUS:
        block.amplitude = rms([row[1] for row in getAmplitudes(block.sound_array, sr)])

#rms frequency
for block in hlabsBlocks:
    if block.type == HlabsType.SINUS:
        frequencies, _  = getFrequencies(block.sound_array)
        frequencies = outputTooHz(frequencies)
        block.frequency = rms(frequencies)




print(hlabsBlocks)

