/* -*- c++ -*- */

#define LIQUIDDSP_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "liquiddsp_swig_doc.i"

%{
#include "liquiddsp/fft.h"
#include "liquiddsp/flex_rx_cb.h"
#include "liquiddsp/flex_rx_c.h"
#include "liquiddsp/flex_tx_c.h"
#include "liquiddsp/flex_tx_bc_2.h"
#include "liquiddsp/flex_rx_c_constel.h"
%}


%include "liquiddsp/fft.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, fft);

%include "liquiddsp/flex_rx_cb.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx_cb);
%include "liquiddsp/flex_rx_c.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx_c);

%include "liquiddsp/flex_tx_c.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_tx_c);
%include "liquiddsp/flex_tx_bc_2.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_tx_bc_2);
%include "liquiddsp/flex_rx_c_constel.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx_c_constel);
