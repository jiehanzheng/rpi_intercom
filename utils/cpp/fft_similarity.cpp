double fft_similarity(PyObject *sample_freq, PyObject *sample_intensity, 
                      PyObject *tmpl_freq, PyObject *tmpl_intensity, 
                      int intensity_threshold) {
  double y2_threshold = (double) intensity_threshold/2;

  double weighted_score = 0;
  double total_weight = 0;

  double x1, y1, x2, y2;
  double best_match_score, weight_of_best_match;

  for (Py_ssize_t i1 = 0; i1 < PyList_Size(sample_freq); i1++) {
    x1 = PyFloat_AsDouble(PyList_GetItem(sample_freq, i1));
    y1 = PyFloat_AsDouble(PyList_GetItem(sample_intensity, i1));

    if (y1 >= intensity_threshold && x1 >= 70) {
      best_match_score = 0;
      weight_of_best_match = 1;

      for (Py_ssize_t i2 = 0; i2 < PyList_Size(tmpl_freq); i2++) {
        x2 = PyFloat_AsDouble(PyList_GetItem(tmpl_freq, i2));
        y2 = PyFloat_AsDouble(PyList_GetItem(tmpl_intensity, i2));

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

  if (weighted_score != (double) 0) {
    // std::cout << weighted_score << " " << total_weight << " " << weighted_score/total_weight << std::endl;
    return weighted_score/total_weight;
  }

  return 0.5;
}
