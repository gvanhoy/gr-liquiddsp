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
              gr::io_signature::make(1, 1, sizeof(unsigned char)))
    {
      d_info = (struct packet_info *) malloc(sizeof(struct packet_info));
      d_info->_payload = (unsigned char *) malloc (sizeof(unsigned char) * 4096*8);
      d_fs = flexframesync_create(callback, (void *) d_info);
    }

    /*
     * Our virtual destructor.
     */
    flex_rx_cb_impl::~flex_rx_cb_impl()
    {
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
      info->_payload_len = _payload_len;
      info->_header = _header;
      info->_header_valid = _header_valid;
      info->_stats = _stats;
      info->_payload_valid = _payload_valid;
    }


    void
    flex_rx_cb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    flex_rx_cb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *) input_items[0];
      unsigned char * out = (unsigned char *) output_items[0];
//      gr_complex * out_symbols = (gr_complex *) output_items[1];
//      gr_complex * out_symbols = (gr_complex *) output_items[0];

      static unsigned char previous_header;

      flexframesync_execute(d_fs, in, (unsigned int) ninput_items[0]);
//      printf("Working on %d items\n", (unsigned int) ninput_items[0]);
      if (d_info->_payload_valid && d_info->_header_valid) {
        previous_header = *d_info->_header;
        printf("Header #%d : %s\n", *(d_info->_header), d_info->_header_valid ? "valid" : "INVALID!");
        memmove(out, d_info->_payload, d_info->_payload_len*sizeof(unsigned char));
      }

//      printf("Produced %d symbols\n", d_info->_stats.num_framesyms);
//      memmove(out_symbols, d_info->_stats.framesyms, d_info->_stats.num_framesyms);
      flexframesync_print(d_fs);
      consume_each(d_info->_payload_len*sizeof(unsigned char));
      // Tell runtime system how many output items we produced.
      return d_info->_payload_len*sizeof(unsigned char);
    }

  } /* namespace liquiddsp */
} /* namespace gr */

