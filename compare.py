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


def the_score(x1, y1, x2, y2, quiet=False):
  dx = abs(x1-x2)
  y_ratio = y1/y2

  x_comp = (0.015*dx)**4
  y_comp = abs(y_ratio-1)**20

  if not quiet:
    print "({x1:3.0f}[{y1:3.0f}], {x2:3.0f}([{y2:3.0f}])): dx={dx:5.1f}, y_ratio={y_ratio:6.2f}, x_comp={x_comp:8.3f}, y_comp={y_comp:15.4f}, SCORE=".format(
             x1=x1,    y1=y1,      x2=x2,     y2=y2,       dx=dx,        y_ratio=y_ratio,        x_comp=x_comp,        y_comp=y_comp),

  return 1/(x_comp+y_comp+1)


def fft_similarity(frq1, frq2, Y1, Y2):
  total_score = 0
  qualified_samples = 0
  for i1,x1 in enumerate(frq1):  # sample 1
    if x1 >= 70 and x1 <= 7000 and Y1[i1] >= 20:
      qualified_samples = qualified_samples + 1
      best_match = 0
      for i2,x2 in enumerate(frq2):
        if x2 >= 70 and x2 <= 7000 and Y2[i2] >= 20:
          # print ( round(the_score(x1,Y1[i1],x2,Y2[i2]), 3) )
          best_match = max(best_match, the_score(x1,Y1[i1],x2,Y2[i2],quiet=True))
      total_score = total_score + best_match

  print "{total_score}/{qualified_samples} = {quotient}".format(
    total_score=total_score,
    qualified_samples=qualified_samples,
    quotient=total_score/qualified_samples)

  return total_score/qualified_samples


def main():
  # almost the same
  wf1 = wave.open("samples/jiehan-jiehan-s6.wav", 'rb')
  wf2 = wave.open("samples/jiehan-kane-s6.wav", 'rb')

  # completely different
  # wf1 = wave.open("samples/kane-kane-s3.wav", 'rb')
  # wf2 = wave.open("samples/jiehan-jiehan-s2.wav", 'rb')

  CHUNK = 1024
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 44100  # 1 second

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

  # # plot time-amplitude for overall sound
  # title("Amplitude")
  # subplot(211)
  # plot([x for x in range(len(audio1))],audio1)

  # subplot(212)
  # plot([x for x in range(len(audio2))],audio2)

  # # new window
  # fig = plt.figure()
  ion()

  # frequency calculations for audio 1
  signal_length = len(audio1)
  k = arange(signal_length)
  T = signal_length/float(RATE)
  frq1 = k/T
  frq1 = frq1[range(signal_length//2)]
  
  Y1 = fft( np.array( [ int(point) for point in audio1 ] ) )/signal_length
  Y1 = Y1[range(signal_length//2)]
  Y1 = map( lambda x: abs(x), Y1 )  # for each one of them, take the abs val

  subplot(2,1,1)
  title("audio 1")
  xlim(70,7000)
  ylim(0,170)
  # xlim(0,300)
  # ylim(0,350)
  fill_between(frq1,Y1)
  plot(frq1, Y1, 'r.')

  # frequency calculations for audio 2
  signal_length = len(audio2)
  k = arange(signal_length)
  T = signal_length/float(RATE)
  frq2 = k/T
  frq2 = frq2[range(signal_length//2)]
  
  Y2 = fft( np.array( [ int(point) for point in audio2 ] ) )/signal_length
  Y2 = Y2[range(signal_length//2)]
  Y2 = map( lambda x: abs(x), Y2 )  # for each one of them, take the abs val

  subplot(2,1,2)
  title("audio 2")
  xlim(70,7000)
  ylim(0,170)
  # xlim(0,300)
  # ylim(0,350)
  fill_between(frq2,Y2)
  plot(frq2, Y2, 'r.')

  show()

  # for each pairs (70-7000), calculate the score and show it on the graph
  print min( fft_similarity(frq1, frq2, Y1=Y1, Y2=Y2), fft_similarity(frq2, frq1, Y1=Y2, Y2=Y1) )

  raw_input("Exit?")


if __name__ == "__main__":
  main()