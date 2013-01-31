from fft import fft_freq_intensity
from debug import indented_print


def fft_similarity(sample_freq,sample_intensity, tmpl_freq,tmpl_intensity, 
                   intensity_threshold=20, quiet=True):
  total_score = 0
  qualified_samples = 0
  for i1,x1 in enumerate(sample_freq):  # sample 1
    if x1 >= 70 and x1 <= 7000 and sample_intensity[i1] >= intensity_threshold:
      qualified_samples = qualified_samples + 1
      best_match = 0
      for i2,x2 in enumerate(tmpl_freq):
        if x2 >= 70 and x2 <= 7000 and tmpl_intensity[i2] >= intensity_threshold:
          best_match = max(best_match, point_score(x1,sample_intensity[i1],x2,tmpl_intensity[i2],quiet=True))
      total_score = total_score + best_match

  if not quiet:
    print "{total_score}/{qualified_samples} = {quotient}".format(
      total_score=total_score,
      qualified_samples=qualified_samples,
      quotient=total_score/qualified_samples)

  if qualified_samples is not 0:
    return total_score/qualified_samples
  else:
    return 0


def point_score(x1, y1, x2, y2, quiet=False):
  dx = abs(x1-x2)
  y_ratio = y1/y2

  x_comp = (0.015*dx)**4
  y_comp = abs(y_ratio-1)**20

  if not quiet:
    print "({x1:3.0f}[{y1:3.0f}], {x2:3.0f}([{y2:3.0f}])): dx={dx:5.1f}, y_ratio={y_ratio:6.2f}, x_comp={x_comp:8.3f}, y_comp={y_comp:15.4f}".format(
             x1=x1,    y1=y1,      x2=x2,     y2=y2,       dx=dx,        y_ratio=y_ratio,        x_comp=x_comp,        y_comp=y_comp),

  return 1/(x_comp+y_comp+1)


def max_slice_tree_score(sample, tmpl, sample_index=0, tmpl_index=0, 
                         lookup_tbl=dict(), cumulative_score=0, try_history=[],
                         sample_fft_lookup_table=dict(),
                         tmpl_fft_lookup_table=dict()):
  if try_history.count(tmpl_index) >= 2:
    return 0

  indented_print(len(try_history), "comparing sample", sample_index, "against tmpl", tmpl_index)

  sample_fft_freq, sample_fft_intensity = fft_freq_intensity(sample[sample_index], 
                                                             lookup_tbl=sample_fft_lookup_table)
  tmpl_fft_freq, tmpl_fft_intensity = fft_freq_intensity(tmpl[tmpl_index],
                                                         lookup_tbl=tmpl_fft_lookup_table)

  try_history.append(tmpl_index)
  cumulative_score = cumulative_score + fft_similarity(sample_fft_freq,
                                                       sample_fft_intensity,
                                                       tmpl_fft_freq,
                                                       tmpl_fft_intensity)

  stay_score = None
  adv_score = None

  # stay
  if tmpl_index < len(tmpl) and sample_index+1 < len(sample):
    stay_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index, 
                                      lookup_tbl=lookup_tbl, 
                                      cumulative_score=cumulative_score,
                                      try_history=try_history[:], 
                                      sample_fft_lookup_table=sample_fft_lookup_table,
                                      tmpl_fft_lookup_table=tmpl_fft_lookup_table)
  # advance
  if tmpl_index+1 < len(tmpl) and sample_index+1 < len(sample):
    adv_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index+1, 
                                     lookup_tbl=lookup_tbl, 
                                     cumulative_score=cumulative_score,
                                     try_history=try_history[:], 
                                     sample_fft_lookup_table=sample_fft_lookup_table,
                                     tmpl_fft_lookup_table=tmpl_fft_lookup_table)

  if stay_score is None and adv_score is None:
    try:
      return cumulative_score/len(try_history)
    except:
      return 0

  return max(stay_score, adv_score)
