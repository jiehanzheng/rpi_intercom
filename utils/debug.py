from __future__ import print_function
from pylab import *


def indented_print(indentation, *stuff):
  print('  '*(indentation-1), *stuff)


def plot_fft(freq, intensity, label="audio"):
  figure()
  title(label)
  xlim(70,7000)
  ylim(0,170)
  fill_between(freq, intensity)
  plot(freq, intensity, 'r.')


def plot_show():
  show()
