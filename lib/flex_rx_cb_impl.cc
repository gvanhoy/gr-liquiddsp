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
#include "flex_rx_cb_impl.h"
#include <liquid/liquid.h>
#include <stdio.h>

namespace gr {
  namespace liquiddsp {

    flex_rx_cb::sptr
    flex_rx_cb::make()
    {
      return gnuradio::get_initial_sptr
        (new flex_rx_cb_impl());
    }



//      static int ios[] = {sizeof(char), sizeof(gr_complex)};
//      static std::vector<int> iosig(ios, ios+sizeof(ios)/sizeof(int));
    /*
     * The private constructor
     */
    flex_rx_cb_impl::flex_rx_cb_impl()
      : gr::block("flex_rx_cb",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)))
    {
      d_info = (struct packet_info *) malloc(sizeof(struct packet_info));
      d_info->_payload_len = 4096;
      d_info->_payload = (unsigned char *) malloc (sizeof(unsigned char) * d_info->_payload_len);
      d_fs = flexframesync_create(callback, (void *) d_info);
      set_output_multiple(d_inbuf_len);
    }

    /*
     * Our virtual destructor.
     */
    flex_rx_cb_impl::~flex_rx_cb_impl()
    {
      free(d_info->_payload);
      free(d_info);
      flexframesync_destroy(d_fs);
    }

    int
    flex_rx_cb_impl::callback(
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
      info->_num_frames++;
      memcpy(info->_frame_symbols, _stats.framesyms, _stats.num_framesyms*sizeof(gr_complex));
      info->_payload_valid = _payload_valid;
    }


    void
    flex_rx_cb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      assert(noutput_items % d_inbuf_len == 0);
      int nblocks = noutput_items / d_inbuf_len;
      ninput_items_required[0] = nblocks*d_inbuf_len;
    }

    int
    flex_rx_cb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      assert (noutput_items % d_inbuf_len == 0);
      gr_complex *in = (gr_complex *) input_items[0];
      unsigned int num_items = 0;
      gr_complex *out_symbols = (gr_complex *) output_items[0];
      d_info->_frame_symbols = out_symbols;
      d_info->_num_frames = 0;

      while(num_items < noutput_items){
        flexframesync_execute(d_fs, in, d_inbuf_len);
        num_items += d_inbuf_len;
        in += d_inbuf_len;
      }

//      flexframesync_print(d_fs);
      assert(num_items == noutput_items);
      printf("Produced %d items\n", d_info->_num_frames*d_info->_stats.num_framesyms);

      consume_each(noutput_items);
      return d_info->_num_frames*d_info->_stats.num_framesyms;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

