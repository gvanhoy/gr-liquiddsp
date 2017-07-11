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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <gnuradio/blocks/pdu.h>
#include "flex_rx_impl.h"

namespace gr {
  namespace liquiddsp {

    flex_rx::sptr
    flex_rx::make()
    {
      return gnuradio::get_initial_sptr
        (new flex_rx_impl());
    }

    /*
     * The private constructor
     */
    flex_rx_impl::flex_rx_impl()
      : gr::sync_block("flex_rx",
              gr::io_signature::make(0, 1, sizeof(gr_complex)),
              gr::io_signature::make(0, 0, 0))
    {
        d_info = (struct packet_info *) malloc(sizeof(struct packet_info));
        d_fs = flexframesync_create(callback, (void *) d_info);
        set_output_multiple(d_inbuf_len);
        message_port_register_out(pmt::mp("constellation"));
        message_port_register_out(pmt::mp("hdr_and_payload"));
    }

    /*
     * Our virtual destructor.
     */
    flex_rx_impl::~flex_rx_impl()
    {
        flexframesync_destroy(d_fs);
    }

    int
    flex_rx_impl::callback(
        unsigned char *_header,
        int _header_valid,
        unsigned char *_payload,
        unsigned int _payload_len,
        int _payload_valid,
        framesyncstats_s _stats,
        void *_userdata) {
      struct packet_info *info = (struct packet_info *) _userdata;
      info->_payload = _payload;
      info->_header = _header;
      info->_header_valid = _header_valid;
      info->_stats = _stats;
      info->_payload_valid = _payload_valid;
      info->_payload_len = _payload_len;
      info->_frame_symbols = _stats.framesyms;
      info->_num_frames++;
      info->_new_payload = true;
    }

    int
    flex_rx_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
        gr_complex *in = (gr_complex *) input_items[0];
      unsigned int num_items = 0;
      assert (noutput_items % d_inbuf_len == 0);
      while (num_items < noutput_items) {
        flexframesync_execute(d_fs, in, d_inbuf_len);
        num_items += d_inbuf_len;
        in += d_inbuf_len;
        if(d_info->_new_payload){
            pmt::pmt_t constellation_pmt = pmt::init_c32vector(d_info->_stats.num_framesyms, d_info->_stats.framesyms);
            pmt::pmt_t constellation_pdu(pmt::cons(pmt::PMT_NIL, constellation_pmt));
            pmt::pmt_t payload_pmt = pmt::init_u8vector(d_info->_payload_len, d_info->_payload);
            pmt::pmt_t payload_pdu(pmt::cons(pmt::PMT_NIL, payload_pmt));
            message_port_pub(pmt::mp("hdr_and_payload"), payload_pdu);
            message_port_pub(pmt::mp("constellation"), constellation_pdu);
            flexframesync_print(d_fs);
            d_info->_new_payload = false;
        }
      }
      // std::cout << "Processed " << num_items << " items." << std::endl;

      return num_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

