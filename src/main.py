import librosa
import os.path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy
import scipy


PLOT_INTERMIN_RESULTS : bool = True #Zwischenschritte Plotten?

fig : int = 0


def PlotInterminResults(value : bool):
  global PLOT_INTERMIN_RESULTS
  PLOT_INTERMIN_RESULTS = value



##############################################################################
# WAV Datei öffnen
##############################################################################
def openFile(filename):
  sr=16000 #Resampling Rate (16kHz for ai pitch finding)
  # Check if file exists
  if os.path.exists(filename):
    print("File", filename, "exists.")
  else:
    print("File", filename, "does not exist")
    exit()
  # 2. Load the audio as a waveform `y`
  #    Store the sampling rate as `sr`
  return librosa.load(path=filename, sr=sr,mono=True)
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
def findBreaks(audio_arr, sr):
  index = -1

# Einstellbare Parameter
  minBreakTime = minBreakDistance = sr / 40 #in samples #eine Pause muss mindestens eine 40 hz Periode lang sein
  toleranz = 0.007 # Amplituden toleranz zwischen 0 und 1 (welsche Werte werden nicht berücksichtigt/als Pause bewertet)
##

  breaksList = []

  for i, value in enumerate(audio_arr):

    if value < toleranz and value > -toleranz and i != len(audio_arr) - 1:
      if index == -1:
          index = i
    else:
      if i - index >= minBreakTime and index != -1:
        #Wenn Zeit zwischen Pausen kleiner als Tolleranz dann die letzte Pause verlängern statt neue zu erstellen
        if len(breaksList) > 0 and breaksList[-1][1] >= index - minBreakTime:
          breaksList[-1][1] = i
        else:
          breaksList.append([index,i])
      index = -1
  # --Wenn Zeit bis endesignal kleinder ist als Mindespausenlänge, letzte Pause verlängern
  if len(breaksList) > 0 and len(audio_arr) - breaksList[-1][1] < minBreakTime:
    breaksList[-1][1] = len(audio_arr)-1
  # elif(len(audio_arr) - index > minBreakTime and index != -1):  
  # #Wenn Zeit/ Abstand zwischen Pausen kleiner als Mindestabstand dann die letzte Pause verlängern statt neue zu erstellen
  #   if len(breaksList) > 0 and breaksList[-1][1] >= len(audio_arr)-1 - minBreakTime:
  #     breaksList[-1][1] = i
  #   else:
  #     breaksList.append([index,len(audio_arr)-1])


  global PLOT_INTERMIN_RESULTS
  if PLOT_INTERMIN_RESULTS:
## Plotten der gefundenen Pausen
    global fig
    plt.figure(fig).set_figwidth(20)
    plt.axhline(0, color="black")
    for breaks in breaksList:
      if len(breaks)==2:
        plt.gca().add_patch(Rectangle((breaks[0],-1),width=breaks[1]-breaks[0],height=2, facecolor = 'yellow', edgecolor="green"))
    plt.plot(audio_arr)
    fig += 1

  return breaksList
###############################################################################



###############################################################################
# Blöcke über Signalamplituden bilden - deprecated
################################################################################
def findBlocksbyAmplitude(audio_arr,sr):
  #frame_length = sr/10  -- frequenzen bis 10 HZ werden korrekt verarbeitet
  frame_length : int = int(sr/25)
  hop_length : int = int(frame_length/4)
  audio_rms_arr = librosa.feature.rms(y=audio_arr, frame_length=frame_length, hop_length=hop_length)
  local_minima_rms = scipy.signal.argrelextrema(audio_rms_arr[-1], numpy.less)
  local_minima_rms =  [hop_length*minimum for minimum in local_minima_rms]

  global PLOT_INTERMIN_RESULTS
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
  if len(breaksList) <= 0: return [audio_arr]

  audio_blocks = [] #audio Blöcke. Audio Array geteil an Pausen

  # undgültige Pauseblöcke überspringen (falls vorhanden)
  i : int = 0
  while len(breaksList[i]) != 2 and i < len(breaksList):
    i += 1
  if i == len(breaksList): return
  #
  if (breaksList[i][0] != 0):
    audio_blocks.append(audio_arr[0:breaksList[i][0]])
    
  for n, breakpoints in enumerate(breaksList):
    if n >= len(breaksList) - 1:
      if breaksList[n][1] < len(audio_arr):
        audio_blocks.append(audio_arr[breaksList[n][1]:])
    else:
      audio_blocks.append(audio_arr[breaksList[n][1]:breaksList[n+1][0]])

 
  return audio_blocks








#############################################################################	
# Vereinfachen von Graphen zu linearen Darstellungen
# Parameter: data: Daten welche verifacht werden [Zeitpunkte, Werte]/ [x,y], window_size: "Auflösung" der vereinfachung (Je größer desto gröber die Vereinfachung)
#            time_tolerance: Zeitwerte innherhalb werden zu einem Zeitwert zusammengefasst
#            value_tolerance: Aufeinanderfolgende Werte innerhalb der Toleranz werden als horizontale Gerade interpretiert/ zusammengefasst.
###############################################################################

def linearApproximation(data, value_tolerance, window_size, time_tolerance = None, fig = None):

  if not data: return

  if time_tolerance is None:
    time_tolerance = window_size/2
  linePoints = []
  

  pos = 0

  linePoints.append(data[0]) #Erster Punkt wrid immer hinzugefügt
  lastMinOnWindowEdge : bool = False #bei letzten Durchgang war das min am rand des Fensters
  lasMaxOnWindowEdge : bool = False #bei letzten durchgang war das max am rand des Fensters
  LastMinFirst : bool = False #beim letzten durchgang war das min vor dem max



  # Berechnen der Minimal- und Maximalwerte im Fenster
  while data:
    
    #Fenster schieben
    windowlength = 0
    for i in range(len(data)):
      if data[i][0] >= pos + window_size:
        windowlength = i
        break
    if windowlength == 1:
      windowlength = 2
      
    if windowlength == 0:
      window = data
      data = []
    else:
      window = data[:windowlength]
      data = data[windowlength-1:]

    print("windows:",window)
    plt.vlines(x=window[0][0], ymin=-1, ymax=1, color="red")
    plt.vlines(x=window[-1][0], ymin=-1, ymax=1, color="red")

    WindowValues = [row[1] for row in window]
    max = numpy.nanmax(WindowValues)
    maxPos = WindowValues.index(max)
    min = numpy.nanmin(WindowValues)
    minPos = WindowValues.index(min)

    print("min: ", min, "max: ", max, "minPos: ", minPos, "maxPos: ", maxPos)

  ## Punkte am Rand der Fenster entfernen, wenn die Grade im Fenster weitergeführt wird.
    if pos > 0:
      if lasMaxOnWindowEdge:
        if minPos == 0:
         linePoints.pop(-1)
         min = None
        elif maxPos < minPos:
          linePoints.pop(-1)

      elif lastMinOnWindowEdge:
        if maxPos == 0:
          linePoints.pop(-1)
          max = None
        elif minPos < maxPos == 0:
          linePoints.pop(-1)

      elif LastMinFirst and maxPos == 0:
        max = None
      elif not LastMinFirst and minPos == 0:
        min = None

    print("min: ", min, "max: ", max, "minPos: ", minPos, "maxPos: ", maxPos)

    lastMinOnWindowEdge = False #bei letzten Durchgang war das min am rand des Fensters
    lasMaxOnWindowEdge = False #bei letzten durchgang war das max am rand des Fensters
    LastMinFirst = False #beim letzten durchgang war das min vor dem max

    if minPos == len(window) - 1:
      lastMinOnWindowEdge = True
    if maxPos == len(window) - 1:
      lasMaxOnWindowEdge = True

    if maxPos > minPos:
      LastMinFirst = True
      if min is not None:
        linePoints.append(window[minPos])
      if max is not None:
        linePoints.append(window[maxPos])
    if minPos >= maxPos:
      LastMinFirst = False
      if max is not None:
        linePoints.append(window[maxPos])
      if min is not None:
        linePoints.append(window[minPos])

    
    pos = window[-1][0] # pos auf Zeitposition / x Position der abgearbeiteten Daten setzen




    #print("pos:",pos,"window:",window)
    #print("linePoints:",linePoints)

    if not data:
      linePoints.append(window[-1]) #letzter Punkt der Daten wird immer hinzugefügt

    print("linePoints: ", linePoints)


  print("linePoints: ", linePoints)
  #Zeittoleranz anwenden
  linePoints = applyTolerance(linePoints, 0, time_tolerance)
  #Werttoleranz anwenden
  linePoints = applyTolerance(linePoints, 1, value_tolerance)

  #Durch Verschiebung entstandene gleiche Punkt entfernen
  deleteDuplicatedPoints(linePoints)
  
  if len(linePoints) >= 3:
    deleteIndexes = []
    for i in range(1,len(linePoints)-1):
      if linePoints[i][1] > linePoints[i-1][1] and linePoints[i][1] < linePoints[i+1][1]:
        deleteIndexes.append(i)
      if linePoints[i][1] < linePoints[i-1][1] and linePoints[i][1] > linePoints[i+1][1]:
        deleteIndexes.append(i)
    for i in reversed(deleteIndexes):
      linePoints.pop(i)




  return linePoints

#entfernt mehrfach vorkommende Punkte (wenn diese in der Liste nebeinander liegen)
def deleteDuplicatedPoints(linePoints):
  i = 1
  while i < len(linePoints):
    try:
     
     while linePoints[i][0] == linePoints[i-1][0] and linePoints[i][1] == linePoints[i-1][1]:
      linePoints.pop(i)

    except IndexError:
      break
    i+=1

#Verschiebt Punkte welche innerhlab der Tolleranz liegen zu einem gemeinsamen durchschnitt.
#Entfernt Punkte, welche durch die Verschiebeung auf bzw. in einer Geraden liegen, welche von zwei außenpunkten aufgespannt wird.
def applyTolerance(list, index, tolerance):
  referenceValue = 0
  outList = []
  for i in range(1,len(list)):
    if abs(list[referenceValue][index] - list[i][index]) > tolerance:
      if i > referenceValue + 1:
        mean = numpy.mean([row[index] for row in list[referenceValue:i-1]])
        outList.append(list[referenceValue])
        outList[-1][index] = mean
        outList.append(list[i-1])
        outList[-1][index] = mean
      else:
        outList.append(list[referenceValue])

      referenceValue = i

  if referenceValue == len(list) - 1:
    outList.append(list[referenceValue])
  else:
    mean =  numpy.mean([row[index] for row in list[referenceValue:]])
    outList.append(list[referenceValue])
    outList[-1][index] = mean
    outList.append(list[-1])
    outList[-1][index] = mean
  return outList
  

###############################################################################
# Split
###############################################################################
  """
  Splits a list into sublists based on a given value.

  Args:
      lst (list): The list to be split.
      value: The value to split the list at.

  Returns:
      list: A list of sublists, where each sublist contains elements from the original list that are not equal to the given value.
  """
def splitListAtValueCrossing(lst, value):
  result = []
  temp = []
  for i in range(len(lst)-1):
    if lst[i] >= value and lst[i+1] < value or lst[i] <= value and lst[i+1] > value:
      if temp:
        result.append(temp)
      temp = []
    
    temp.append(lst[i])

#wenn keine spilts gefunden werde, wird eingangsliste zurückgegeben
  if result == []:
    result.append(lst)
  return result





###############################################################################
# Berechnet harmonische Grundfrequenz
###############################################################################
def getFrequency(audio_arr, sr):
  # anfangsbedingungen
  if audio_arr is None: return
  if len(audio_arr) <= 0: return #Leres Array ignorieren

  # FFT berechnen
  fft_result = scipy.fft.fft(audio_arr)
  frequencies = scipy.fft.fftfreq(len(fft_result), d=1/sr)

  # Verwende librosa.pyin zur Bestimmung der Grundfrequenz
  f0, voiced_flag, voiced_probs = librosa.pyin(audio_arr, fmin=20, fmax=500, sr=sr,frame_length=len(audio_arr))
  #durchschnittliche Grundfrequenz
  mean_f0 = numpy.mean(f0[~numpy.isnan(f0)])
  print(mean_f0)
  print(f0)

  global PLOT_INTERMIN_RESULTS
  if PLOT_INTERMIN_RESULTS:
    global fig
    plt.figure(fig)
    plt.axvline(x=mean_f0, color="red")
    plt.plot(frequencies[:len(frequencies)//2],abs(fft_result[:len(fft_result)//2]))

    fig += 1
  return frequencies

###############################################################################
# Amplituden erkennung
###############################################################################

def getAmplitudes(audio_arr, sr):
  amplitudes = []
  splits = splitListAtValueCrossing(audio_arr, 0)

  #Betrag des Signals berechnen
  splits = [numpy.abs(split) for split in splits]


  #Zeiten hinzufügen (Samples seit beginn)
  counter = 0
  temp = []
  timeAbsValueSplits = []	
  for split in splits:
    for value in split:
      temp.append([counter,value])
      counter += 1
    if temp:
      timeAbsValueSplits.append(temp)
      temp = []

  #Amplituden finden
  for absSplit in timeAbsValueSplits:
    splitValues = [row[1] for row in absSplit]
    amplitude = numpy.max(splitValues)
    index = splitValues.index(amplitude)
    amplitudes.append([absSplit[index][0],amplitude])

  global PLOT_INTERMIN_RESULTS
  if PLOT_INTERMIN_RESULTS:
    global fig
    plt.figure(fig).set_figwidth(20)
    plt.plot(audio_arr, label="Zeitsignal")
    if amplitudes:
      plt.plot([row[0] for row in amplitudes],[row[1] for row in amplitudes],color="red",marker="x",label="Amplituden")
    plt.legend()
    plt.title("Amplituden (getAmplitudes())")
    plt.xlabel("Samples")
    plt.ylabel("Auslenkung")
    fig += 1
  return amplitudes


def interpolate(x_y_arr, signal_length):
  x = [row[0] for row in x_y_arr]
  y = [row[1] for row in x_y_arr]
  interpolated = numpy.interp(x = range(0, signal_length), xp=x, fp=y, left=x_y_arr[0][1], right=x_y_arr[-1][1])
  if PLOT_INTERMIN_RESULTS:
    global fig
    plt.figure(fig)
    plt.plot(interpolated,label="Interpolierterung")
    plt.legend()
    plt.title("Interpolierung (interpolate())")
    fig += 1
  return interpolated

def rms(arr):
    return numpy.sqrt(numpy.mean([value ** 2. for value in arr]))



def simpleSplitByAmplitude(audio_arr, amplitudes, sr, start = 0, stop = None):

  if stop is None: stop = len(audio_arr)

  if start >= stop:  raise ValueError("start must be smaller than stop")

  fisrstAmplitudeIndex = 0
  lastAmplitudeIndex = 0
  for i, amplitude in enumerate(amplitudes):
    if amplitude[0] >= start and amplitude[0] < stop:
      fisrstAmplitudeIndex = i
      break
  for i, amplitude in reversed(list(enumerate(amplitudes))):
    if amplitude[0] >= start and amplitude[0] < stop:
      lastAmplitudeIndex = i
      break

  amplitudes = amplitudes[fisrstAmplitudeIndex:lastAmplitudeIndex+1]

  minBlockSize = sr//40 # meindestens eine 40HZ Periode
  threshold = 0.1 # 10% amplitudenänderung führen zu neuen Block
  reference_amplitude = amplitudes[0]
  cut_indices = []
  #finde stellen an den das signal geteilt wird
  for amplitude in amplitudes:
    if abs(amplitude[1] - reference_amplitude[1]) > threshold and amplitude[0] - reference_amplitude[0] > minBlockSize:
      cut_indices.append(amplitude[0])
      reference_amplitude = amplitude

  if len(cut_indices) <= 0: return numpy.array([[audio_arr]]), cut_indices

  return numpy.split(audio_arr, cut_indices), cut_indices

def simpleBlockByAmplitude(audio_arr, amplitudes, sr,start = 0, stop = None):

  if stop is None: stop = len(audio_arr)
  if start >= stop:  raise ValueError("start must be smaller than stop")

  audios, cuts = simpleSplitByAmplitude(audio_arr, amplitudes, sr, start=start, stop=stop)
  if len(cuts) == 0: return audios, [[start, stop-1]]
  blocks = []
  blocks.append([start,cuts[0]-1])

  if len(cuts) > 1:
    for i in range(0, len(cuts)-1):
      blocks.append([cuts[i], cuts[i+1]-1])
  if cuts[-1] < stop-1:
    blocks.append([cuts[-1], stop-1])
  return audios,blocks


def blockMeanFrequency(frequencies, block):
  return rms(frequencies[block[0]:block[1]])

def blockMeanAmplitude(inrterpolatedAmplitudes, block):
  return rms(inrterpolatedAmplitudes[block[0]:block[1]])


#audio_arr, sr = openFile(r"viblib\v-09-10-3-52.wav")
# print("sample rate: ", sr)
#breaks_list = findBreaks(audio_arr=audio_arr, sr=sr)
#print(breaks_list)
#print(len(audio_arr))

# audio_arr_list = splitAudioArrAtBreaks(audio_arr=audio_arr, breaksList=breaks_list)
# print(audio_arr_list)
#print(audio_arr_list[-1])

# if audio_arr_list is None: exit()
# for audio in audio_arr_list:
#   getAmplitudes(audio_arr=audio)

#plt.show()


# plt.show()
# list = [[1,0],[2,90],[3,85],[4,80],[5,70],[6,60],[7,50],[8,40],[9,50],[10,60],[11,70],[12,80],[13,90],[14,100],[15,1],[16,40],[17,30],[18,40],[19,60]]

# print(linearApproximation(list,10,5,1))
# test = [row[1] for row in list]
# max = numpy.nanmax(test)
# print(test.index(max))
# print(test)