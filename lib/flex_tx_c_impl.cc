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
#include "flex_tx_c_impl.h"

namespace gr {
  namespace liquiddsp {

    flex_tx_c::sptr
    flex_tx_c::make(size_t item_size, int msgq_limit) {
      return gnuradio::get_initial_sptr
              (new flex_tx_c_impl(item_size, msgq_limit));
    }

    flex_tx_c::sptr
    flex_tx_c::make(size_t item_size, msg_queue::sptr msgq)
    {
      return gnuradio::get_initial_sptr
        (new flex_tx_c_impl(item_size, msgq));
    }

    /*
     * The private constructor
     */
    flex_tx_c_impl::flex_tx_c_impl(size_t item_size, msg_queue::sptr msgq)
      : gr::sync_block("flex_tx_c",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
        d_item_size(item_size), d_msgq(msgq)
    {
      flexframegenprops_init_default(&d_fgprops);
      d_fg = flexframegen_create(&d_fgprops);
      d_outbuf = (gr_complex *) malloc(d_buf_len * sizeof(gr_complex));
      d_header = (unsigned char *) malloc(14 * sizeof(unsigned char));
      set_output_multiple(d_buf_len);
    }

    flex_tx_c_impl::flex_tx_c_impl(size_t item_size, int msgq_limit)
            : sync_block("flex_tx_c",
                         io_signature::make(0, 0, 0),
                         io_signature::make(1, 1, sizeof(gr_complex))),
              d_item_size(item_size), d_msgq(msg_queue::make(msgq_limit))
    {
      flexframegenprops_init_default(&d_fgprops);
      d_fg = flexframegen_create(&d_fgprops);
      d_outbuf = (gr_complex *) malloc(d_buf_len * sizeof(gr_complex));
      d_header = (unsigned char *) malloc(14 * sizeof(unsigned char));
      set_output_multiple(d_buf_len);
    }

    /*
     * Our virtual destructor.
     */
    flex_tx_c_impl::~flex_tx_c_impl()
    {
      flexframegen_destroy(d_fg);
      free(d_outbuf);
      free(d_payload);
      free(d_header);
    }

    void
    flex_tx_c_impl::set_modulation(unsigned int modulation) {
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
        default:
          printf("Unsupported Modulation Defaulting to BPSK.\n");
          d_modulation = LIQUID_MODEM_PSK2;
          break;
      }
    }

    void
    flex_tx_c_impl::set_inner_code(unsigned int inner_code) {
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
        default:
          printf("Unsupported FEC Defaulting to none.\n");
          d_inner_code = LIQUID_FEC_NONE;
          break;
      }
    }

    void
    flex_tx_c_impl::set_outer_code(unsigned int outer_code) {
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
        default:
          printf("Unsupported FEC Defaulting to none.\n");
          d_outer_code = LIQUID_FEC_NONE;
          break;
      }
    }

    void
    flex_tx_c_impl::reconfigure() {
      d_fgprops.mod_scheme = d_modulation;
      d_fgprops.fec0 = d_inner_code;
      d_fgprops.fec1 = d_outer_code;
      flexframegen_setprops(d_fg, &d_fgprops);
      flexframegen_assemble(d_fg, d_header, d_payload, d_payload_len);
      d_frame_len = flexframegen_getframelen(d_fg);
//      flexframegen_print(d_fg);
    }

    void
    flex_tx_c_impl::get_message()
    {
      static unsigned int frame_number = 0;
      set_modulation(d_msg->msg()[0]);
      set_inner_code(d_msg->msg()[1]);
      set_outer_code(d_msg->msg()[2]);
      d_payload_len = (d_msg->length() - 3);
//      printf("Got modulation %d, inner code %d, outer code %d\n", d_msg->msg()[0], d_msg->msg()[1], d_msg->msg()[2]);
      d_payload = (unsigned char *) malloc(d_payload_len*sizeof(unsigned char));
      memcpy(d_payload, d_msg->msg() + 3, d_payload_len*sizeof(unsigned char));
      memcpy(d_header, &frame_number, sizeof(unsigned int));
      memset(d_header + sizeof(unsigned int), 0, 14 - sizeof(unsigned int));
      frame_number++;
      reconfigure();
    }


    int
    flex_tx_c_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      assert (noutput_items % d_buf_len == 0);

      gr_complex *out = (gr_complex *) output_items[0];

      unsigned int num_items = 0;
      static int frame_complete = 0;

      while(num_items < noutput_items){
        //Have message in queue
        if (d_msg) {
          //But still working on previous frame
          if(!frame_complete) {
            frame_complete = flexframegen_write_samples(d_fg, d_outbuf, d_buf_len);
            memcpy(out, d_outbuf, d_buf_len * sizeof(gr_complex));
            out += d_buf_len;
            num_items += d_buf_len;
          }
          // Ready for new frame
          else{
            frame_complete = 0;
            d_msg.reset();
          }
        }
        else{
          // No more messages, but still need to produce more items
          if (d_msgq->empty_p()) {
            memset(out + num_items, 0, sizeof(gr_complex)*(noutput_items - num_items));
            return noutput_items;
          }
          else{
            d_msg = d_msgq->delete_head();     // this should not block since it returns when no message exists.
            get_message();
          }
        }
      }
      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

