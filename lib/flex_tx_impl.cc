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
#include "flex_tx_impl.h"

namespace gr {
  namespace liquiddsp {

    flex_tx::sptr
    flex_tx::make(unsigned int modulation, unsigned int inner_code, unsigned int outer_code)
    {
      return gnuradio::get_initial_sptr
        (new flex_tx_impl(modulation, inner_code, outer_code));
    }

    /*
     * The private constructor
     */
    flex_tx_impl::flex_tx_impl(unsigned int modulation, unsigned int inner_code, unsigned int outer_code)
      : gr::sync_block("flex_tx",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)),
              d_modulation(modulation),
              d_inner_code(inner_code),
              d_outer_code(outer_code)
    {
        flexframegenprops_init_default(&d_fgprops);
        d_fg = flexframegen_create(&d_fgprops);
        message_port_register_out(pmt::mp("frame_symbols"));
        d_header = (unsigned char *) malloc(14*sizeof(unsigned char));
        message_port_register_in(PDU_PORT_ID);
        set_msg_handler(PDU_PORT_ID, boost::bind(&flex_tx_impl::send_pkt, this, _1));
    }

    /*
     * Our virtual destructor.
     */
    flex_tx_impl::~flex_tx_impl()
    {
    }

    void flex_tx_impl::send_pkt(pmt::pmt_t pdu){

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t bytes = pmt::cdr(pdu);
        bool frame_complete = false;

        // fill it with random bytes
        flexframegen_assemble(d_fg, d_header, d_payload, pmt::length(meta));
        unsigned int frame_len = flexframegen_getframelen(d_fg);
        std::vector<gr_complex> vec(frame_len);
        frame_complete = flexframegen_write_samples(d_fg, &vec.front(), frame_len);
        pmt::pmt_t vecpmt = pmt::init_c32vector(frame_len, vec);

        // send the vector
        pmt::pmt_t out_pdu(pmt::cons(pmt::PMT_NIL, vecpmt));
        message_port_pub(PDU_PORT_ID, out_pdu);
    }

    int
    flex_tx_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
        throw std::runtime_error("This is not a stream block.");
        return noutput_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

