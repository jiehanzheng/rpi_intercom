def slice_audio(audio, slice_size):
  return [audio[i:i+slice_size] for i in range(0, len(audio), slice_size)]