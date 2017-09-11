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


#ifndef INCLUDED_LIQUIDDSP_FLEX_RX_H
#define INCLUDED_LIQUIDDSP_FLEX_RX_H

#include <liquiddsp/api.h>
#include <gnuradio/sync_block.h>
#include <pmt/pmt.h>

namespace gr {
  namespace liquiddsp {

    /*!
     * \brief <+description of block+>
     * \ingroup liquiddsp
     *
     */
    class LIQUIDDSP_API flex_rx : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<flex_rx> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of liquiddsp::flex_rx.
       *
       * To avoid accidental use of raw pointers, liquiddsp::flex_rx's
       * constructor is in a private implementation
       * class. liquiddsp::flex_rx::make is the public interface for
       * creating new instances.
       */
      virtual unsigned long int get_num_received(unsigned int modulation, unsigned int inner_code, unsigned int outer_code) = 0;
      virtual unsigned long int get_num_correct(unsigned int modulation, unsigned int inner_code, unsigned int outer_code) = 0;
      static sptr make();
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FLEX_RX_H */

