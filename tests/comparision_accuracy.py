from utils.input import wave_to_list
from utils.fft import fft_freq_intensity
from utils.comparison import fft_similarity
from utils.debug import plot_fft, plot_show


def slice_comp():
  # slice #2 from both audio should get a score of >0.8
  jiehan_jiehan_s = fft_freq_intensity(wave_to_list('samples/jiehan-jiehan_s8.wav'),lookup_tbl=dict())
  jiehan_kane_s = fft_freq_intensity(wave_to_list('samples/jiehan-kane_s7.wav'),lookup_tbl=dict())
  print fft_similarity(jiehan_jiehan_s[0], jiehan_jiehan_s[1],
                       jiehan_kane_s[0], jiehan_kane_s[1])

  plot_fft(*jiehan_jiehan_s)
  plot_fft(*jiehan_kane_s)
  plot_show()

  # print jiehan_jiehan_s
  # print "================================="
  # print jiehan_kane_s

  # # two completely different slices
  # jiehan_kane_s6 = fft_freq_intensity(wave_to_list('samples/jiehan-kane-s2.wav'))
  # jiehan_jiehan_s6 = fft_freq_intensity(wave_to_list('samples/jiehan-jiehan-s6.wav'))
  # print fft_similarity(jiehan_kane_s6[0], jiehan_kane_s6[1],
  #                      jiehan_jiehan_s6[0], jiehan_jiehan_s6[1])
