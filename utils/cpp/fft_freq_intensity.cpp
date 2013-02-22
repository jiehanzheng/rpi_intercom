#include <math.h>
#include "kiss_fftr.h"

PyObject* fft_freq_intensity(PyObject *sample, int rate) {
  #ifdef DEBUG
    std::cout << "working on freq" << std::endl;
  #endif

  int nfft = PyTuple_Size(sample);

  #ifdef DEBUG
    std::cout << "size determined: " << nfft << std::endl;
  #endif

  // declare kiss_fft_scalar's of size len(sample), for in and out
  kiss_fft_scalar rin[nfft];
  std::complex<double> cout[nfft/2+1];
  memset(cout, 0, sizeof(std::complex<double>)*(nfft/2+1));

  #ifdef DEBUG
    std::cout << "memset done" << std::endl;
  #endif

  // each in PyTupleObject --append--> kiss_fft_scalar[]
  for (int i = 0; i < nfft; i++) {
    rin[i] = PyInt_AsLong(PyTuple_GetItem(sample, i));
  }

  #ifdef DEBUG
    std::cout << "list elements transferred" << std::endl;
  #endif

  // initialize a FFT algorithm's cfg/state buffer
  kiss_fftr_cfg kiss_fftr_state;
  kiss_fftr_state = kiss_fftr_alloc(/* nfft */        nfft, 
                                    /* inverse_fft */ 0, 
                                    /* *mem */        NULL, 
                                    /* *lemmem */     NULL);

  // let kiss_fft do the work
  kiss_fftr(kiss_fftr_state, rin, (kiss_fft_cpx *) cout);
  kiss_fft_free(kiss_fftr_state);

  #ifdef DEBUG
    std::cout << "kiss fft done" << std::endl;
  #endif

  // create freq list
  PyObject *freq_list, *intensity_list;

  // only half of our FFT result is useful, the other half is symmetric
  freq_list = PyTuple_New((Py_ssize_t) nfft/2);
  intensity_list = PyTuple_New((Py_ssize_t) nfft/2);

  #ifdef DEBUG
    std::cout << "made two PyTuple's" << std::endl;
  #endif

  // populate freq, intensity list
  // PyTuple_SetItem(freq_list,      1, PyFloat_FromDouble(0));
  // PyTuple_SetItem(intensity_list, 1, PyFloat_FromDouble(0));

  #ifdef DEBUG
    std::cout << "i = ";
  #endif

  for (int i = 0; i <= nfft/2; i++) {
    #ifdef DEBUG
      std::cout << i << ", ";
    #endif

    PyTuple_SetItem(freq_list,      i, PyFloat_FromDouble((double) i/((double) nfft/rate)));
    PyTuple_SetItem(intensity_list, i, PyFloat_FromDouble(std::abs(cout[i])));
  }

  #ifdef DEBUG
    std::cout << "PyTuple populated" << std::endl;
  #endif

  #ifdef DEBUG
    std::cout << "freed mem" << std::endl;
  #endif

  // return python tuple
  return PyTuple_Pack(2, freq_list, intensity_list);
}
