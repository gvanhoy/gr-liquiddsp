#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
import pmt


class cognitive_engine(gr.sync_block):
    """
    docstring for block cognitive_engine
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="cognitive_engine",
            in_sig=[],
            out_sig=[])
        self.message_port_register_in(pmt.intern('packet_info'))
        self.set_msg_handler(pmt.intern('packet_info'), self.handler)
        self.message_port_register_out(pmt.intern('configuration'))

    def handler(self, packet_info):
        print packet_info