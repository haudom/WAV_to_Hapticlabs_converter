from main import *

audio_arr, sr = openFile(r"viblib\v-09-11-3-8.wav")
breaks_list = findBreaks(audio_arr=audio_arr)
audio_arr_list = splitAudioArrAtBreaks(audio_arr=audio_arr, breaksList=breaks_list)

for audio in audio_arr_list:
  findBlocksbyAmplitude(audio,sr=sr)




plt.show()