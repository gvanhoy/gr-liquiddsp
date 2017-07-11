/* -*- c++ -*- */

#define LIQUIDDSP_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "liquiddsp_swig_doc.i"

%{
#include "liquiddsp/flex_tx.h"
#include "liquiddsp/flex_rx.h"
#include "liquiddsp/frame_detector_cc.h"
%}




%include "liquiddsp/flex_tx.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_tx);

%include "liquiddsp/flex_rx.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, flex_rx);

%include "liquiddsp/frame_detector_cc.h"
GR_SWIG_BLOCK_MAGIC2(liquiddsp, frame_detector_cc);
