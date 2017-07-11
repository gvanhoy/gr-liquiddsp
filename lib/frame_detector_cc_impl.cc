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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "frame_detector_cc_impl.h"

namespace gr {
  namespace liquiddsp {

    frame_detector_cc::sptr
    frame_detector_cc::make()
    {
      return gnuradio::get_initial_sptr
        (new frame_detector_cc_impl());
    }

    /*
     * The private constructor
     */
    frame_detector_cc_impl::frame_detector_cc_impl()
      : gr::sync_block("frame_detector_cc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))), d_num_frames(0)
    {
        d_preamble_pn = (gr_complex *) malloc(64*sizeof(gr_complex));
        msequence ms = msequence_create(7, 0x0089, 1);
        for (unsigned int i = 0; i < 64; i++) {
                d_preamble_pn[i].real() = (msequence_advance(ms) ? M_SQRT1_2 : -M_SQRT1_2);
                d_preamble_pn[i].imag() = (msequence_advance(ms) ? M_SQRT1_2 : -M_SQRT1_2);
        }
        msequence_destroy(ms);

        d_detector = qdetector_cccf_create_linear(d_preamble_pn, 64, LIQUID_FIRFILT_ARKAISER, d_k, d_m, d_beta);
        qdetector_cccf_set_threshold(d_detector, 0.4);
    }

    /*
     * Our virtual destructor.
     */
    frame_detector_cc_impl::~frame_detector_cc_impl()
    {
        qdetector_cccf_destroy(d_detector);
    }

    int
    frame_detector_cc_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const gr_complex *in = (const gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

        // Do <+signal processing+>
        // std::cout << "Producing " << noutput_items << " output items." << std::endl;
        for(unsigned long int i = 0; i < noutput_items; i++){
            void * v = qdetector_cccf_execute(d_detector, in[i]);
            if(v != NULL){
                std::cout << "Detected " << d_num_frames << " frames!" << std::endl;
                d_num_frames++;
            }
            out[i] = in[i];
        }

        // check if frame has been detected
        //if (v == NULL)
        //return;

        // get estimates
        //_q->tau_hat   = qdetector_cccf_get_tau  (d_detector);
        //_q->gamma_hat = qdetector_cccf_get_gamma(d_detector);
        //_q->dphi_hat  = qdetector_cccf_get_dphi (d_detector);
        //_q->phi_hat   = qdetector_cccf_get_phi  (d_detector);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

