/* -*- c++ -*- */
/* 
 * Copyright 2016 <+YOU OR YOUR COMPANY+>.
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
#include "flex_tx_bc_2_impl.h"

namespace gr {
  namespace liquiddsp {

    flex_tx_bc_2::sptr
    flex_tx_bc_2::make(int mod, int inner, int outer, int payload_size)
    {
      return gnuradio::get_initial_sptr
        (new flex_tx_bc_2_impl(mod, inner, outer, payload_size));
    }

    /*
     * The private constructor
     */
    flex_tx_bc_2_impl::flex_tx_bc_2_impl(int mod, int inner, int outer, int payload_size)
      : gr::block("flex_tx_bc_2",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
    d_payload_len(payload_size)
    {
      flexframegenprops_init_default(&d_fgprops);
      d_fgprops.check = LIQUID_CRC_24;      // data validity check
      set_inner_code(inner);      // inner FEC scheme
      set_outer_code(outer);      // outer FEC scheme
      set_modulation(mod);
      d_fg = flexframegen_create(&d_fgprops);
      d_header = (unsigned char *) malloc(14 * sizeof(unsigned char));
      memset(d_header, 0, 14);
      d_payload = (unsigned char *) malloc(d_payload_len * sizeof(unsigned char));
      d_outbuf = (gr_complex *) malloc(d_buf_len * sizeof(gr_complex));
      flexframegen_assemble(d_fg, d_header, d_payload, d_payload_len);
      d_frame_len = flexframegen_getframelen(d_fg);
      printf("Tx: Setting relative rate to: %.3f.\n", 1.0 * d_frame_len / ((double) d_payload_len));
      set_relative_rate(1.0 * d_frame_len / ((double) d_payload_len));
      set_output_multiple(d_frame_len);
    }

    /*
     * Our virtual destructor.
     */
    flex_tx_bc_2_impl::~flex_tx_bc_2_impl()
    {
    }

    void
    flex_tx_bc_2_impl::set_modulation(unsigned int modulation) {
      switch (modulation) {
        case 0:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK2;
          break;
        case 1:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK4;
          break;
        case 2:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK8;
          break;
        case 3:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK16;
          break;
        case 4:
          d_fgprops.mod_scheme = LIQUID_MODEM_DPSK2;
          break;
        case 5:
          d_fgprops.mod_scheme = LIQUID_MODEM_DPSK4;
          break;
        case 6:
          d_fgprops.mod_scheme = LIQUID_MODEM_DPSK8;
          break;
        case 7:
          d_fgprops.mod_scheme = LIQUID_MODEM_ASK4;
          break;
        case 8:
          d_fgprops.mod_scheme = LIQUID_MODEM_QAM16;
          break;
        case 9:
          d_fgprops.mod_scheme = LIQUID_MODEM_QAM32;
          break;
        case 10:
          d_fgprops.mod_scheme = LIQUID_MODEM_QAM64;
          break;
        default:
          printf("Unsupported Modulation Defaulting to BPSK.\n");
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK2;
          break;
      }
    }

    void
    flex_tx_bc_2_impl::set_inner_code(unsigned int inner_code) {
      switch (inner_code) {
        case 0:
          d_fgprops.fec0 = LIQUID_FEC_NONE;
          break;
        case 1:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27;
          break;
        case 2:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P23;
          break;
        case 3:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P45;
          break;
        case 4:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P56;
          break;
        case 5:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P67;
          break;
        case 6:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P78;
          break;
        default:
          printf("Unsupported FEC Defaulting to none.\n");
          d_fgprops.fec0 = LIQUID_FEC_NONE;
          break;
      }
    }

    void
    flex_tx_bc_2_impl::set_outer_code(unsigned int outer_code) {
      switch (outer_code) {
        case 0:
          d_fgprops.fec1 = LIQUID_FEC_NONE;
          break;
        case 1:
          d_fgprops.fec1 = LIQUID_FEC_GOLAY2412;
          break;
        case 2:
          d_fgprops.fec1 = LIQUID_FEC_RS_M8;
          break;
        case 3:
          d_fgprops.fec1 = LIQUID_FEC_HAMMING74;
          break;
        case 4:
          d_fgprops.fec1 = LIQUID_FEC_HAMMING128;
          break;
        case 5:
          d_fgprops.fec1 = LIQUID_FEC_SECDED2216;
          break;
        case 6:
          d_fgprops.fec1 = LIQUID_FEC_SECDED3932;
          break;
        case 7:
          d_fgprops.fec1 = LIQUID_FEC_SECDED7264;
          break;
        default:
          printf("Unsupported FEC Defaulting to none.\n");
          d_fgprops.fec1 = LIQUID_FEC_NONE;
          break;
      }
    }

    void
    flex_tx_bc_2_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required) {
      assert (noutput_items % d_frame_len == 0);
      int nblocks = noutput_items / d_frame_len;
      int input_required = nblocks * d_payload_len;
      ninput_items_required[0] = input_required;
    }

    int
    flex_tx_bc_2_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      assert (noutput_items % d_frame_len == 0);
      const unsigned char *in = (const unsigned char *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

      int byte_count = 0;

      static unsigned int frame_count = 0;
      unsigned int total_items = 0;
      int frame_complete = 0;

//      printf("Requested %d items\n", noutput_items);
      while (total_items < noutput_items) {
        frame_count++;
        memcpy(d_payload, in, d_payload_len);
        in += d_payload_len;
        byte_count += d_payload_len;

        // Assemble the frame
        while (!flexframegen_is_assembled(d_fg)) {
          flexframegen_assemble(d_fg, d_header, d_payload, d_payload_len);
        }

        // Make the frame in blocks
        frame_complete = 0;
        while (!frame_complete) {
          frame_complete = flexframegen_write_samples(d_fg, d_outbuf, d_buf_len);
          memcpy(out, d_outbuf, d_buf_len * sizeof(gr_complex));
          out += d_buf_len;
          total_items += d_buf_len;
        }
      }

      consume_each(byte_count); //input items consumed

//      printf("Produced %d items\n", total_items);
      return noutput_items; //output items produced
    }

  } /* namespace liquiddsp */
} /* namespace gr */

