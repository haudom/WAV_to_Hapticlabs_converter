import numpy
import matplotlib.pyplot as plt
import math
from librosa.feature import rms
import os
import sys
import scipy
sys.path.append(r'../../src')
from main import openFile


def cutToSameLength(original, converted):
    if(len(original)> len(converted)):
        print("Original um ", len(original)-len(converted), "samples gekürzt")
        original = original[:len(converted)]

    elif(len(original)< len(converted)):
        print("Converted um ", len(converted)-len(original), "samples gekürzt")
        converted = converted[:len(original)]
    
    return original, converted

def fft(original, converted, sr):

    original, converted = cutToSameLength(original, converted)
    
    original_fft=abs(scipy.fft.fft(original)) # Betrag des fft repräsentiert die Amplitude
    converted_fft=abs(scipy.fft.fft(converted))

    frequencies = numpy.fft.fftfreq(n=len(original), d=1/sr)
    original_fft = original_fft[:len(original_fft)//2]
    original_fft = abs(original_fft)


    converted_fft = converted_fft[:len(converted_fft)//2]
    converted_fft = abs(converted_fft)

    frequencies = frequencies[:len(frequencies)//2]

    # 1000 alles über 1000 HZ weckschneiden (menschliche Wahrnemung von Frequenzen nur bis ca. 1000Hz)
    index1000 = numpy.argmax(frequencies>1000)
    original_fft = original_fft[:index1000]
    converted_fft = converted_fft[:index1000]
    frequencies = frequencies[:index1000]

    # scale
    original_fft = original_fft/len(original)
    converted_fft = converted_fft/len(converted)

    return frequencies, original_fft, converted_fft

def averageWithZero(values,weights = None):
    try:
        return numpy.average(values, weights=weights)
    except ZeroDivisionError:
        return 0

def WeightedStandardDeviation(values, weights):
    try:
        average = numpy.average(values, weights=weights)
        # Fast and numerically precise:
        variance = numpy.average((values-average)**2, weights=weights)
    except ZeroDivisionError:
        return 0
    return math.sqrt(variance)

def compareWeightedMean(values1, values2, weights):
    mean1 = numpy.mean(values1, weights=weights)
    mean2 = numpy.mean(values2, weights=weights)
    return abs(mean1 - mean2)

def getMask(frequencies):
    index200 = numpy.argmax(frequencies>200)
    step = 1/numpy.argmax(frequencies>1)

    #bis 200hz bleibt die Wahrnehmung ungefähr gleich, dann wird sie schwächer
    mask1=numpy.ones(len(frequencies[:index200]))
    mask2=numpy.linspace(1,0,len(frequencies[index200:]))
    return numpy.concatenate((mask1,mask2),axis=0)

def error(values1, values2):
    error = abs(values1 - values2)
    return error, numpy.mean(error)
def rmsError(values1, values2):
    error = abs( values1 - values2)
def power(y,sr):
    frame_length = sr//40
    return rms(y=y,frame_length=frame_length, hop_length=1)[0]


def entropy(y):
    # Create a histogram of the audio data
    hist, _ = numpy.histogram(y, bins=256, range=(-1, 1), density=True)
    
    # Calculate the entropy
    return scipy.stats.entropy(hist, base=2)

def addEntropyToFiles(files):
    entropies = []
    for file1, file2 in files:
        signal, sr = openFile(file1)
        entropies.append(entropy(signal))
    # add to files1d the entropies as a new column
    return numpy.column_stack((files, entropies))

def sortByEntropy(files):
    files = addEntropyToFiles(files)
    return sorted(files, key=lambda x: x[-1])
    

        

def find_common_wav_files(folder1, folder2):
    # Listen von .wav Dateien in den beiden Ordnern erstellen
    files1 = {f for f in os.listdir(folder1) if f.endswith('.wav')}
    files2 = {f for f in os.listdir(folder2) if f.endswith('.wav')}
    
    # Gemeinsame Dateien finden
    common_files = files1.intersection(files2)
    
    # Zweidimensionale Liste mit den Pfaden der gemeinsamen Dateien erstellen
    result = [[os.path.join(folder1, f), os.path.join(folder2, f)] for f in common_files]
    
    return result

def comparFrequency(samples1, samples2):
    frequencies, original_fft, converted_fft = fft(samples1, samples2)
    compareMean = compareWeightedMean(original_fft, converted_fft, frequencies)
    compareError = error(original_fft, converted_fft)
    StarndardDeviationOrg = WeightedStandardDeviation(original_fft, frequencies)
    StandardDeviationCon = WeightedStandardDeviation(converted_fft, frequencies)
    # TODO

def meanFrequencyStandardDerivation(files):
    deviations1 = []
    deviations2 = []
    for file1, file2 in files:
        signal, sr = openFile(file1)
        signal2, sr2 = openFile(file2)
        frequencies, fft1, fft2 = fft(signal, signal2, sr)
        StandardDeviation1 = WeightedStandardDeviation(frequencies, fft1)
        StandardDeviation2 = WeightedStandardDeviation(frequencies, fft2)
        deviations1.append(StandardDeviation1)
        deviations2.append(StandardDeviation2)
    
    return numpy.mean(deviations1), numpy.mean(deviations2)

def meanPowerStandardDerivation(files):
    deviations1 = []
    deviations2 = []
    for file1, file2 in files:
        signal, sr = openFile(file1)
        signal2, sr2 = openFile(file2)
        power1 = power(signal, sr)
        power2 = power(signal2, sr2)
        PowerStandardDerivation1 = numpy.var(power1)
        PowerStandardDerivation2 = numpy.var(power2)
        deviations1.append(PowerStandardDerivation1)
        deviations2.append(PowerStandardDerivation2)
    
    return numpy.mean(deviations1), numpy.mean(deviations2)

def meanFrequencyError(files):
    errors = []

    for file1, file2 in files:
        signal, sr = openFile(file1)
        signal2, sr2 = openFile(file2)
        frequencies, fft1, fft2 = fft(signal, signal2, sr)
        _, error1 = error(fft1, fft2)
        errors.append(error1)
    
    return numpy.mean(errors), errors

def meanPowerError(files):
    errors = []

    for file1, file2 in files:
        signal, sr = openFile(file1)
        signal2, sr2 = openFile(file2)
        signal, signal2 = cutToSameLength(signal, signal2)
        power1 = power(signal, sr)
        power2 = power(signal2, sr2)
        _, error1 = error(power1, power2)
        errors.append(error1)
    
    return numpy.mean(errors), errors

def addSrtandardDeviationToFiles(files):
    standardDeviations1 = []
    standardDeviations2 = []
    for file1, file2 in files:
        signal, sr = openFile(file1)
        signal2, sr2 = openFile(file2)
        frequencies, fft1, fft2 = fft(signal, signal2, sr)
        StandardDeviation1 = WeightedStandardDeviation(frequencies, fft1)
        StandardDeviation2 = WeightedStandardDeviation(frequencies, fft2)
        standardDeviations1.append(StandardDeviation1)
        standardDeviations2.append(StandardDeviation2)
    
    files = numpy.column_stack((files, standardDeviations1))
    files = numpy.column_stack((files, standardDeviations2))
    return files

def sortByStandardDeviation(files):
    files = addSrtandardDeviationToFiles(files)
    return sorted(files, key=lambda x: x[-2])

def meanEntropy(files):
    entropies = []
    entropies2 = []
    for file1, file2 in files:
        signal, sr = openFile(file1)
        signal2, sr = openFile(file2)
        entropies.append(entropy(signal))
        entropies2.append(entropy(signal2))

    return numpy.mean(entropies), numpy.mean(entropies2)

def meanFrequencies(files):

    meanFrequencies1 = []
    meanFrequencies2 = []

    for file1, file2 in files:
        signal1, sr = openFile(file1)
        signal2, sr = openFile(file2)

        frequencies, fft1, fft2 = fft(signal1, signal2, sr)

        meanFrequencies1.append(averageWithZero(frequencies, weights=fft1))
        meanFrequencies2.append(averageWithZero(frequencies, weights=fft2))

    return numpy.mean(meanFrequencies1), numpy.mean(meanFrequencies2)

def meanPower(files):

    meanPower1 = []
    meanPower2 = []

    for file1, file2 in files:
        signal1, sr = openFile(file1)
        signal2, sr = openFile(file2)

        power1 = power(signal1, sr)
        power2 = power(signal2, sr)

        meanPower1.append(numpy.mean(power1))
        meanPower2.append(numpy.mean(power2))

    return numpy.mean(meanPower1), numpy.mean(meanPower2)


