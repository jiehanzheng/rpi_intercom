import wave
import pyaudio
import struct
import numpy as np
from pylab import *
from scipy import fft, arange
import pprint
import array
pp = pprint.PrettyPrinter(indent=4)

# PyAudio init
p = pyaudio.PyAudio()

# wf = wave.open("samples/jiehan-jiehan.wav", 'rb')
wf = wave.open("samples/kane-kane.wav", 'rb')

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = wf.getframerate()
RECORD_SECONDS = 1
SLICE_SIZE = 2048  # best when this is a power of 2

# read data
frames = ""
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
  data = wf.readframes(CHUNK)
  frames = frames + data

# p.terminate()

# binary data --> list
count = len(frames)/2
format = "%dh"%(count)
audio = struct.unpack( format, frames )

# slice
slices = [audio[i:i+SLICE_SIZE] for i in range(0, len(audio), SLICE_SIZE)]
print "done slicing:", len(slices), "slices"

# # plot time-amplitude for overall sound
# title("Full-length")
# # xlabel('Sample ID')
# # ylabel('Amplitude')
# plot([x for x in range(len(audio))],audio)
# xticks( np.arange(0,len(audio),SLICE_SIZE) )

# plt.figure()

# frequency calculations for each slice
# for slice_id, slice in enumerate(slices):
slice = slices[3]

signal_length = len(slice)         # length of the signal
k = arange(signal_length)
T = signal_length/float(RATE)
frq = k/T                          # two sides frequency range
frq = frq[range(signal_length/2)]  # one side frequency range

# FFT
Y = fft( np.array( [ int(point) for point in slice ] ) )/signal_length
Y = Y[range(signal_length/2)]

# xlabel('Freq (Hz)')
xlim(70,7000)
# ylabel('|Y(freq)|')
ylim(0,170)
fill_between(frq,abs(Y))

wf = wave.open("samples/kane-kane-s3.wav", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)

# this line taken from:
#   http://ja.nishimotz.com/python_wave (wow i can read Japanese now)
# to pack unpacked data again
wf.writeframes(array.array('h', slice).tostring())

wf.close()

show()