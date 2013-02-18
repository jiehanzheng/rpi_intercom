from fft import fft_freq_intensity


class Peer:
  """Stores everything related to a peer, including network address, sound 
  template, etc.

  """

  def __init__(self, address, audio, chunk):
    self.address = address
    self.audio = slice_audio(audio, slice_size=chunk, audio_type=address)


class Slice:
  """Store identifier along with the actual data for slices, making it easy to 
  cache calculation results.

  """

  def __init__(self, data, slice_id):
    self.data = data
    self.id = slice_id


def slice_audio(audio, slice_size, audio_type):
  return [Slice(audio[i:i+slice_size], audio_type+'_'+str(i)) for i in range(0, len(audio), slice_size)]
