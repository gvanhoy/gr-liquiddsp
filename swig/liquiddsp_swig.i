/* -*- c++ -*- */

#define LIQUIDDSP_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "liquiddsp_swig_doc.i"

%{
#include "liquiddsp/flex_rx_cb.h"
#include "liquiddsp/flex_rx_c.h"
#include "liquiddsp/flex_rx_c_constel.h"
#include "liquiddsp/flex_rx_msgq.h"
#include "liquiddsp/flex_tx.h"
#include "liquiddsp/flex_rx.h"
%}


%include "liquiddsp/flex_rx_cb.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx_cb);
%include "liquiddsp/flex_rx_c.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx_c);

%include "liquiddsp/flex_rx_c_constel.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx_c_constel);
%include "liquiddsp/flex_rx_msgq.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx_msgq);

%include "liquiddsp/flex_tx.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_tx);

%include "liquiddsp/flex_rx.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx);
