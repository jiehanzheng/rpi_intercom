import sys
import wave
import re
import pyaudio
import struct
import math
from pylab import *
from utils.input import wave_to_list
from utils.data import slice_audio
from utils.fft import fft_freq_intensity

sample_slices = slice_audio(wave_to_list(sys.argv[1]),2048)

if len(sys.argv)>=3 and sys.argv[2] >= 0:
  slice = sample_slices[int(sys.argv[2])]

  freq, intensity = fft_freq_intensity(slice)

  title("audio %s" % sys.argv[2])
  xlim(70,7000)
  ylim(0,170)
  fill_between(freq, intensity)
  plot(freq, intensity, 'r.')

  p = pyaudio.PyAudio()

  wf = wave.open(re.sub(r'\.', '_s'+sys.argv[2]+'.', sys.argv[1]), 'wb')
  wf.setnchannels(1)
  wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
  wf.setframerate(44100)
  for byte in slice:
    wf.writeframes(struct.pack('h',byte))
  wf.close()

else:
  for id, slice in enumerate(sample_slices):
    plt.figure()

    freq, intensity = fft_freq_intensity(slice)

    title("audio %d" % id)
    xlim(70,7000)
    ylim(0,170)
    fill_between(freq, intensity)
    plot(freq, intensity, 'r.')

show()
