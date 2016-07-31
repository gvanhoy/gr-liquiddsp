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

#ifndef INCLUDED_LIQUIDDSP_FLEX_TX_C_IMPL_H
#define INCLUDED_LIQUIDDSP_FLEX_TX_C_IMPL_H

#include <liquiddsp/flex_tx_c.h>
#include <gnuradio/msg_queue.h>
#include <liquid/liquid.h>

namespace gr {
  namespace liquiddsp {

    class flex_tx_c_impl : public flex_tx_c
    {
     private:
        size_t	 	                d_item_size;
        msg_queue::sptr	          d_msgq;
        message::sptr	            d_msg;
        static const unsigned int d_buf_len = 512;
        unsigned int              d_modulation;
        unsigned int              d_inner_code;
        unsigned int              d_outer_code;
        unsigned int              d_payload_len;
        unsigned int              d_frame_len;
        unsigned char           * d_payload;
        unsigned char           * d_header;
        gr_complex              * d_outbuf;
        flexframegenprops_s       d_fgprops;
        flexframegen              d_fg;

        void get_message();
        void set_modulation(unsigned int modulation);
        void set_inner_code(unsigned int inner_code);
        void set_outer_code(unsigned int outer_code);

    public:
        flex_tx_c_impl(size_t item_size, int msgq_limit);

        flex_tx_c_impl(size_t item_size, msg_queue::sptr msgq);
      ~flex_tx_c_impl();

      msg_queue::sptr msgq() const { return d_msgq; }

       void reconfigure();
      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FLEX_TX_C_IMPL_H */

