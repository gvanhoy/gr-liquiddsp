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
#include "flex_tx_bc_impl.h"
#include <liquid/liquid.h>

namespace gr {
  namespace liquiddsp {

    flex_tx_bc::sptr
    flex_tx_bc::make()
    {
      return gnuradio::get_initial_sptr
        (new flex_tx_bc_impl());
    }

    /*
     * The private constructor
     */
    flex_tx_bc_impl::flex_tx_bc_impl()
      : gr::block("flex_tx_bc",
                            gr::io_signature::make(1, -1, sizeof(char)),
                            gr::io_signature::make(1, -1, sizeof(gr_complex)))
    {
        flexframegenprops_init_default(&d_fgprops);
        d_fgprops.check = LIQUID_CRC_NONE;      // data validity check
        d_fgprops.fec0 = LIQUID_FEC_NONE;      // inner FEC scheme
        d_fgprops.fec1 = LIQUID_FEC_NONE;      // outer FEC scheme
        d_fgprops.mod_scheme = LIQUID_MODEM_QAM16;
        d_fg = flexframegen_create(&d_fgprops);
    }

    /*
     * Our virtual destructor.
     */
    flex_tx_bc_impl::~flex_tx_bc_impl()
    {
        flexframegen_destroy(d_fg);
    }

    void
    flex_tx_bc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    flex_tx_bc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const unsigned char *in = (const unsigned char *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];


        gr_complex *outbuf = new gr_complex[10000000];
        unsigned int payload_len = 1024;
        int byte_count = payload_len;
        unsigned char header[14]; // Liquid hardcodes this as the length for the header
        unsigned char payload[1024];
        static unsigned char frame_count;
        unsigned int frame_len = 0;
        unsigned int total_items = 0;
        int frame_complete = 0;
        for(int i = 1; i < 14; i++){
            header[i] = i;
        }

        while(byte_count < ((int) ninput_items[0])) {
            header[0] = frame_count;
            frame_count > 255 ? frame_count = 0 : frame_count++;
            for (int i = 0; i < payload_len; i++) {
                payload[i] = in[i + byte_count];
            }


            while(!flexframegen_is_assembled(d_fg)) {
                printf("Frame assembled.\n");
                flexframegen_assemble(d_fg, header, payload, payload_len);
            }
            frame_len = flexframegen_getframelen(d_fg);
            printf("Input Items: %d Frame: %d Byte: %d Frame_len: %d\n", ninput_items[0], frame_count, byte_count, frame_len);

            flexframegen_write_samples(d_fg, outbuf, payload_len);
            printf("Frame written.\n");

            byte_count += payload_len;
            total_items += frame_len;
        }

        printf("%d items ready.\n", total_items);
        memcpy(out, outbuf, noutput_items);
        delete[] outbuf;
        consume_each (noutput_items);

      // Tell runtime system how many output items we produced.
      return total_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

