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

#ifndef INCLUDED_LIQUIDDSP_FLEX_RX_C_IMPL_H
#define INCLUDED_LIQUIDDSP_FLEX_RX_C_IMPL_H

#include <liquiddsp/flex_rx_c.h>
#include <liquid/liquid.h>
#include <deque>

struct packet_info{
    unsigned char *  _header;
    int              _header_valid;
    unsigned char *  _payload;
    unsigned int     _payload_len;
    framesyncstats_s _stats;
    int              _payload_valid;
    bool *           _packet_history;
    bool             _print_debug;
};

namespace gr {
  namespace liquiddsp {

    class flex_rx_c_impl : public flex_rx_c
    {
     private:
        flexframesync d_fs;
        struct packet_info *d_info;
        static const unsigned int d_inbuf_len = 256;

     public:
      flex_rx_c_impl();
      ~flex_rx_c_impl();
      static int callback(
              unsigned char *  _header,
              int              _header_valid,
              unsigned char *  _payload,
              unsigned int     _payload_len,
              int              _payload_valid,
              framesyncstats_s _stats,
              void *           _userdata);

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FLEX_RX_C_IMPL_H */

