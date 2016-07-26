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
        d_header = (unsigned char *)malloc(14*sizeof(unsigned char));
        d_payload = (unsigned char *)malloc(d_payload_len*sizeof(unsigned char));
        d_outbuf = (gr_complex *) malloc(d_buf_len*sizeof(gr_complex));
        for(int i = 0; i < 14; i++) d_header[i] = i;
        flexframegen_assemble(d_fg, d_header, d_payload, d_payload_len);
        d_frame_len = flexframegen_getframelen(d_fg);
        printf("Setting relative rate to: %.3f.\n", 1.0*d_payload_len/((double) d_frame_len));
        set_relative_rate(1.0*d_payload_len/((double) d_frame_len));
        set_output_multiple (d_frame_len);
    }

    /*
     * Our virtual destructor.
     */
    flex_tx_bc_impl::~flex_tx_bc_impl()
    {
        flexframegen_destroy(d_fg);
        free(d_outbuf);
        free(d_header);
        free(d_payload);
    }

    void
    flex_tx_bc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        assert (noutput_items % d_frame_len == 0);
        ninput_items_required[0] = (int)((double) d_payload_len/((double) d_frame_len)*noutput_items);
    }

    int
    flex_tx_bc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        assert (noutput_items % d_frame_len == 0);

        unsigned char *in = (unsigned char *) input_items[0];
        unsigned char *inbuf = in;
        gr_complex *out = (gr_complex *) output_items[0];
        gr_complex *front = out;
        int byte_count = 0;

        unsigned char frame_count;
        unsigned int total_items = 0;
        int frame_complete = 0;

        // Make header
        for(int i = 1; i < 14; i++) d_header[i] = i;
        while(byte_count < ((int) ninput_items[0]) - d_payload_len && total_items < 32768/2) {
//            printf("Input Items: %d Frame: %d Byte: %d\n", ninput_items[0], frame_count, byte_count);
            d_header[0] = frame_count;
            frame_count > 255 ? frame_count = 0 : frame_count++;
            memcpy(d_payload, inbuf, d_payload_len);
            inbuf += d_payload_len;
            byte_count += d_payload_len;
            // Assemble the frame
            while (!flexframegen_is_assembled(d_fg)) {
                flexframegen_assemble(d_fg, d_header, d_payload, d_payload_len);
            }
//            printf("Frame assembled.\n");

            // Make the frame in blocks
            frame_complete = 0;
            while (!frame_complete && total_items < 32768/2){
                frame_complete = flexframegen_write_samples(d_fg, d_outbuf, d_buf_len);
                memcpy(front, d_outbuf, d_buf_len*sizeof(gr_complex));
                front += d_buf_len;
                total_items += d_buf_len;
//                printf("Wrote a total of %d samples.\n", total_items);
            }
//            printf("Frame written.\n");

            // Get frame length
        }

//        printf("%d items ready.\n", total_items);
//        printf("Consuming Items.\n");
        consume_each (total_items);
//        printf("Items Consumed.\n");

      // Tell runtime system how many output items we produced.
      return total_items;
    }

  } /* namespace liquiddsp */
} /* namespace gr */

