import sys
from utils.input import wave_to_list
from utils.slicing import slice_audio
from utils.fft import fft_freq_intensity
from utils.comparison import max_slice_tree_score


def main():
  tmpl = wave_to_list(sys.argv[1])
  sample = wave_to_list(sys.argv[2])

  tmpl_slices = slice_audio(tmpl, 2048)
  sample_slices = slice_audio(sample, 2048)

  print len(tmpl_slices), "in tmpl and", len(sample_slices), "in sample"
  print max_slice_tree_score(sample_slices, tmpl_slices)


if __name__ == "__main__":
  main()