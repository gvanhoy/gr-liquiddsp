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
        self.database = DatabaseControl()
        self.message_port_register_in(pmt.intern('packet_info'))
        self.set_msg_handler(pmt.intern('packet_info'), self.handler)
        self.message_port_register_out(pmt.intern('configuration'))
        self.num_packets = 0

    def handler(self, packet_info):
        self.num_packets += 1
        modulation = pmt.dict_ref(packet_info, pmt.intern("modulation"), pmt.PMT_NIL)
        inner_code = pmt.dict_ref(packet_info, pmt.intern("inner_code"), pmt.PMT_NIL)
        outer_code = pmt.dict_ref(packet_info, pmt.intern("outer_code"), pmt.PMT_NIL)
        config_id = modulation*11 + inner_code*7 + outer_code + 1
        configuration = make_Conf(config_id, modulation, inner_code, outer_code)
        config11 = Conf_map(modulation, inner_code, outer_code)
        goodput = math.log(config11.constellationN, 2) * (float(config11.outercodingrate)) * (float(config11.innercodingrate)) * payload_valid[0]
        self.database.write_configuration(configuration,
                                          pmt.dict_ref(packet_info, pmt.intern("header_valid"), pmt.PMT_NIL),
                                          pmt.dict_ref(packet_info, pmt.intern("payload_valid"), pmt.PMT_NIL),
                                          goodput)

        ce_configuration = EGreedy(self.num_packets, .01, 1)
        if ce_configuration is not None:
            new_configuration = pmt.make_dict()
            new_ce_configuration = ce_configuration[0]
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("modulation"), pmt.from_long(new_ce_configuration.modulation))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("inner_code"), pmt.from_long(new_ce_configuration.innercode))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("outer_code"), pmt.from_long(new_ce_configuration.outercode))
            self.message_port_pub(pmt.intern('configuration'), new_configuration)
