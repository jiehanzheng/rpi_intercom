from __future__ import division
from fft import fft_freq_intensity
from debug import indented_print

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


def fft_similarity_conservative(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
                                intensity_threshold=20,
                                lookup_tbl=dict()):
  """Do FFT both ways and return the minimum value to be conservative"""
  return min(
             fft_similarity(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
                            intensity_threshold, 
                            lookup_tbl),
             fft_similarity(tmpl_freq,tmpl_intensity, sample_freq,sample_intensity,
                            intensity_threshold, 
                            lookup_tbl))


def fft_similarity(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
                   intensity_threshold=20, 
                   lookup_tbl=dict()):
  fingerprint = id(sample_freq),id(sample_intensity),id(tmpl_freq),id(tmpl_intensity)

  if fingerprint in lookup_tbl:
    return lookup_tbl[fingerprint]

  # TODO: oh this is very unpythonic, dont even want to look at it.
  total_score = 0
  qualified_samples = 0
  for i1,x1 in enumerate(sample_freq):  # sample 1
    if x1 >= 70 and x1 <= 7000 and sample_intensity[i1] >= intensity_threshold:
      qualified_samples = qualified_samples + 1
      best_match = 0
      for i2,x2 in enumerate(tmpl_freq):
        if x2 >= max(70,x1-150) and x2 <= min(x1+150,7000) and tmpl_intensity[i2] >= intensity_threshold:
          best_match = max(best_match, point_score(x1,sample_intensity[i1],x2,tmpl_intensity[i2]))
      total_score = total_score + best_match

  try:
    # # DEBUG
    # print "{total_score}/{qualified_samples} = {quotient}".format(
    #   total_score=total_score,
    #   qualified_samples=qualified_samples,
    #   quotient=total_score/qualified_samples)

    lookup_tbl[fingerprint] = total_score/qualified_samples
    return total_score/qualified_samples
  except:
    # if no points are qualified, return 0.5, meaning "neutral"
    lookup_tbl[fingerprint] = 0.5
    return 0.5


def point_score(x1, y1, x2, y2):
  dx = abs(x1-x2)
  y_ratio = y1/y2

  x_comp = (0.015*dx)**4
  y_comp = abs(y_ratio-1)**6

  # # DEBUG
  # print "({x1:3.0f}[{y1:3.0f}], {x2:3.0f}([{y2:3.0f}])): dx={dx:5.1f}, y_ratio={y_ratio:6.2f}, x_comp={x_comp:8.3f}, y_comp={y_comp:15.4f} => {score:8.3f}".format(
  #          x1=x1,    y1=y1,      x2=x2,     y2=y2,       dx=dx,        y_ratio=y_ratio,        x_comp=x_comp,        y_comp=y_comp,           score=1/(x_comp+y_comp+1))

  return 1/(x_comp+y_comp+1)


def max_slice_tree_score(sample, tmpl, sample_index=0, tmpl_index=0, 
                         cumulative_score=0, try_history=[],
                         fft_similarity_lookup_tbl=dict(), 
                         sample_fft_lookup_table=dict(),
                         tmpl_fft_lookup_table=dict()):
  # sample slice that is too far behind tmpl should not be considered
  if try_history.count(tmpl_index) >= 2:
    return 0

  # DEBUG
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
  if this_fft_similarity <= 0.5 and tmpl_index > 2 and sample_index > 2:
    try:
      # DEBUG
      # indented_print(len(try_history), "-- [give up]")

      return cumulative_score/len(try_history)
    except:
      return 0

  # DEBUG
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
