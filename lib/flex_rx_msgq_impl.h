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

#ifndef INCLUDED_LIQUIDDSP_FLEX_RX_MSGQ_IMPL_H
#define INCLUDED_LIQUIDDSP_FLEX_RX_MSGQ_IMPL_H

#include <liquiddsp/flex_rx_msgq.h>
#include <liquid/liquid.h>
#include <gnuradio/msg_queue.h>

struct packet_info {
  unsigned char *_header;
  int _header_valid;
  unsigned char *_payload;
  unsigned int _payload_len;
  framesyncstats_s _stats;
  gr_complex *_frame_symbols;
  unsigned int _num_frames;
  int _payload_valid;
  bool _new_payload;
};

namespace gr {
  namespace liquiddsp {

    class flex_rx_msgq_impl : public flex_rx_msgq {
    private:
      flexframesync d_fs;
      struct packet_info *d_info;
      gr::msg_queue::sptr d_bit_queue;
      gr::msg_queue::sptr d_symbol_queue;
      static const unsigned int d_inbuf_len = 1024;
      int d_rx_mod_scheme;
      int d_rx_outer_code;
      int d_rx_inner_code;
      int d_packet_window_size;


      void get_mod_scheme(unsigned int mod_scheme);
      void get_outer_code(unsigned int outer_code);
      void get_inner_code(unsigned int inner_code);

    public:
      flex_rx_msgq_impl(gr::msg_queue::sptr bit_queue, gr::msg_queue::sptr symbol_queue);

      ~flex_rx_msgq_impl();

      gr::msg_queue::sptr bit_msgq() const { return d_bit_queue; }
      gr::msg_queue::sptr symbol_msgq() const { return d_symbol_queue; }

      static int callback(
          unsigned char *_header,
          int _header_valid,
          unsigned char *_payload,
          unsigned int _payload_len,
          int _payload_valid,
          framesyncstats_s _stats,
          void *_userdata);

      // Where all the action really happens
      int work(int noutput_items,
               gr_vector_const_void_star &input_items,
               gr_vector_void_star &output_items);
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FLEX_RX_MSGQ_IMPL_H */

