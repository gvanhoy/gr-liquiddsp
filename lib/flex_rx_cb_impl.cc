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
//              gr::io_signature::makev(2, 2, iosig))
              gr::io_signature::make(1, 1, sizeof(unsigned char *)))

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
      info->_frame_symbols += _stats.num_framesyms;
      info->_payload_valid = _payload_valid;
    }


    void
    flex_rx_cb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      assert(noutput_items % d_inbuf_len == 0);
//      printf("Rx: Need %.3f relative items\n", ((1.0 * d_info->_stats.num_framesyms )/((double) d_info->_payload_len)*noutput_items));
//      ninput_items_required[0] = int ((1.0 * d_info->_stats.num_framesyms )/((double) d_info->_payload_len)*noutput_items);
      ninput_items_required[0] = noutput_items;
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

//      printf("Got %d items. Producing %d\n", ninput_items[0], noutput_items);
      while(num_items < noutput_items){
        flexframesync_execute(d_fs, in, d_inbuf_len);
        num_items += d_inbuf_len;
        in += d_inbuf_len;
//        printf("Processed %d items\n", num_items);
      }
//      if (d_info->_payload_valid && d_info->_header_valid && (previous_header != *(d_info->_header))) {
//        previous_header = *(d_info->_header);
//        printf("Rx: Header #%d : %s\n", *(d_info->_header), d_info->_header_valid ? "valid" : "INVALID!");
//        memcpy(out_bytes, d_info->_payload, d_info->_payload_len*sizeof(unsigned char));
//        printf("Rx: Setting relative rate to: %.2f\n", (1.0 * d_info->_stats.num_framesyms)/((double) d_info->_payload_len));
//        set_relative_rate((1.0 * d_info->_stats.num_framesyms)/((double) d_info->_payload_len));
//        consume_each(noutput_items);
//        return d_info->_payload_len;
//      }

//      printf("Produced %d symbols\n", d_info->_stats.num_framesyms);
//      memmove(out_symbols, d_info->_stats.framesyms, d_info->_stats.num_framesyms);
      flexframesync_print(d_fs);
      // Tell runtime system how many output items we produced.
      assert(num_items == noutput_items);
      consume_each(noutput_items);
//      printf("Consumed %d items.\n", num_items);
      return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

