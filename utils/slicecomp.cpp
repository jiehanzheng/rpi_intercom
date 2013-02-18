  float max_slice_tree_score(py::list sample, py::list tmpl, 
                             Py_ssize_t sample_index, Py_ssize_t tmpl_index, 
                             float cumulative_score, py::list try_history, 
                             py::dict fft_similarity_lookup_table) {
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

    // in addition, the current matching slice must not stretch more than 1.2x
    //   if tmpl_index > 2 and sample_index > 2 and (sample_index+1)/(tmpl_index+1) > 1.2:
    //     return 0
    if (tmpl_index > 2 && sample_index > 2 && (sample_index+1)/(tmpl_index+1) > 1.2) {
      #ifdef DEBUG
      std::cout << "return: too stretched" << std::endl;
      #endif
      return 0;
    }

    char *sample_id = PyString_AsString(PyObject_GetAttrString(PyList_GetItem(sample, sample_index), "id"));
    char *tmpl_id   = PyString_AsString(PyObject_GetAttrString(PyList_GetItem(tmpl, tmpl_index), "id"));
    PyTupleObject *fft_sim_fp = PyTuple_Pack(2, sample_id, tmpl_id);

    #ifdef DEBUG
    std::cout << PyString_AsString(PyTuple_GetItem(fft_sim_fp, 0)) << ", " << PyString_AsString(PyTuple_GetItem(fft_sim_fp, 1)) << std::end;
    #endif

    float this_fft_similarity = 0.0;
    if (PyDict_Contains(fft_similarity_lookup_table, fft_sim_fp)) {
      this_fft_similarity = PyDict_GetItem(fft_similarity_lookup_tbl,
                                           fft_sim_fp);
    } else {
      // prepare a call to our Python function to do FFT
      // TODO: rewrite FFT function in C++

      // FFT of sample
      py::tuple args(1);
      args[0] = PyList_GetItem(sample, sample_index);
      py::tuple sample_result = fft_freq_intensity.call(args);

      // FFT of tmpl
      py::tuple args(1);
      args[0] = PyList_GetItem(tmpl, tmpl_index);
      py::tuple tmpl_result = fft_freq_intensity.call(args);

      // find lowest similarity of sample,tmpl and tmpl,sample
      // TODO take min
      fft_similarity()
    }

  }