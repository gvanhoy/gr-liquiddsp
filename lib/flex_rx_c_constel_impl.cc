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
#include <liquid/liquid.h>
#include "flex_rx_c_constel_impl.h"

namespace gr {
  namespace liquiddsp {

    flex_rx_c_constel::sptr
    flex_rx_c_constel::make(gr::msg_queue::sptr target_queue)
    {
      return gnuradio::get_initial_sptr
        (new flex_rx_c_constel_impl(target_queue));
    }

    /*
     * The private constructor
     */
    flex_rx_c_constel_impl::flex_rx_c_constel_impl(gr::msg_queue::sptr target_queue)
            : gr::sync_block("flex_rx_c_constel",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(0, 0, 0)),
        d_target_queue(target_queue)
    {
      d_info = (struct packet_info *) malloc(sizeof(struct packet_info));
      d_info->_payload = (unsigned char *) malloc (sizeof(unsigned char) * 5000);
      d_fs = flexframesync_create(callback, (void *) d_info);
    }

    /*
     * Our virtual destructor.
     */
    flex_rx_c_constel_impl::~flex_rx_c_constel_impl()
    {
      flexframesync_destroy(d_fs);
    }

    int
    flex_rx_c_constel_impl::callback(
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
      info->_payload_len = _payload_len;
      info->_frame_symbols = _stats.framesyms;
      info->_num_frames++;
    }

    int
    flex_rx_c_constel_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *) input_items[0];
      d_info->_num_frames = 0;
      unsigned int num_items = 0;
      int nItemsFromSync = 0;

//      printf("Requesting %d items\n", noutput_items);
      while(num_items < noutput_items){
        flexframesync_execute(d_fs, in, d_inbuf_len);
        num_items += d_inbuf_len;
        in += d_inbuf_len;
      }

      nItemsFromSync = d_info->_num_frames*d_info->_stats.num_framesyms;
//      printf("Produced %d items from framesync\n", nItemsFromSync);
      if (nItemsFromSync != 0){
        message::sptr msg = message::make(0, sizeof(gr_complex), noutput_items, sizeof(gr_complex)*(noutput_items));
        memcpy(msg->msg(), d_info->_frame_symbols, noutput_items);
        d_target_queue->insert_tail(msg);
      }

      return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

