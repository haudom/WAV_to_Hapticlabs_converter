import numpy
from fading import *
from enum import Enum
import json



class HlabsType(Enum):
    BREAK = 0,
    SINUS = 1,
    UNDEFINED = 2

class HlabsBlock:
    # def __init__(self, type : HlabsType,
    #               sound_array = None, duration = None, amplitude = None, frequency = None, frequency_fade_in = None, frequency_fade_out = None, amplitude_fade_in = None, amplitude_fade_out = None):
      
    #   if sound_array is not None:
    #     if duration is None: duration = len(sound_array)
    #   if duration is not None:
    #     if duration <= 0: raise Exception("duration must be greater than 0")

    #   self.type = type
    #   self.sound_array = sound_array

    #   self.duration = duration # samples
    #   self.amplitude = amplitude # between 0 and 1
    #   self.frequency = frequency

    #   self.frequency_fade_in = frequency_fade_in
    #   self.frequency_fade_out = frequency_fade_out
    #   self.amplitude_fade_in = amplitude_fade_in
    #   self.amplitude_fade_out = amplitude_fade_out

    def __init__(self, type : HlabsType, full_sound_array=None, start_time=None, end_time=None, duration = None, 
                 amplitude = None, frequency = None, frequency_fade_in : fading = None, frequency_fade_out : fading = None, amplitude_fade_in : fading = None, amplitude_fade_out : fading = None):
      if not duration:
        if start_time >= end_time: raise Exception("start time must be smaller than end time")
      
      self.type : HlabsType = type
      
      if not duration:
        if not full_sound_array: raise Exception("full_sound_array must be provided if no duration is provided")
        if not start_time: raise Exception("start time must be provided if no duration is provided")
        if not end_time: raise Exception("end time must be provided if no duration is provided")
        self.sound_array : numpy.ndarray = full_sound_array[start_time:end_time] #audio in this block
      else:
        self.sound_array : numpy.ndarray = full_sound_array

      if not duration:
        self.duration : int = end_time - start_time
      else:
        self.duration : int = duration

      self.amplitude = amplitude if amplitude is not None else None # between 0 and 1
      self.frequency = frequency if frequency is not None else None   # in Hz

      self.frequency_fade_in = frequency_fade_in if frequency_fade_in is not None else None
      self.frequency_fade_out = frequency_fade_out if frequency_fade_out is not None else None
      self.amplitude_fade_in = amplitude_fade_in if amplitude_fade_in is not None else None
      self.amplitude_fade_out = amplitude_fade_out if amplitude_fade_out is not None else None

    def __str__(self):
       return "{type: " + str(self.type) + ", duration: " + str(self.duration) + ", amplitude: " + str(self.amplitude) + ", frequency: " + str(self.frequency) + "}"

    def __repr__(self):
       return self.__str__()
    def toJson(self):
        block = { }
        if self.type == HlabsType.UNDEFINED:
            return
        
        if self.type == HlabsType.BREAK:
            block["type"] = "p"
            block["data"] = {
                "dur" : self.duration,
            }
        if self.type == HlabsType.SINUS:
            block["type"] = "v"
            block["data"] = {
                "amp" : self.amplitude.item(),
                "freq" : self.frequency.item(),
                "form" : "sine",
                "dur" : self.duration,
                
            }
        return block

def toJson(hlabsBlocks, fliePath):
   sequence = {"sequence": []}

   for block in hlabsBlocks:
      sequence["sequence"].append(block.toJson())

   json.dump(sequence, open(fliePath, 'w'))


def readFromJson(filePath):
   jsonFile = json.load(open(filePath, 'r'))
   sequence = jsonFile["sequence"]

   hlabsBlocks = []
   for block in sequence:
      if block["type"] == "p":
         hlabsBlocks.append(HlabsBlock(type=HlabsType.BREAK, duration = block["data"]["dur"]))
      if block["type"] == "v":
         hlabsBlocks.append(HlabsBlock(type=HlabsType.SINUS, duration = block["data"]["dur"], amplitude = block["data"]["amp"], frequency = block["data"]["freq"]))

   return hlabsBlocks
