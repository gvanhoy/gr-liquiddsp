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
#include "flex_tx_bc_impl.h"
#include <liquid/liquid.h>
#include <stdio.h>

namespace gr {
  namespace liquiddsp {

    flex_tx_bc::sptr
    flex_tx_bc::make() {
      return gnuradio::get_initial_sptr
              (new flex_tx_bc_impl());
    }

    /*
     * The private constructor
     */
    flex_tx_bc_impl::flex_tx_bc_impl()
            : gr::block("flex_tx_bc",
                        gr::io_signature::make(1, 1, sizeof(char)),
                        gr::io_signature::make(1, 1, sizeof(gr_complex)))
    {
      flexframegenprops_init_default(&d_fgprops);
      d_fgprops.check = LIQUID_CRC_24;      // data validity check
      d_fgprops.fec0 = LIQUID_FEC_HAMMING74;      // inner FEC scheme
      d_fgprops.fec1 = LIQUID_FEC_NONE;      // outer FEC scheme
      d_fgprops.mod_scheme = LIQUID_MODEM_DPSK2;
      d_outer_code = LIQUID_FEC_NONE;
      d_inner_code = LIQUID_FEC_HAMMING74;
      d_modulation = LIQUID_MODEM_DPSK2;
      d_fg = flexframegen_create(&d_fgprops);
      d_header = (unsigned char *) malloc(14 * sizeof(unsigned char));
      memset(d_header + sizeof(unsigned int), 0, 14 - sizeof(unsigned int));
      d_payload = (unsigned char *) malloc((d_payload_len + 10) * sizeof(unsigned char));
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
    flex_tx_bc_impl::~flex_tx_bc_impl() {
      flexframegen_destroy(d_fg);
      free(d_outbuf);
      free(d_header);
      free(d_payload);
    }

    void flex_tx_bc_impl::set_modulation(unsigned int modulation) {
      switch (modulation) {
        case 0:
          d_modulation = LIQUID_MODEM_PSK2;
          break;
        case 1:
          d_modulation = LIQUID_MODEM_PSK4;
          break;
        case 2:
          d_modulation = LIQUID_MODEM_PSK8;
          break;
        case 3:
          d_modulation = LIQUID_MODEM_PSK16;
          break;
        case 4:
          d_modulation = LIQUID_MODEM_DPSK2;
          break;
        case 5:
          d_modulation = LIQUID_MODEM_DPSK4;
          break;
        case 6:
          d_modulation = LIQUID_MODEM_DPSK8;
          break;
        case 7:
          d_modulation = LIQUID_MODEM_ASK4;
          break;
        case 8:
          d_modulation = LIQUID_MODEM_QAM16;
          break;
        case 9:
          d_modulation = LIQUID_MODEM_QAM32;
          break;
        case 10:
          d_modulation = LIQUID_MODEM_QAM64;
          break;
      }
      reconfigure();
    }

    void flex_tx_bc_impl::set_inner_code(unsigned int inner_code) {
      switch (inner_code) {
        case 0:
          d_inner_code = LIQUID_FEC_NONE;
          break;
        case 1:
          d_inner_code = LIQUID_FEC_CONV_V27;
          break;
        case 2:
          d_inner_code = LIQUID_FEC_CONV_V27P23;
          break;
        case 3:
          d_inner_code = LIQUID_FEC_CONV_V27P45;
          break;
        case 4:
          d_inner_code = LIQUID_FEC_CONV_V27P56;
          break;
        case 5:
          d_inner_code = LIQUID_FEC_CONV_V27P67;
          break;
        case 6:
          d_inner_code = LIQUID_FEC_CONV_V27P78;
          break;
      }
      reconfigure();
    }

    void flex_tx_bc_impl::set_outer_code(unsigned int outer_code) {
      switch (outer_code) {
        case 0:
          d_outer_code = LIQUID_FEC_NONE;
          break;
        case 1:
          d_outer_code = LIQUID_FEC_GOLAY2412;
          break;
        case 2:
          d_outer_code = LIQUID_FEC_RS_M8;
          break;
        case 3:
          d_outer_code = LIQUID_FEC_HAMMING74;
          break;
        case 4:
          d_outer_code = LIQUID_FEC_HAMMING128;
          break;
        case 5:
          d_outer_code = LIQUID_FEC_SECDED2216;
          break;
        case 6:
          d_outer_code = LIQUID_FEC_SECDED3932;
          break;
        case 7:
          d_outer_code = LIQUID_FEC_SECDED7264;
          break;
      }
      reconfigure();
    }

    void flex_tx_bc_impl::reconfigure() {
      d_fgprops.mod_scheme = d_modulation;
      d_fgprops.fec0 = d_inner_code;
      d_fgprops.fec1 = d_outer_code;
      flexframegen_setprops(d_fg, &d_fgprops);
      flexframegen_assemble(d_fg, d_header, d_payload, d_payload_len);
      d_frame_len = flexframegen_getframelen(d_fg);
      flexframegen_print(d_fg);
      set_relative_rate(1.0 * d_frame_len / ((double) d_payload_len));
    }

    void
    flex_tx_bc_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required) {
      assert (noutput_items % d_frame_len == 0);
      int nblocks = noutput_items / d_frame_len;
      int input_required = nblocks * d_payload_len;
      ninput_items_required[0] = input_required;
    }

    int
    flex_tx_bc_impl::general_work(int noutput_items,
                                  gr_vector_int &ninput_items,
                                  gr_vector_const_void_star &input_items,
                                  gr_vector_void_star &output_items) {

      gr::thread::scoped_lock guard(d_setlock);
      assert (noutput_items % d_frame_len == 0);
      const unsigned char *in = (const unsigned char *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];
      std::vector<tag_t> tags;
      tag_t current_tag;
      get_tags_in_window(
              tags, // Tags will be saved here
              0, // Port 0
              0, // Start of range
              ninput_items[0]// End of range
      );

      for(std::vector<tag_t>::iterator it = tags.begin(); it != tags.end(); ++it) {
          if(it->key == pmt::string_to_symbol("modulation")); // use gr_tags::key_time
          {
            pmt::pmt_t modulation = it->value;
            printf("Got modulation key\n");
            pmt::to_bool(modulation) ? set_modulation(0) : set_modulation(1);
          }
      }

      int byte_count = 0;

      static unsigned int frame_count = 0;
      unsigned int total_items = 0;
      int frame_complete = 0;

      // Make header
      while (total_items < noutput_items) {
        memcpy(d_header, &frame_count, sizeof(unsigned int));
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
        while (!frame_complete && total_items < noutput_items) {
          frame_complete = flexframegen_write_samples(d_fg, d_outbuf, d_buf_len);
          memcpy(out, d_outbuf, d_buf_len * sizeof(gr_complex));
          out += d_buf_len;
          total_items += d_buf_len;
        }
      }


      assert(total_items == noutput_items);
      consume_each(d_payload_len * noutput_items / d_frame_len);

      return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

