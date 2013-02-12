from __future__ import division
from scipy import fft, arange
import math


def normalize(Y):
  # # percentage
  # sum_y = sum(Y)
  # return map(lambda Y: (Y/sum_y)*2000, Y)

  # # log function
  # return map(lambda Y: math.log(Y,1.03), Y)

  # normalize, but changes < 2.5x
  sum_y = sum(Y)
  rate = (3000/sum_y)
  if rate >= 1:
    rate = min(2.5, rate)
  else:
    rate = max(1/2.5, rate)
  return map(lambda y: y*rate, Y)

  # # do not normalize
  # return Y


def fft_freq_intensity(sound, rate=44100, lookup_tbl=dict()):
  sound_addr = id(sound)

  if sound_addr in lookup_tbl:
    return lookup_tbl[sound_addr]

  signal_length = len(sound)
  ks = range(signal_length)
  T = signal_length/float(rate)
  freq = map(lambda k: k/T, ks)
  freq = freq[:signal_length//2]

  Y = fft([int(point) for point in sound])/signal_length
  Y = Y[range(signal_length//2)]
  Y = map(lambda y: abs(y), Y)
  Y = normalize(Y)

  lookup_tbl[sound_addr] = (freq, Y)
  return freq, Y
