from __future__ import division
from fft import fft_freq_intensity
from debug import indented_print
from numpy import searchsorted
import scipy.weave as weave
import time

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

fft_similarity_c = r"""
  float fft_similarity(PyObject *sample_freq, PyObject *sample_intensity, 
                       PyObject *tmpl_freq, PyObject *tmpl_intensity, 
                       int intensity_threshold) {
    float y2_threshold = (float) intensity_threshold/2;

    float weighted_score = 0;
    float total_weight = 0;

    float x1, y1, x2, y2;
    float best_match_score, weight_of_best_match;

    for (Py_ssize_t i1 = 0; i1 < PyList_Size(sample_freq); i1++) {
      x1 = PyFloat_AsDouble(PyList_GetItem(sample_freq, i1));
      y1 = PyFloat_AsDouble(PyList_GetItem(sample_intensity, i1));

      if (y1 >= intensity_threshold && x1 >= 70) {
        best_match_score = 0;
        weight_of_best_match = 1;

        for (Py_ssize_t i2 = 0; i2 < PyList_Size(tmpl_freq); i2++) {
          x2 = PyFloat_AsDouble(PyList_GetItem(tmpl_freq, i2));
          y2 = PyFloat_AsDouble(PyList_GetItem(tmpl_intensity, i2));

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
      // std::cout << weighted_score << " " << total_weight << " " << weighted_score/total_weight << std::endl;
      return weighted_score/total_weight;
    }

    return 0.5;
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
    headers=['<math.h>'],
    # force=1,
    verbose=2)


def max_slice_tree_score(sample, tmpl, sample_index=5, tmpl_index=5, 
                         cumulative_score=0, try_history=[],
                         fft_similarity_lookup_tbl={}):
  max_slice_tree_score_c = r"""
    #ifdef DEBUG
    std::cout << "checking repetition" << std::endl;
    #endif

    // each slice must not repeat twice or more
    //   if try_history.count(tmpl_index) >= 2: return 0
    long occurrences = 0;
    for (Py_ssize_t i = 0; i < PyList_Size(try_history); i++) {
      if (PyInt_AsLong(PyList_GetItem(try_history, i)) == (long) tmpl_index) {
        occurrences++;
      }

      if (occurrences >= 2) {
        #ifdef DEBUG
          std::cout << "return: too much repetition" << std::endl;
        #endif
        return 0;
      }
    }

    #ifdef DEBUG
      std::cout << "checking stretch rate" << std::endl;
    #endif

    // in addition, the current matching slice must not stretch more than 1.2x
    //   if tmpl_index > 2 and sample_index > 2 and (sample_index+1)/(tmpl_index+1) > 1.2:
    //     return 0
    if (tmpl_index > 2 && sample_index > 2 && (sample_index+1)/(tmpl_index+1) > 1.2) {
      #ifdef DEBUG
        std::cout << "return: too stretched" << std::endl;
      #endif
      return 0;
    }

    #ifdef DEBUG
      std::cout << "fetching slice ids" << std::endl;
    #endif

    char *sample_id = PyString_AsString(PyObject_GetAttrString(PyList_GetItem(sample, sample_index), "id"));
    char *tmpl_id   = PyString_AsString(PyObject_GetAttrString(PyList_GetItem(tmpl, tmpl_index), "id"));
    
    #ifdef DEBUG
      std::cout << "generating fp: ";
    #endif

    PyObject *fft_sim_fp = Py_BuildValue("(ss)", sample_id, tmpl_id);

    #ifdef DEBUG
      std::cout << "(" << PyString_AsString(PyTuple_GetItem(fft_sim_fp, 0)) << ", " << PyString_AsString(PyTuple_GetItem(fft_sim_fp, 1)) << ")" << std::endl;
    #endif

    double this_fft_similarity = 0.0;
    if (PyDict_Contains(fft_similarity_lookup_tbl, fft_sim_fp)) {
      this_fft_similarity = PyFloat_AsDouble(PyDict_GetItem(fft_similarity_lookup_tbl,
                                                            fft_sim_fp));
    } else {
      // prepare a call to our Python function to do FFT
      // TODO: rewrite FFT function in C++

      #ifdef DEBUG
        std::cout << "preparing FFT" << std::endl;
      #endif

      // FFT of sample
      PyObject *sample_result = PyObject_CallFunctionObjArgs(fft_freq_intensity, 
                                                             PyObject_GetAttrString(PyList_GetItem(sample, sample_index), "data"), 
                                                             NULL);

      // FFT of tmpl
      PyObject *tmpl_result = PyObject_CallFunctionObjArgs(fft_freq_intensity, 
                                                           PyObject_GetAttrString(PyList_GetItem(tmpl, tmpl_index), "data"), 
                                                           NULL);
      
      #ifdef DEBUG
        std::cout << "FFT done" << std::endl;
      #endif

      std::cout << PyTuple_Check(sample_result) << std::endl;

      PyObject *sample_freq, *sample_intensity, *tmpl_freq, *tmpl_intensity;
      PyArg_ParseTuple(sample_result, "OO", &sample_freq, &sample_intensity);
      PyArg_ParseTuple(tmpl_result, "OO", &tmpl_freq, &tmpl_intensity);

      #ifdef DEBUG
        std::cout << "sample_freq size: " << PyList_Size(sample_freq) << std::endl;
        std::cout << "fetch done" << std::endl;
      #endif

      // find lowest similarity of sample,tmpl and tmpl,sample
      // TODO take min
      this_fft_similarity = fft_similarity(sample_freq,
                                           sample_intensity,
                                           tmpl_freq,
                                           tmpl_intensity,
                                           20);

      #ifdef DEBUG
        std::cout << "similarity " << this_fft_similarity << std::endl;
      #endif

      PyDict_SetItem(fft_similarity_lookup_tbl, 
                     fft_sim_fp, 
                     PyFloat_FromDouble(this_fft_similarity));

      #ifdef DEBUG
        std::cout << "cached result, dict is now " << PyDict_Size(fft_similarity_lookup_tbl) << " long" << std::endl;
      #endif
    }
    
"""
  
  weave.inline(max_slice_tree_score_c,
    ['sample', 'tmpl', 'sample_index', 'tmpl_index', 
     'cumulative_score', 'try_history',
     'fft_similarity_lookup_tbl', 'fft_freq_intensity'],
    support_code=point_score_struct_c + point_score_c + fft_similarity_c,
    define_macros=[('DEBUG', None)],
    # define_macros=[],
    # force=1,
    verbose=2)

  # # # DEBUG
  # # indented_print(len(try_history), "comparing sample", sample_index, "against tmpl", tmpl_index, {'end': ''})


  # # any slice must not repeat twice or more
  # if try_history.count(tmpl_index) >= 2:
  #   # # DEBUG
  #   # print " -> return: too much repetition"
  #   return 0

  # # in addition, the current matching slice must not stretch more than 1.2x
  # if tmpl_index > 2 and sample_index > 2 and (sample_index+1)/(tmpl_index+1) > 1.2:
  #   # # # DEBUG
  #   # print " -> return: too stretched"
  #   return 0

  # fft_similarity_signature = (sample[sample_index].id, tmpl[tmpl_index].id)

  # if fft_similarity_signature in fft_similarity_lookup_tbl:
  #   # print "cache hit"
  #   this_fft_similarity = fft_similarity_lookup_tbl[fft_similarity_signature]
  # else:
  #   # print "cache MISS"
  #   sample_fft_freq, sample_fft_intensity = fft_freq_intensity(sample[sample_index].data)
  #   tmpl_fft_freq, tmpl_fft_intensity = fft_freq_intensity(tmpl[tmpl_index].data)
  #   this_fft_similarity = fft_similarity_conservative(sample_fft_freq,
  #                                                     sample_fft_intensity,
  #                                                     tmpl_fft_freq,
  #                                                     tmpl_fft_intensity)
  #   fft_similarity_lookup_tbl[fft_similarity_signature] = this_fft_similarity

  # # # DEBUG
  # # print ':', this_fft_similarity

  # # do not continue trying impossible routes
  # if this_fft_similarity < 0.3 and tmpl_index > 2 and sample_index > 2:
  #   # # DEBUG
  #   # indented_print(len(try_history), " -> return: too bad so far")
  #   return 0

  # # # DEBUG
  # # try:
  # #   indented_print(len(try_history), "-- score =", cumulative_score/len(try_history))
  # # except:
  # #   indented_print(len(try_history), "-- score =", 0)

  # try_history.append(tmpl_index)
  # cumulative_score = cumulative_score + this_fft_similarity

  # stay_score = None
  # adv_score = None

  # # stay
  # if tmpl_index < len(tmpl) and sample_index+1 < len(sample):
  #   stay_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index, 
  #                                     cumulative_score=cumulative_score,
  #                                     try_history=try_history[:], 
  #                                     fft_similarity_lookup_tbl=fft_similarity_lookup_tbl)
  # # advance
  # if tmpl_index+1 < len(tmpl) and sample_index+1 < len(sample):
  #   adv_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index+1, 
  #                                    cumulative_score=cumulative_score,
  #                                    try_history=try_history[:], 
  #                                    fft_similarity_lookup_tbl=fft_similarity_lookup_tbl)

  # # at the bottom of the tree
  # if stay_score is None and adv_score is None:
  #   return cumulative_score/len(try_history)

  # # # DEBUG
  # # indented_print(len(try_history)-1, "-> max =", max(stay_score, adv_score))
  
  # return max(stay_score, adv_score)
