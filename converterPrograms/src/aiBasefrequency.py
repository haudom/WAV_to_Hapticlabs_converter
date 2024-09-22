# src: https://www.tensorflow.org/hub/tutorials/spice

import tensorflow as tf
import tensorflow_hub as hub

import numpy as np
import matplotlib.pyplot as plt
import librosa
from librosa import display as librosadisplay




import logging
import math
import statistics
import sys

from IPython.display import Audio, Javascript
from scipy.io import wavfile

from base64 import b64decode

import music21
from pydub import AudioSegment


logger = logging.getLogger()
logger.setLevel(logging.ERROR)

print("tensorflow: %s" % tf.__version__)


EXPECTED_SAMPLE_RATE = 16000
MAX_ABS_INT16 = 32768.0

model = hub.load("https://www.kaggle.com/models/google/spice/TensorFlow1/spice/2")
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

print("tensorflow: %s" % tf.__version__)

# Function that converts the user-created audio to the format that the model 
# expects: bitrate 16kHz and only one channel (mono).
def convert_audio_for_model(user_file, output_file='converted_audio_file.wav'):
  audio = AudioSegment.from_file(user_file)
  audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
  audio.export(output_file, format="wav")
  return output_file


def getFrequencies(audio_samples, sr = EXPECTED_SAMPLE_RATE):

  if sr != EXPECTED_SAMPLE_RATE:
    audio_samples = librosa.resample(audio_samples, orig_sr=sr, target_sr=EXPECTED_SAMPLE_RATE)    


  # We now feed the audio to the SPICE tf.hub model to obtain pitch and uncertainty outputs as tensors.
  model_output = model.signatures["serving_default"](tf.constant(audio_samples, tf.float32))

  pitch_outputs = model_output["pitch"]
  uncertainty_outputs = model_output["uncertainty"]
  return pitch_outputs, uncertainty_outputs

#Sample Frequenz zuordung
#TODO wie groß ist der Abstand?
#def toSampleValue(values):
#   return [[i*abstand, values[i]]for i in range(len(values))]


# Kivertiere die Frequenz in Hz
def outputTooHz(pitch_output):
  # Constants taken from https://tfhub.dev/google/spice/2
  PT_OFFSET = 25.58
  PT_SLOPE = 63.07
  FMIN = 10.0
  BINS_PER_OCTAVE = 12.0
  cqt_bin = pitch_output * PT_SLOPE + PT_OFFSET
  return FMIN * 2.0 ** (1.0 * cqt_bin / BINS_PER_OCTAVE)



# pitch_outputs, uncertainty_outputs = getFrequency(r"viblib\v-10-28-7-26.wav")

# print(toSampleValue(output2hz(pitch_outputs)))

