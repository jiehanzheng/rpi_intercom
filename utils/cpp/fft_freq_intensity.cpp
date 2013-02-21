#include "kiss_fftr.h"
#include "_kiss_fft_guts.h"
#include <math.h>

PyObject* fft_freq_intensity(PyObject *sample, int rate) {
  int nfft = PyList_Size(sample);

  // declare kiss_fft_scalar's of size len(sample), for in and out
  kiss_fft_scalar rin[nfft];
  std::complex<double> *cout;
  memset(cout, 0, sizeof(std::complex<double>)*(nfft/2+1));

  // each in PyListObject --append--> kiss_fft_scalar[]
  for (int i = 0; i < nfft; i++) {
    rin[i] = PyInt_AsLong(PyList_GetItem(sample, i));
  }

  // initialize a FFT algorithm's cfg/state buffer
  kiss_fftr_cfg kiss_fftr_state;
  kiss_fftr_state = kiss_fftr_alloc(/* nfft */        nfft, 
                                    /* inverse_fft */ 0, 
                                    /* *mem */        NULL, 
                                    /* *lemmem */     NULL);

  // let kiss_fft do the work
  kiss_fftr(kiss_fftr_state, rin, (kiss_fft_cpx *) cout);
  kiss_fft_free(kiss_fftr_state);

  // create freq list
  PyObject *freq_list, *intensity_list;

  // only half of our FFT result is useful, the other half is symmetric
  freq_list = PyList_New((Py_ssize_t) nfft/2);
  intensity_list = PyList_New((Py_ssize_t) nfft/2);

  // populate freq, intensity list
  for (int i = 0; i < nfft/2; i++) {
    PyList_Append(freq_list, PyFloat_FromDouble(i/(nfft/rate)));
    PyList_Append(intensity_list, PyFloat_FromDouble(std::abs(cout[i])));
  }

  free(cout);

  // return python tuple
  return PyTuple_Pack(2, freq_list, intensity_list);
}
