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


point_score_struct_c = r"""
  typedef struct {
    double weighted_score;
    double weight;
  } score_info;
"""


# need #include <math.h>
point_score_c = r"""
  score_info point_score(double x1, double y1, double x2, double y2) {
    double dx = std::abs(x1-x2);
    double y_ratio = y1/y2;
    double y_margin = pow(std::max(y1,y2),2.2)/1000000;

    double x_comp = pow((0.015*dx),4);
    double y_comp = pow(std::max((double)0,abs(y_ratio-1)-y_margin),(double)5);
    double point_weight = y_margin+1;

    score_info result = {(1/(x_comp+y_comp+1))*point_weight,
                         point_weight};
    return result;
  }
"""


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


def fft_similarity_conservative(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
                                intensity_threshold=20,
                                lookup_tbl=dict()):
  """Do FFT both ways and return the minimum value to be conservative"""
  # return min(
  #            fft_similarity(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
  #                           intensity_threshold, 
  #                           lookup_tbl),
  #            fft_similarity(tmpl_freq,tmpl_intensity, sample_freq,sample_intensity,
  #                           intensity_threshold, 
  #                           lookup_tbl))

  return fft_similarity(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
                            intensity_threshold, 
                            lookup_tbl)


def fft_similarity(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
                   intensity_threshold=20, 
                   lookup_tbl=dict()):
  fingerprint = id(sample_freq),id(sample_intensity),id(tmpl_freq),id(tmpl_intensity)

  if fingerprint in lookup_tbl:
    return lookup_tbl[fingerprint]
  
  #
  # remove unnecessary elements to avoid N^2 useless calculations
  # >7000, wastes ~15000^2 comparisons, doesnt cause index to shift
  sample_freq = sample_freq[:searchsorted(sample_freq, 7000)]
  tmpl_freq = tmpl_freq[:searchsorted(tmpl_freq, 7000)]
  # <70, wastes 4900 comparisons, but how much does it cost to find index and slice?
  # TODO

  weighted_score, total_weight = weave.inline(r"""
    double y2_threshold = (double) intensity_threshold/2;

    double weighted_score = 0;
    double total_weight = 0;

    for (int i1 = 0; i1 <= sample_freq.size(); i1++) {
      double x1 = PyFloat_AsDouble(PyList_GetItem(sample_freq,i1));
      double y1 = PyFloat_AsDouble(PyList_GetItem(sample_intensity,i1));

      if (y1 >= intensity_threshold && x1 >= 70) {
        double best_match_score = 0;
        double weight_of_best_match = 0;

        for (int i2 = 0; i2 <= tmpl_freq.size(); i2++) {
          double x2 = PyFloat_AsDouble(PyList_GetItem(tmpl_freq,i2));
          double y2 = PyFloat_AsDouble(PyList_GetItem(tmpl_intensity,i2));

          if (y2 >= y2_threshold && x2 >= std::max((double)70,x1-150) && x2 <= x1+150) {
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

    return_val = Py_BuildValue("(dd)", weighted_score, total_weight);""",
               ['sample_freq', 'sample_intensity', 'tmpl_freq', 'tmpl_intensity',
                'intensity_threshold'],
               support_code=point_score_struct_c + point_score_c,
               headers=['<math.h>'],
               verbose=2)

  try:
    # DEBUG
    print weighted_score, '/', total_weight, '=', weighted_score/total_weight

    lookup_tbl[fingerprint] = weighted_score/total_weight
    return weighted_score/total_weight
  except:
    # not enough information to work with
    # return 0.5 saying we are neutral
    lookup_tbl[fingerprint] = 0.5
    return 0.5


def point_score(x1, y1, x2, y2):
  #
  # score
  dx = abs(x1-x2)  # the closer to 0, the better
  y_ratio = y1/y2  # the closer to 1, the better
  y_margin = max(y1,y2)**2.2/1000000

  x_comp = (0.015*dx)**4
  y_comp = max(0,abs(y_ratio-1)-y_margin)**5

  # # DEBUG
  # print "({x1:4.0f}[{y1:3.0f}], {x2:4.0f}([{y2:3.0f}])): dx={dx:5.1f}, y_ratio={y_ratio:6.2f}-{y_margin:3.2f}, x_comp={x_comp:8.3f}, y_comp={y_comp:15.4f} => {score:4.3f}".format(
  #          x1=x1,    y1=y1,      x2=x2,     y2=y2,       dx=dx,        y_ratio=y_ratio,        y_margin=y_margin, x_comp=x_comp,     y_comp=y_comp,           score=1/(x_comp+y_comp+1))

  #
  # weight
  # TODO let's find a more mathmagically correct formula...
  point_weight = y_margin+1

  return ((1/(x_comp+y_comp+1))*point_weight, point_weight)


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

  fft_similarity_signature = (id(sample), sample_index, id(tmpl), tmpl_index)

  if fft_similarity_signature in fft_similarity_lookup_tbl:
    this_fft_similarity = fft_similarity_lookup_tbl[fft_similarity_signature]
  else:
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
