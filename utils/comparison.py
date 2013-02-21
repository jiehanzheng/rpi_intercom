from __future__ import division
from fft import fft_freq_intensity
from debug import indented_print
from numpy import searchsorted
import scipy.weave as weave
import time
import os.path

#
#       SIMILARITY SCALE
#
#                threshold
#                    |
#     [---------|----|----]
#     0        0.5        1 
#    diff    neutral  identical
#


point_score_struct_c = r"""
  typedef struct {
    float weighted_score;
    float weight;
  } score_info;

"""

with open(os.path.join(os.path.dirname(__file__), 'cpp/point_score.cpp'), 'r') as f:
  point_score_c = f.read()

with open(os.path.join(os.path.dirname(__file__), 'cpp/fft_similarity.cpp'), 'r') as f:
  fft_similarity_c = f.read()

with open(os.path.join(os.path.dirname(__file__), 'cpp/max_slice_tree_score.cpp'), 'r') as f:
  max_slice_tree_score_c = f.read()

with open(os.path.join(os.path.dirname(__file__), 'cpp/fft_freq_intensity.cpp'), 'r') as f:
  fft_freq_intensity_c = f.read()


def find_out_which_peer_this_guy_mentioned(guy, peers, slice_comparison_lookup, callback):
  """Returns the best guess and our confidence"""

  best_peer = None
  best_peer_confidence = 0
  for peer in peers:
    # print len(peer.audio), "in tmpl and", len(guy), "in sample"
    similarity = max_slice_tree_score(guy, peer.audio, 
                                      fft_similarity_lookup_tbl=slice_comparison_lookup)
    
    if similarity >= best_peer_confidence:
      best_peer_confidence = similarity
      best_peer = peer
  
  callback(best_peer, best_peer_confidence)


def listen_for_over(callback):
  pass


def fft_similarity_conservative(sample_freq, sample_intensity,
                                tmpl_freq, tmpl_intensity, 
                                intensity_threshold=20):
  """Do FFT both ways and return the minimum value to be conservative"""
  return min(
             fft_similarity(sample_freq[:],sample_intensity[:], tmpl_freq[:],tmpl_intensity[:], 
                            intensity_threshold),
             fft_similarity(tmpl_freq[:],tmpl_intensity[:], sample_freq[:],sample_intensity[:],
                            intensity_threshold))


def fft_similarity(sample_freq, sample_intensity,
                   tmpl_freq, tmpl_intensity, 
                   intensity_threshold=20):
  # remove unnecessary elements to avoid N^2 useless calculations
  # >7000, wastes ~15000^2 comparisons, doesnt cause index to shift
  sample_freq = sample_freq[:searchsorted(sample_freq, 7000)]
  tmpl_freq = tmpl_freq[:searchsorted(tmpl_freq, 7000)]
  # <70, wastes 4900 comparisons, but how much does it cost to find index and slice?
  # TODO

  return weave.inline(r"""
    return_val = Py_BuildValue("f", fft_similarity(sample_freq, 
                                                   sample_intensity, tmpl_freq, 
                                                   tmpl_intensity,
                                                   intensity_threshold));
""",
    ['sample_freq', 'sample_intensity', 'tmpl_freq', 'tmpl_intensity',
     'intensity_threshold'],
    support_code=point_score_struct_c + point_score_c + fft_similarity_c,
    # force=1,
    verbose=2)


def max_slice_tree_score(sample, tmpl, sample_index=0, tmpl_index=0, 
                         cumulative_score=0, try_history=[],
                         fft_similarity_lookup_tbl={}):
    
  weave.inline("""
    max_slice_tree_score(sample, tmpl,
                         sample_index, tmpl_index,
                         cumulative_score, try_history,
                         fft_similarity_lookup_tbl);
""",
    ['sample', 'tmpl', 'sample_index', 'tmpl_index', 
     'cumulative_score', 'try_history', 'fft_similarity_lookup_tbl'],
    support_code=point_score_struct_c + point_score_c + fft_freq_intensity_c + fft_similarity_c + max_slice_tree_score_c,
    define_macros=[('DEBUG', None)],
    include_dirs=[os.path.join(os.path.dirname(__file__), 'cpp')],
    sources=['utils/cpp/kiss_fftr.c', 'utils/cpp/kiss_fft.c'],
    force=1,
    verbose=2)


  # # at the bottom of the tree
  # if stay_score is None and adv_score is None:
  #   return cumulative_score/len(try_history)

  # # # DEBUG
  # # indented_print(len(try_history)-1, "-> max =", max(stay_score, adv_score))
  
  # return max(stay_score, adv_score)
