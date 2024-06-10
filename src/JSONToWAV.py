from hlabs import *
import numpy
from scipy.io.wavfile import write
import pathlib
import os

###################################################################################################################
# Generiert aus Hlabs-JSON Wav-Datei
# Parameter: filepath: Pfad zur JSON-Datei
# Samplerate: Samplerate der WAV-Datei
###################################################################################################################

def jsonToWav(filepath, sample_rate = 16000):
    audio_arr = []


    ample_rate = 16000 # the number of samples per second 
    hlabsBlocks = readFromJson(filepath)

    for block in hlabsBlocks:

        duration_in_seconds = block.duration / 1000
        if block.type == HlabsType.SINUS:
            t = numpy.linspace(0, duration_in_seconds, int(sample_rate *duration_in_seconds), endpoint=False)  # Time array
            audio_arr.extend(block.amplitude * numpy.sin(2 * numpy.pi * block.frequency * t))  # Sine wave formula
        else:
            audio_arr.extend(numpy.zeros(int(sample_rate * duration_in_seconds)))

    audio_arr = numpy.float32(audio_arr)

    #Speichern als wav
    write(os.path.splitext(filepath)[0] + ".wav", sample_rate, audio_arr)
