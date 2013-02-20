double max_slice_tree_score(PyObject *sample, PyObject *tmpl,
                            long sample_index, long tmpl_index,
                            double cumulative_score, PyObject *try_history,
                            PyObject *fft_similarity_lookup_tbl) {
  #ifdef DEBUG
    std::cout << "checking repetition" << std::endl;
  #endif

  // each slice must not repeat twice or more
  //   if try_history.count(tmpl_index) >= 2: return 0
  long occurrences = 0;
  for (Py_ssize_t i = 0; i < PyList_Size(try_history); i++) {
    if (PyInt_AsLong(PyList_GetItem(try_history, i)) == tmpl_index) {
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

    PyObject *sample_freq, *sample_intensity, *tmpl_freq, *tmpl_intensity;
    PyArg_ParseTuple(sample_result, "OO", &sample_freq, &sample_intensity);
    PyArg_ParseTuple(tmpl_result, "OO", &tmpl_freq, &tmpl_intensity);

    // Py_XDECREF(sample_result);
    // Py_XDECREF(tmpl_result);

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

    Py_XDECREF(fft_sim_fp);

    #ifdef DEBUG
      std::cout << "cached result, dict is now " << PyDict_Size(fft_similarity_lookup_tbl) << " long" << std::endl;
    #endif
  }

  if (this_fft_similarity < 0.3 && tmpl_index > 2 && sample_index > 2) {
    #ifdef DEBUG
      std::cout << "return: current too bad" << std::endl;
    #endif
    return 0;
  }

  #ifdef DEBUG
    std::cout << "appending to history" << std::endl;
  #endif

  PyList_Append(try_history, PyInt_FromLong(tmpl_index));
  cumulative_score += this_fft_similarity;

  #ifdef DEBUG
    std::cout << "appended to history" << std::endl;
  #endif

  long stay_score = 0;
  long adv_score = 0;

  if (tmpl_index < PyList_Size(tmpl) && sample_index+1 < PyList_Size(sample)) {
    stay_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index, 
                                      cumulative_score,
                                      PyList_GetSlice(try_history, 
                                                      0, 
                                                      PyList_Size(try_history) - 1), 
                                      fft_similarity_lookup_tbl);
  }

  if (tmpl_index+1 < PyList_Size(tmpl) && sample_index+1 < PyList_Size(sample)) {
    adv_score = max_slice_tree_score(sample, tmpl, sample_index+1, tmpl_index+1, 
                                     cumulative_score,
                                     PyList_GetSlice(try_history, 
                                                     0, 
                                                     PyList_Size(try_history) - 1), 
                                     fft_similarity_lookup_tbl);
  }

  #ifdef DEBUG
    std::cout << "done stay & adv" << std::endl;
  #endif


  Py_XDECREF(try_history);

}
