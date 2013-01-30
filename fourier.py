from __future__ import division
import wave
import pyaudio
import struct
import numpy as np
from pylab import *
from scipy import fft, arange
import pprint
pp = pprint.PrettyPrinter(indent=4)

def main():
  USE_INPUT_FILE = True

  # PyAudio init
  p = pyaudio.PyAudio()

  if USE_INPUT_FILE:
    # wf = wave.open("samples/jiehan-jiehan.wav", 'rb')
    wf = wave.open("samples/jiehan-kane.wav", 'rb')

  CHUNK = 1024
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  if USE_INPUT_FILE:
    RATE = wf.getframerate()
  else:
    RATE = 44100     # define the rate of the recording
  RECORD_SECONDS = 1
  SLICE_SIZE = 2048  # best when this is a power of 2


  if not USE_INPUT_FILE:
    stream = p.open( format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                     frames_per_buffer=CHUNK )
    print("* start recording")

  # read data
  frames = ""
  for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    if USE_INPUT_FILE:
      data = wf.readframes(CHUNK)
    else:
      data = stream.read(CHUNK)

    frames = frames + data

  if not USE_INPUT_FILE:
    print("* done recording")
    stream.stop_stream()
    stream.close()

  p.terminate()

  # binary data --> list
  count = len(frames)/2
  format = "%dh"%(count)
  audio = struct.unpack( format, frames )

  # slice
  slices = [audio[i:i+SLICE_SIZE] for i in range(0, len(audio), SLICE_SIZE)]
  print "done slicing:", len(slices), "slices"

  # plot time-amplitude for overall sound
  title("Full-length")
  # xlabel('Sample ID')
  # ylabel('Amplitude')
  plot([x for x in range(len(audio))],audio)
  xticks( np.arange(0,len(audio),SLICE_SIZE) )

  # plt.figure()

  # frequency calculations for each slice
  for slice_id, slice in enumerate(slices):
    signal_length = len(slice)          # length of the signal
    k = arange(signal_length)
    T = signal_length/float(RATE)
    frq = k/T                           # two sides frequency rangenumpy.set_string_function(f, repr=True)
    frq = frq[range(signal_length//2)]  # one side frequency range

    # FFT
    Y = fft( np.array( [ int(point) for point in slice ] ) )/signal_length
    Y = Y[range(signal_length//2)]
    Y = map( lambda x: abs(x), Y )  # for each one of them, take the abs val

    # plot six spectrums in each window
    slice_num = slice_id%6+1

    # get a new window if...
    if slice_num == 1:
      plt.figure()

    subplot(2,3,slice_num)
    title(slice_id)
    # xlabel('Freq (Hz)')
    xlim(70,7000)
    # ylabel('|Y(freq)|')
    ylim(0,170)
    fill_between(frq,Y)
    plot(frq, Y, 'r.')

  show()


# def moving_average(index, src, window_size=3):
#   starting_index = index - window_size//2
#   ending_index = index + window_size//2

#   # calculate the sum
#   current_sum = 0

#   for current_index in range(starting_index, ending_index+1):
#     try:
#       current_sum = current_sum + src[current_index]
#     except IndexError:
#       window_size = window_size - 1

#   # return sum/size
#   return current_sum/window_size if window_size is not 0 else 0

if __name__ == "__main__":
  main()