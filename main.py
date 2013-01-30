from __future__ import division
import wave
import pyaudio
import struct
import numpy as np
from pylab import *
from scipy import fft, arange

import inspect

import pprint
pp = pprint.PrettyPrinter(indent=4)

from compare import point_score, fft_similarity, normalize


def main():
  # almost the same
  wf1 = wave.open("samples/jiehan-jiehan.wav", 'rb')
  wf2 = wave.open("samples/jiehan-kane.wav", 'rb')

  # completely different
  # wf1 = wave.open("samples/kane-kane.wav", 'rb')
  # wf2 = wave.open("samples/jiehan-jiehan.wav", 'rb')

  CHUNK = 1024
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 44100  # 1 second
  SLICE_SIZE = 2048  # best when this is a power of 2

  # read data
  frames1 = ""
  for i in range(wf1.getnframes()):
    data = wf1.readframes(CHUNK)
    frames1 = frames1 + data

  frames2 = ""
  for i in range(wf2.getnframes()):
    data = wf2.readframes(CHUNK)
    frames2 = frames2 + data

  # binary data --> list
  count1 = len(frames1)/2
  format = "%dh"%(count1)
  audio1 = struct.unpack( format, frames1 )

  count2 = len(frames2)/2
  format = "%dh"%(count2)
  audio2 = struct.unpack( format, frames2 )

  slices1 = [audio1[i:i+SLICE_SIZE] for i in range(0, len(audio1), SLICE_SIZE)]
  slices2 = [audio2[i:i+SLICE_SIZE] for i in range(0, len(audio2), SLICE_SIZE)]

  # ion()

  for i2,slice2 in enumerate(slices2):
    slice_scores = []

    for i1,slice1 in enumerate(slices1):
      # frequency calculations for audio 1 (TEMPLATE)
      signal_length = len(slice1)
      k = arange(signal_length)
      T = signal_length/float(RATE)
      frq1 = k/T
      frq1 = frq1[range(signal_length//2)]
      
      Y1 = fft( np.array( [ int(point) for point in slice1 ] ) )/signal_length
      Y1 = Y1[range(signal_length//2)]
      Y1 = map( lambda x: abs(x), Y1 )  # for each one of them, take the abs val

      Y1 = normalize(Y1)

      # frequency calculations for audio 2
      signal_length = len(slice2)
      k = arange(signal_length)
      T = signal_length/float(RATE)
      frq2 = k/T
      frq2 = frq2[range(signal_length//2)]
      
      Y2 = fft( np.array( [ int(point) for point in slice2 ] ) )/signal_length
      Y2 = Y2[range(signal_length//2)]
      Y2 = map( lambda x: abs(x), Y2 )  # for each one of them, take the abs val

      Y2 = normalize(Y2)

      # show()

      # for each pairs (70-7000), calculate the score and show it on the graph
      # print min( fft_similarity(frq1, frq2, Y1=Y1, Y2=Y2), fft_similarity(frq2, frq1, Y1=Y2, Y2=Y1) )
      slice_scores.append( (i1, min( fft_similarity(frq1, frq2, Y1=Y1, Y2=Y2), fft_similarity(frq2, frq1, Y1=Y2, Y2=Y1) ) ) )

    sort_similarity_list(slice_scores)
    print i2, "=",
    print_similarity_list(slice_scores)
    print


def sort_similarity_list(the_list):
  the_list.sort(key=lambda x: x[1], reverse=True)


def print_similarity_list(the_list):
  for item in the_list:
    if item[1]:
      print item[0],":",round(item[1],3),",",

if __name__ == "__main__":
  main()