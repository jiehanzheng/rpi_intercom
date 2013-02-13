from utils.input import wave_to_list
from utils.fft import fft_freq_intensity
from utils.comparison import fft_similarity, max_slice_tree_score
from utils.debug import plot_fft, plot_show
from utils.slicing import slice_audio


def slice_comp():
  # similar slices from two audio clips should get a score of >0.7
  s1 = fft_freq_intensity(wave_to_list('samples/jiehan-jiehan_s8.wav'),lookup_tbl=dict())
  s2 = fft_freq_intensity(wave_to_list('samples/jiehan-kane_s7.wav'),lookup_tbl=dict())
  result = fft_similarity(s1[0], s1[1],
                          s2[0], s2[1])

  print result

  plot_fft(*s1)
  plot_fft(*s2)
  plot_show()

  assert result >= 0.7, "similar slices should get a score of >0.7"

  # different slices from two audio clips should get a score of <0.4
  s1 = fft_freq_intensity(wave_to_list('samples/jiehan-jiehan_s0.wav'),lookup_tbl=dict())
  s2 = fft_freq_intensity(wave_to_list('samples/kane-kane_s4.wav'),lookup_tbl=dict())
  result = fft_similarity(s1[0], s1[1],
                          s2[0], s2[1])

  print result

  # assert result <= 0.4, "different slices should get a score of <0.4"


def audio_comp():
  a1 = slice_audio(wave_to_list('samples/jiehan-jiehan.wav'),2048)
  a2 = slice_audio(wave_to_list('samples/jiehan-kane.wav'),2048)
  result = max_slice_tree_score(a1, a2)

  print result
  assert result <= 0.4, "different audio should get a score of <0.4"