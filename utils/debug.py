from __future__ import print_function
from pylab import *


def indented_print(indentation, *stuff):
  if isinstance(stuff[-1], dict):
    args = stuff[-1]
    stuff = stuff[:-1]
  else:
    args = {}
  print('  '*(indentation-1), *stuff, **args)


def plot_fft(freq, intensity, label="audio"):
  figure()
  title(label)
  xlim(70,7000)
  ylim(0,170)
  fill_between(freq, intensity)
  plot(freq, intensity, 'r.')


def plot_show():
  show()
