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

#ifndef INCLUDED_LIQUIDDSP_FLEX_RX_CB_IMPL_H
#define INCLUDED_LIQUIDDSP_FLEX_RX_CB_IMPL_H

#include <liquiddsp/flex_rx_cb.h>
#include <liquid/liquid.h>

struct packet_info{
    unsigned char *  _header;
    int              _header_valid;
    unsigned char *  _payload;
    unsigned int     _payload_len;
    framesyncstats_s _stats;
    gr_complex *     _frame_symbols;
    unsigned int     _num_frames;
    int              _payload_valid;
};

namespace gr {
  namespace liquiddsp {

    class flex_rx_cb_impl : public flex_rx_cb
    {
     private:
      flexframesync d_fs;
      struct packet_info *d_info;
      static const unsigned int d_inbuf_len = 256;


    public:
      flex_rx_cb_impl();
      ~flex_rx_cb_impl();



      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);
      static int callback(
              unsigned char *  _header,
              int              _header_valid,
              unsigned char *  _payload,
              unsigned int     _payload_len,
              int              _payload_valid,
              framesyncstats_s _stats,
              void *           _userdata);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FLEX_RX_CB_IMPL_H */

