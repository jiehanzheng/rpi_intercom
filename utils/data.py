from utils.fft import fft_freq_intensity
from utils.slicing import slice_audio


class Peer:
  """Stores everything related to a peer, including network address, sound 
  template, etc.

  """

  fft_lookup_table = dict()

  def __init__(self, address, audio, chunk):
    self.address = address
    self.audio = slice_audio(audio, slice_size=chunk)
