from __future__ import division
import wave
import struct
import pyaudio
import os


def wave_to_list(wav_path, chunk=2048):
  wf = wave.open(wav_path, 'rb')

  frames = ""
  for _ in range(wf.getnframes()//chunk+1):
    data = wf.readframes(chunk)
    frames = frames + data

  # binary --> list
  count = len(frames)/2
  format = "%dh"%(count)
  return struct.unpack(format, frames)


# def microphone_read_chunk(stream, chunk=2048):
#   data = stream.read(chunk)
#   count = len(data)/2
#   format = "%dh"%(count)

#   return struct.unpack(format, data)


# def faked_realtime_read_chunk(stream, chunk=2048):
#   pass
