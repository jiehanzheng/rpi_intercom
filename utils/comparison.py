from __future__ import division
from fft import fft_freq_intensity
from debug import indented_print
from numpy import searchsorted
import scipy.weave as weave

#
#       SIMILARITY SCALE
#
#     [---------|----|----]
#     0        0.5        1 
#    diff    neutral  identical
#


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
  useful_sample_i = searchsorted(sample_freq, 7000)
  print "useful samp:", useful_sample_i
  sample_freq = sample_freq[:useful_sample_i]

  useful_tmpl_i = searchsorted(tmpl_freq, 7000)
  tmpl_freq = tmpl_freq[:useful_tmpl_i]
  # <70, wastes 4900 comparisons, but how much does it cost to find index and slice?
  # TODO

  point_score_struct_c = r"""
    typedef struct {
      float weighted_score;
      float weight;
    } score_info;
"""

  # need #include <math.h>
  point_score_c = r"""
    score_info point_score(float x1, float y1, float x2, float y2) {
      float dx = std::abs(x1-x2);
      float y_ratio = y1/y2;
      float y_margin = pow(std::max(y1,y2),2.2)/1000000;

      float x_comp = pow((0.015*dx),4);
      float y_comp = pow(std::max((float)0,abs(y_ratio-1)-y_margin),(float)5);
      float point_weight = y_margin+1;

      score_info result = {(1/(x_comp+y_comp+1))*point_weight,
                           point_weight};
      return result;
    }
"""

  return weave.inline(r"""
    float y2_threshold = (float) intensity_threshold/2;

    float weighted_score = 0;
    float total_weight = 0;

    float x1, y1, x2, y2;
    float best_match_score, weight_of_best_match;

    for (int i1 = 0; i1 < sample_freq.size(); i1++) {
      x1 = PyFloat_AsDouble(PyList_GetItem(sample_freq,i1));
      y1 = PyFloat_AsDouble(PyList_GetItem(sample_intensity,i1));

      if (y1 >= intensity_threshold && x1 >= 70) {
        best_match_score = 0;
        weight_of_best_match = 1;

        for (int i2 = 0; i2 < tmpl_freq.size(); i2++) {
          x2 = PyFloat_AsDouble(PyList_GetItem(tmpl_freq,i2));
          y2 = PyFloat_AsDouble(PyList_GetItem(tmpl_intensity,i2));

          if (y2 >= y2_threshold && x2 >= std::max((float)70,x1-150) && x2 <= x1+150) {
            score_info this_score_info = point_score(x1, y1, x2, y2);

            if (this_score_info.weighted_score > best_match_score) {
              best_match_score = this_score_info.weighted_score;
              weight_of_best_match = this_score_info.weight;
            }
          }
        }

        weighted_score += best_match_score;
        total_weight += weight_of_best_match;
      }
    }

    if (weighted_score != (float) 0) {
      std::cout << weighted_score << " " << total_weight << " " << weighted_score/total_weight << std::endl;
      return_val = Py_BuildValue("f", weighted_score/total_weight);
    } else {
      return_val = Py_BuildValue("f", 0.5);
    }
""",
      ['sample_freq', 'sample_intensity', 'tmpl_freq', 'tmpl_intensity',
       'intensity_threshold'],
      support_code=point_score_struct_c + point_score_c,
      headers=['<math.h>'],
      verbose=2)


def max_slice_tree_score(sample, tmpl, sample_index=0, tmpl_index=0, 
                         cumulative_score=0, try_history=[],
                         fft_similarity_lookup_tbl=dict(), 
                         sample_fft_lookup_table=dict(),
                         tmpl_fft_lookup_table=dict()):
  # sample slice that is too far behind tmpl should not be considered
  if try_history.count(tmpl_index) >= 2:
    return 0

  # # DEBUG
  # indented_print(len(try_history), "comparing sample", sample_index, "against tmpl", tmpl_index)

  fft_similarity_signature = (id(sample[sample_index]), id(tmpl[tmpl_index]))

  if fft_similarity_signature in fft_similarity_lookup_tbl:
    print "cache hit"
    this_fft_similarity = fft_similarity_lookup_tbl[fft_similarity_signature]
  else:
    print "cache MISS"
    sample_fft_freq, sample_fft_intensity = fft_freq_intensity(sample[sample_index], 
                                                               lookup_tbl=sample_fft_lookup_table)
    tmpl_fft_freq, tmpl_fft_intensity = fft_freq_intensity(tmpl[tmpl_index],
                                                           lookup_tbl=tmpl_fft_lookup_table)

    this_fft_similarity = fft_similarity_conservative(sample_fft_freq,
                                                      sample_fft_intensity,
                                                      tmpl_fft_freq,
                                                      tmpl_fft_intensity)

    fft_similarity_lookup_tbl[fft_similarity_signature] = this_fft_similarity

  # do not continue trying impossible routes
  if this_fft_similarity < 0.5 and tmpl_index > 2 and sample_index > 2:
    try:
      # DEBUG
      # indented_print(len(try_history), "-- [give up]")

      return cumulative_score/len(try_history)
    except:
      return 0

  # # DEBUG
  # try:
  #   indented_print(len(try_history), "-- score =", cumulative_score/len(try_history))
  # except:
  #   indented_print(len(try_history), "-- score =", 0)

  try_history.append(tmpl_index)
  cumulative_score = cumulative_score + this_fft_similarity

  stay_score = None
  adv_score = None

  # stay
  if tmpl_index < len(tmpl) and sample_index+1 < len(sample):
    stay_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index, 
                                      cumulative_score=cumulative_score,
                                      try_history=try_history[:], 
                                      fft_similarity_lookup_tbl=fft_similarity_lookup_tbl, 
                                      sample_fft_lookup_table=sample_fft_lookup_table,
                                      tmpl_fft_lookup_table=tmpl_fft_lookup_table)
  # advance
  if tmpl_index+1 < len(tmpl) and sample_index+1 < len(sample):
    adv_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index+1, 
                                     cumulative_score=cumulative_score,
                                     try_history=try_history[:], 
                                     fft_similarity_lookup_tbl=fft_similarity_lookup_tbl, 
                                     sample_fft_lookup_table=sample_fft_lookup_table,
                                     tmpl_fft_lookup_table=tmpl_fft_lookup_table)

  # at the bottom of the tree
  if stay_score is None and adv_score is None:
    return cumulative_score/len(try_history)

  # # DEBUG
  # indented_print(len(try_history), "-> max =", max(stay_score, adv_score), "(", try_history, ")")
  
  return max(stay_score, adv_score)
