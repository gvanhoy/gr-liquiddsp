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

#ifndef INCLUDED_LIQUIDDSP_FLEX_RX_IMPL_H
#define INCLUDED_LIQUIDDSP_FLEX_RX_IMPL_H

#include <liquiddsp/flex_rx.h>
#include <liquid/liquid.h>

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

typedef struct performance_info_struct{
	unsigned long int num_received;
	unsigned long int num_correct;
} performance_info;

namespace gr {
  namespace liquiddsp {

    class flex_rx_impl : public flex_rx
    {
     private:
         flexframesync d_fs;
         struct packet_info *d_info;
         static const unsigned int d_inbuf_len = 256;
		static int callback(
          unsigned char *_header,
          int _header_valid,
          unsigned char *_payload,
          unsigned int _payload_len,
          int _payload_valid,
          framesyncstats_s _stats,
          void *_userdata);
		performance_info d_performance_matrix[11][7][8];
		int d_rx_mod_scheme;
        int d_rx_outer_code;
		int d_rx_inner_code;
        void get_mod_scheme(unsigned int mod_scheme);
        void get_outer_code(unsigned int outer_code);
		void get_inner_code(unsigned int inner_code);

     public:
      flex_rx_impl();
      ~flex_rx_impl();

      pmt::pmt_t get_performance_info(unsigned int modulation, unsigned int inner_code, unsigned int outer_code);

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FLEX_RX_IMPL_H */

