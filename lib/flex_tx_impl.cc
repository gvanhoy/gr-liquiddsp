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
              d_outer_code(outer_code),
              d_num_frames(0)
    {
        flexframegenprops_init_default(&d_fgprops);
        d_fgprops.check = LIQUID_CRC_24;      // data validity check
        set_inner_code(inner_code);      // inner FEC scheme
        set_outer_code(outer_code);      // outer FEC scheme
        set_modulation(modulation);
        d_fg = flexframegen_create(&d_fgprops);
        message_port_register_out(PDU_PORT_ID);
        d_header = (unsigned char *) malloc(14*sizeof(unsigned char));
        memset(d_header, 0, 14);
        message_port_register_in(PDU_PORT_ID);
        set_msg_handler(PDU_PORT_ID, boost::bind(&flex_tx_impl::send_pkt, this, _1));

        message_port_register_in(pmt::mp("configuration"));
        set_msg_handler(pmt::mp("configuration"), boost::bind(&flex_tx_impl::configure, this, _1));
    }

    /*
     * Our virtual destructor.
     */
    flex_tx_impl::~flex_tx_impl()
    {
        flexframegen_destroy(d_fg);
    }

    void
    flex_tx_impl::set_modulation(unsigned int modulation) {
      switch (modulation) {
        case 0:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK2;
          break;
        case 1:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK4;
          break;
        case 2:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK8;
          break;
        case 3:
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK16;
          break;
        case 4:
          d_fgprops.mod_scheme = LIQUID_MODEM_DPSK2;
          break;
        case 5:
          d_fgprops.mod_scheme = LIQUID_MODEM_DPSK4;
          break;
        case 6:
          d_fgprops.mod_scheme = LIQUID_MODEM_DPSK8;
          break;
        case 7:
          d_fgprops.mod_scheme = LIQUID_MODEM_ASK4;
          break;
        case 8:
          d_fgprops.mod_scheme = LIQUID_MODEM_QAM16;
          break;
        case 9:
          d_fgprops.mod_scheme = LIQUID_MODEM_QAM32;
          break;
        case 10:
          d_fgprops.mod_scheme = LIQUID_MODEM_QAM64;
          break;
        default:
            std::cout << "Unsupported Modulation Defaulting to BPSK." << std::endl;
          d_fgprops.mod_scheme = LIQUID_MODEM_PSK2;
          break;
      }
    }

    void
    flex_tx_impl::set_inner_code(unsigned int inner_code) {
      switch (inner_code) {
        case 0:
          d_fgprops.fec0 = LIQUID_FEC_NONE;
          break;
        case 1:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27;
          break;
        case 2:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P23;
          break;
        case 3:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P45;
          break;
        case 4:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P56;
          break;
        case 5:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P67;
          break;
        case 6:
          d_fgprops.fec0 = LIQUID_FEC_CONV_V27P78;
          break;
        default:
            std::cout << "Unsupported FEC Defaulting to none." << std::endl;
          d_fgprops.fec0 = LIQUID_FEC_NONE;
          break;
      }
    }

    void
    flex_tx_impl::set_outer_code(unsigned int outer_code) {
      switch (outer_code) {
        case 0:
          d_fgprops.fec1 = LIQUID_FEC_NONE;
          break;
        case 1:
          d_fgprops.fec1 = LIQUID_FEC_GOLAY2412;
          break;
        case 2:
          d_fgprops.fec1 = LIQUID_FEC_RS_M8;
          break;
        case 3:
          d_fgprops.fec1 = LIQUID_FEC_HAMMING74;
          break;
        case 4:
          d_fgprops.fec1 = LIQUID_FEC_HAMMING128;
          break;
        case 5:
          d_fgprops.fec1 = LIQUID_FEC_SECDED2216;
          break;
        case 6:
          d_fgprops.fec1 = LIQUID_FEC_SECDED3932;
          break;
        case 7:
          d_fgprops.fec1 = LIQUID_FEC_SECDED7264;
          break;
        default:
          std::cout << "Unsupported FEC Defaulting to none." << std::endl;
          d_fgprops.fec1 = LIQUID_FEC_NONE;
          break;
      }
    }

    void flex_tx_impl::configure(pmt::pmt_t configuration){
        if(pmt::dict_has_key(configuration, pmt::mp("modulation"))) set_modulation(pmt::to_long(pmt::dict_ref(configuration, pmt::mp("modulation"), pmt::PMT_NIL)));
        if(pmt::dict_has_key(configuration, pmt::mp("inner_code"))) set_inner_code(pmt::to_long(pmt::dict_ref(configuration, pmt::mp("inner_code"), pmt::PMT_NIL)));
        if(pmt::dict_has_key(configuration, pmt::mp("outer_code"))) set_outer_code(pmt::to_long(pmt::dict_ref(configuration, pmt::mp("outer_code"), pmt::PMT_NIL)));
        flexframegen_setprops(d_fg, d_fgprops);
    }

    void flex_tx_impl::send_pkt(pmt::pmt_t pdu){

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t bytes = pmt::cdr(pdu);

        // fill it with random bytes
        std::vector<uint8_t> payload = pmt::u8vector_elements(bytes);
        flexframegen_assemble(d_fg, d_header, &payload.front(), pmt::length(bytes));
        unsigned int frame_len = flexframegen_getframelen(d_fg);
        std::vector<gr_complex> vec(frame_len);
        flexframegen_write_samples(d_fg, &vec.front(), frame_len);
        pmt::pmt_t vecpmt = pmt::init_c32vector(frame_len, vec);

        // send the vector
        pmt::pmt_t out_pdu(pmt::cons(pmt::PMT_NIL, vecpmt));
        message_port_pub(PDU_PORT_ID, out_pdu);
        d_num_frames++;
        // std::cout << "Sent " << d_num_frames << " frames" << std::endl;
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

