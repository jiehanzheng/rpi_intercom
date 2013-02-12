import sys
from utils.input import wave_to_list

sample = wave_to_list(sys.argv[0])

if sys.argv[0] >= 0:
  # cut mode
else:
  # view mode
