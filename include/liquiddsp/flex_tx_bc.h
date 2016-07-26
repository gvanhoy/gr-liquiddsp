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


#ifndef INCLUDED_LIQUIDDSP_FLEX_TX_BC_H
#define INCLUDED_LIQUIDDSP_FLEX_TX_BC_H

#include <liquiddsp/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace liquiddsp {

    /*!
     * \brief <+description of block+>
     * \ingroup liquiddsp
     *
     */
    class LIQUIDDSP_API flex_tx_bc : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<flex_tx_bc> sptr;


        virtual void set_modulation(unsigned int modulation) = 0;
        virtual void set_inner_code(unsigned int inner_code) = 0;

      /*!
       * \brief Return a shared_ptr to a new instance of liquiddsp::flex_tx_bc.
       *
       * To avoid accidental use of raw pointers, liquiddsp::flex_tx_bc's
       * constructor is in a private implementation
       * class. liquiddsp::flex_tx_bc::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace liquiddsp
} // namespace gr

#endif /* INCLUDED_LIQUIDDSP_FLEX_TX_BC_H */

