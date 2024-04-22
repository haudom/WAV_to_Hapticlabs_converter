import librosa
import os.path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy
import audioflux
import scipy



PLOT_INTERMIN_RESULTS : bool = True #Zwischenschritte Plotten?

fig : int = 0

##############################################################################
# WAV Datei öffnen
##############################################################################
def openFile(filename):
  # Check if file exists
  if os.path.exists(filename):
    print("File", filename, "exists.")
  else:
    print("File", filename, "does not exist")
    exit()
  # 2. Load the audio as a waveform `y`
  #    Store the sampling rate as `sr`
  return librosa.load(filename)
##############################################################################



##############################################################################
# Tiefpass Filter
##############################################################################
def lowPassFilter(audio_arr, sr):
  cutoff = 50 # Low Pass Filterfrequenz in HZ
  nyq = 0.5 * sr
  normal_cutoff = cutoff / nyq
  order = 2 # Filter Ordnung
      # Get the filter coefficients 
  b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
  return scipy.signal.filtfilt(b, a, audio_arr)
##############################################################################



##############################################################################
# Findest stellen mit einer längeren Folge von niedrigen Pegeln (Pausen)
##############################################################################
def findBreaks(audio_arr):
  index = -1

  minBreakTime = 100 # in samples
  toleranz = 0.007
  breaksList = []

  for i, value in enumerate(audio_arr):

    if value < toleranz and value > -toleranz:
      if index == -1:
        index = i
    else:
      if i - index >= minBreakTime and index != -1:
        breaksList.append([index,i])
      index = -1

  if len(audio_arr) - index >= minBreakTime and index != -1:
    breaksList.append([index,len(audio_arr)])

  if PLOT_INTERMIN_RESULTS:
## Plotten der gefundenen Pausen
    global fig
    plt.figure(fig)
    for breaks in breaksList:
      if len(breaks)==2:
        plt.gca().add_patch(Rectangle((breaks[0],-1),width=breaks[1]-breaks[0],height=2, facecolor = 'yellow', edgecolor="green"))
    plt.plot(audio_arr)
    fig += 1

  return breaksList
###############################################################################



###############################################################################
# Blöcke über Signalamplituden bilden
################################################################################
def findBlocksbyAmplitude(audio_arr,sr):
  #frame_length = sr/10  -- frequenzen bis 10 HZ werden korrekt verarbeitet
  frame_length : int = int(sr/25)
  hop_length : int = int(frame_length/4)
  audio_rms_arr = librosa.feature.rms(y=audio_arr, frame_length=frame_length, hop_length=hop_length)
  local_minima_rms = scipy.signal.argrelextrema(audio_rms_arr[-1], numpy.less)
  local_minima_rms =  [hop_length*minimum for minimum in local_minima_rms]


  if PLOT_INTERMIN_RESULTS:
    global fig
    plt.figure(fig)
    plt.plot(audio_arr)
    plt.plot([i * hop_length for i in range(len(audio_rms_arr[-1]))],audio_rms_arr[-1]) 
    plt.vlines(x=local_minima_rms[0], ymin=-1, ymax=1, color="red")
    fig +=1

  return numpy.split(audio_arr, local_minima_rms[0])


###############################################################################



##############################################################################
# Audio Array bei pausen teilen
##############################################################################
def splitAudioArrAtBreaks(audio_arr, breaksList):
  # anfangsbedingungen
  if len(audio_arr) <= 0: return
  if len(breaksList) <= 0: return

  audio_blocks = [] #audio Blöcke. Audio Array geteil an Pausen

  #undgültige Pauseblöcke überspringen (falls vorhanden)
  i : int = 0
  while len(breaksList[i]) != 2 and i < len(breaksList):
    i += 1
  if i == len(breaksList): return

  if (breaksList[i][0] != 0):
    audio_blocks.append(audio_arr[0:breaksList[i][0]])
    
  for n, breakpoints in enumerate(breaksList):
    if n >= len(breaksList) - 1:
      audio_blocks.append(audio_arr[breaksList[n][1]:])
    else:
      audio_blocks.append(audio_arr[breaksList[n][1]:breaksList[n+1][0]])

  
  return audio_blocks
###############################################################################



audio_arr, sr = openFile(r"viblib\v-09-11-3-8.wav")
breaks_list = findBreaks(audio_arr=audio_arr)
audio_arr_list = splitAudioArrAtBreaks(audio_arr=audio_arr, breaksList=breaks_list)

for audio in audio_arr_list:
  findBlocksbyAmplitude(audio,sr=sr)




plt.show()
