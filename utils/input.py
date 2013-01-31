import wave
import struct


def wave_to_list(wav_path):
  wf = wave.open(wav_path, 'rb')

  CHUNK = 1024

  frames = ""
  for i in range(wf.getnframes()):
    data = wf.readframes(CHUNK)
    frames = frames + data

  # binary --> list
  count = len(frames)/2
  format = "%dh"%(count)  
  return struct.unpack( format, frames )