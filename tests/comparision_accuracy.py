from __future__ import division
from utils.input import wave_to_list
from utils.fft import fft_freq_intensity
from utils.comparison import fft_similarity, max_slice_tree_score
from utils.debug import plot_fft, plot_show
from utils.data import slice_audio
from time import time,sleep


def slice_comp():
  # similar slices from two audio clips should get a score of >0.7
  s1 = fft_freq_intensity(wave_to_list('tests/samples/jiehan-jiehan_s8.wav'))
  s2 = fft_freq_intensity(wave_to_list('tests/samples/jiehan-kane_s7.wav'))

  # plot_fft(*s1)
  # plot_fft(*s2)
  # plot_show()
  
  time_started = time()
  result = fft_similarity(s1[0], s1[1],
                          s2[0], s2[1])
  print "jiehan: jiehan8 -- kane7 =", result, "in", time() - time_started
  assert result >= 0.7, "jiehan: jiehan8 -- kane7 score is too low (%f)" % result


  # similar slices from two audio clips should get a score of >0.7
  s1 = fft_freq_intensity(wave_to_list('tests/samples/jiehan-jiehan_s8.wav'))
  s2 = fft_freq_intensity(wave_to_list('tests/samples/jiehan-sean_s11.wav'))
  
  time_started = time()  
  result = fft_similarity(s1[0], s1[1],
                          s2[0], s2[1])
  print "jiehan: jiehan8 -- sean11 =", result, "in", time() - time_started
  assert result >= 0.9, "jiehan: jiehan8 -- sean11 score is too low (%f)" % result

  # different slices from two audio clips should get a score of <0.4
  s1 = fft_freq_intensity(wave_to_list('tests/samples/jiehan-jiehan_s11.wav'))
  s2 = fft_freq_intensity(wave_to_list('tests/samples/kane-kane_s5.wav'))

  time_started = time()
  result = fft_similarity(s1[0], s1[1],
                          s2[0], s2[1])
  print "diff: jiehan8 -- kane4 =", result, "in", time() - time_started
  # assert result <= 0.4, "diff: jiehan8 -- kane4 score is too high (%f)" % result


def audio_comp():
  a1 = slice_audio(wave_to_list('tests/samples/jiehan-jiehan.wav'),2048, 'a1')
  a2 = slice_audio(wave_to_list('tests/samples/jiehan-sean.wav'),2048, 'a2')

  time_started = time()
  
  result = max_slice_tree_score(a1, a2)

  print "jiehan: jiehan -- sean = ", result, "in", time() - time_started
  assert result >= 0.7, "same thing score too low (%f)" % result


  a1 = slice_audio(wave_to_list('tests/samples/jiehan-jiehan.wav'),2048, 'a1')
  a2 = slice_audio(wave_to_list('tests/samples/jiehan-sean.wav'),2048, 'a2')

  time_started = time()
  
  result = max_slice_tree_score(a1, a2)

  print "jiehan: jiehan -- sean = ", result, "in", time() - time_started
  # assert result >= 0.7, "same thing score too low (%f)" % result

  a1 = slice_audio(wave_to_list('tests/samples/jiehan-sean.wav'),2048, 'a1')
  a2 = slice_audio(wave_to_list('tests/samples/kane-kane.wav'),2048, 'a2')

  time_started = time()
  
  result = max_slice_tree_score(a1, a2)

  print "diff: sean -- kane = ", result, "in", time() - time_started
  # assert result >= 0.7, "same thing score too low (%f)" % result

  a1 = slice_audio(wave_to_list('tests/samples/jiehan-jiehan.wav'),2048, 'a1')
  a2 = slice_audio(wave_to_list('tests/samples/kane-kane.wav'),2048, 'a2')

  time_started = time()
  
  result = max_slice_tree_score(a1, a2)

  print "diff: jiehan -- kane = ", result, "in", time() - time_started
  # assert result >= 0.7, "same thing score too low (%f)" % result