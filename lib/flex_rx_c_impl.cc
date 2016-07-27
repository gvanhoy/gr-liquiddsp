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
      message_port_register_in(pmt::mp("symbols"));
      d_info = (struct packet_info *) malloc(sizeof(struct packet_info));
      d_info->_payload = (unsigned char *) malloc (sizeof(unsigned char) * 5000);
      d_fs = flexframesync_create(callback, (void *) d_info);
      set_output_multiple(d_inbuf_len);
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
      struct packet_info *info = (struct packet_info *) _userdata;
      info->_payload = _payload;
      info->_header = _header;
      info->_header_valid = _header_valid;
      info->_stats = _stats;
      info->_payload_valid = _payload_valid;
      if(_payload_valid && _header_valid){
        printf("Message Length %d: ", _payload_len);
        for(int i = 0; i < _payload_len; i++){
          printf("%c", _payload[i]);
        }
        printf("\n");
      }
//      framesyncstats_print(&_stats);
    }

    int
    flex_rx_c_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *) input_items[0];

      assert (noutput_items % d_inbuf_len == 0);
      unsigned int num_items = 0;
      framedatastats_s stats = flexframesync_get_framedatastats(d_fs);
//      printf("Dropped Packet Rate: %.4f\n", 1.0 - ((double) stats.num_payloads_valid)/((double) stats.num_frames_detected));
      while(num_items < noutput_items){
        flexframesync_execute(d_fs, in, d_inbuf_len);
        num_items += d_inbuf_len;
        in += d_inbuf_len;
//        flexframesync_print(d_fs);
      }

      assert(num_items == noutput_items);
      return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

