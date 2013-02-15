
from scipy import fft, arange
import math

from time import time

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
  return [y*rate for y in Y]

  # # do not normalize
  # return Y


def fft_freq_intensity(sound, rate=44100, lookup_tbl=dict()):
  sound_addr = id(sound)

  if sound_addr in lookup_tbl:
    return lookup_tbl[sound_addr]

  signal_length = len(sound)
  ks = list(range(signal_length))
  T = signal_length/float(rate)
  freq = [k/T for k in ks]
  freq = freq[:signal_length//2]

  Y = fft([int(point) for point in sound])/signal_length
  Y = Y[list(range(signal_length//2))]
  Y = [abs(y) for y in Y]
  Y = normalize(Y)

  lookup_tbl[sound_addr] = (freq, Y)
  return freq, Y
