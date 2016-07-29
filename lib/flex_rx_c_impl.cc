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
#include "flex_rx_c_impl.h"
#include <liquid/liquid.h>

namespace gr {
  namespace liquiddsp {

    flex_rx_c::sptr
    flex_rx_c::make()
    {
      return gnuradio::get_initial_sptr
        (new flex_rx_c_impl());
    }

    /*
     * The private constructor
     */
    flex_rx_c_impl::flex_rx_c_impl()
      : gr::sync_block("flex_rx_c",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(0, 0, 0))
    {
      d_info = (struct packet_info *) malloc(sizeof(struct packet_info));
      d_info->_payload = (unsigned char *) malloc (sizeof(unsigned char) * 1280);
      d_info->_packet_history = (bool *)malloc(100*sizeof(bool));
      d_info->_print_debug = false;
      d_fs = flexframesync_create(callback, (void *) d_info);
      flexframesync_debug_enable(d_fs);
    }

    /*
     * Our virtual destructor.
     */
    flex_rx_c_impl::~flex_rx_c_impl()
    {
    }

    int
    flex_rx_c_impl::callback(
            unsigned char *  _header,
            int              _header_valid,
            unsigned char *  _payload,
            unsigned int     _payload_len,
            int              _payload_valid,
            framesyncstats_s _stats,
            void *           _userdata)
    {
      static unsigned int current_frame = 0;
      unsigned int header_number = 0;
      double average_fer = 0;
      struct packet_info *info = (struct packet_info *) _userdata;
      info->_payload = _payload;
      info->_header = _header;
      info->_header_valid = _header_valid;
      info->_stats = _stats;
      info->_payload_valid = _payload_valid;
      memcpy(&header_number, _header, sizeof(unsigned int));
      info->_packet_history[current_frame] = (_payload_valid && _header_valid);
      info->_print_debug = true;
      for(unsigned int i = 0; i < 100; i++){
        average_fer += info->_packet_history[i] ? 0.0 : 1.0/100;
      }
      printf("Header received %d Current frame Received: %d Average FER %.4f\n", header_number, current_frame, average_fer);
      current_frame++;
    }

    int
    flex_rx_c_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *) input_items[0];

      assert (noutput_items % d_inbuf_len == 0);
      unsigned int num_items = 0;
      while(num_items < noutput_items){
        flexframesync_execute(d_fs, in, d_inbuf_len);
        num_items += d_inbuf_len;
        in += d_inbuf_len;
      }

      if(d_info->_print_debug == true){
//        flexframesync_debug_print(d_fs, "debug.m");
        d_info->_print_debug = false;
      }


      assert(num_items == noutput_items);
      return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

