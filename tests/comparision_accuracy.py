from utils.input import wave_to_list
from utils.fft import fft_freq_intensity
from utils.comparison import fft_similarity

def slice_comp():
  # slice #2 from both audio should get a score of >0.8
  jiehan_jiehan_s2 = fft_freq_intensity(wave_to_list('samples/jiehan-jiehan.wav'))
  jiehan_kane_s2 = fft_freq_intensity(wave_to_list('samples/jiehan-kane.wav'))
  print fft_similarity(jiehan_jiehan_s2[0], jiehan_jiehan_s2[1],
                       jiehan_kane_s2[0], jiehan_kane_s2[1])

  # two completely different slices
  jiehan_kane_s6 = fft_freq_intensity(wave_to_list('samples/jiehan-kane-s2.wav'))
  jiehan_jiehan_s6 = fft_freq_intensity(wave_to_list('samples/jiehan-jiehan-s6.wav'))
  print fft_similarity(jiehan_kane_s6[0], jiehan_kane_s6[1],
                       jiehan_jiehan_s6[0], jiehan_jiehan_s6[1])

