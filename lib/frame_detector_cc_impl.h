/* -*- c++ -*- */
/*
 * Copyright 2017 <+YOU OR YOUR COMPANY+>.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_LIQUIDDSP_FRAME_DETECTOR_CC_IMPL_H
#define INCLUDED_LIQUIDDSP_FRAME_DETECTOR_CC_IMPL_H

#include <liquiddsp/frame_detector_cc.h>
#include "liquid/liquid.h"

namespace gr {
  namespace liquiddsp {

    class frame_detector_cc_impl : public frame_detector_cc
    {
     private:
         qdetector_cccf             d_detector;
         const unsigned int         d_k = 2;
         const unsigned int         d_m = 7;
         const float                d_beta = 0.3;
         gr_complex *               d_preamble_pn;
         unsigned long int          d_num_frames;

     public:
      frame_detector_cc_impl();
      ~frame_detector_cc_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FRAME_DETECTOR_CC_IMPL_H */

