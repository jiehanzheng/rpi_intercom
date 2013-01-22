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


def main():
  wf1 = wave.open("samples/jiehan-jiehan-s6.wav", 'rb')
  wf2 = wave.open("samples/jiehan-kane-s6.wav", 'rb')

  CHUNK = 1024
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 44100  # 1 second
  RECORD_SECONDS = 1
  SLICE_SIZE = 2048

  # read data
  frames1 = ""
  for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = wf1.readframes(CHUNK)
    frames1 = frames1 + data

  frames2 = ""
  for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = wf2.readframes(CHUNK)
    frames2 = frames2 + data

  # binary data --> list
  count1 = len(frames1)/2
  format = "%dh"%(count1)
  audio1 = struct.unpack( format, frames1 )

  count2 = len(frames2)/2
  format = "%dh"%(count2)
  audio2 = struct.unpack( format, frames2 )

  # plot time-amplitude for overall sound
  title("Amplitude")
  subplot(211)
  plot([x for x in range(len(audio1))],audio1)
  xticks( np.arange(0,len(audio1),SLICE_SIZE) )

  subplot(212)
  plot([x for x in range(len(audio2))],audio2)
  xticks( np.arange(0,len(audio2),SLICE_SIZE) )

  # new window
  fig = plt.figure()
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

  plot2 = subplot(2,1,2)
  title("audio 2")
  xlim(70,7000)
  ylim(0,170)
  fill_between(frq2,Y2)
  plot(frq2, Y2, 'r.')

  show()

  # for each pairs (70-7000), calculate the score and show it on the graph
  for i1,x1 in enumerate(frq1):  # sample 1
    if x1 >= 70 and x1 <= 7000 and Y1[i1] >= 100:
      for i2,x2 in enumerate(frq2):
        if x2 >= 70 and x2 <= 7000:
          print "%s(%s) & %s(%s): %s" % ( round(x1), round(Y1[i1],0), round(x2), round(Y2[i2],0), the_score(x1,Y1[i1],x2,Y2[i2] ) )

  annotation2 = plot2.annotate('arrowstyle', xy=(0, 1),  xycoords='data',
                xytext=(50, 30), textcoords='offset points',
                arrowprops=dict(arrowstyle="->")
                )
  # cid = fig.canvas.mpl_connect('button_press_event', onclick)
  # pp.pprint(inspect.getmembers( annotation2 ))

  raw_input("Remove?")
  annotation2.set_visible(False)
  draw()
  
  raw_input("Exit?")

def onclick(event):
  print event
    # print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
    #     event.button, event.x, event.y, event.xdata, event.ydata)

def the_score(x1, y1, x2, y2):
  return ( 1 / abs(x1-x2)**2 ) * abs(y1-y2)

def moving_average(index, src, window_size=3):
  starting_index = index - window_size//2
  ending_index = index + window_size//2

  # calculate the sum
  current_sum = 0

  for current_index in range(starting_index, ending_index+1):
    try:
      current_sum = current_sum + src[current_index]
    except IndexError:
      window_size = window_size - 1

  # return sum/size
  return current_sum/window_size if window_size is not 0 else 0

if __name__ == "__main__":
  main()