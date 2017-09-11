from gnuradio import blocks
from gnuradio import gr
import es
import liquiddsp
import pmt
import numpy as np


class FlexTransceiver(gr.hier_block2):
    def __init__(self, samp_rate=200000):
        gr.hier_block2.__init__(self,
                                "Flex Transceiver",
                                gr.io_signature(0, 0, gr.sizeof_gr_complex),
                                gr.io_signature(0, 0, gr.sizeof_gr_complex))

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000

        ##################################################
        # Blocks
        ##################################################
        self.liquiddsp_flex_tx_0 = liquiddsp.flex_tx(0, 0, 0)
        self.liquiddsp_flex_rx_0 = liquiddsp.flex_rx()
        self.es_source_0 = es.source(1 * [gr.sizeof_gr_complex], 1, 2, 0)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex * 1, samp_rate, True)
        self.blocks_random_pdu_0 = blocks.random_pdu(50, 200, chr(0xFF), 2)
        self.blocks_message_strobe_random_0 = blocks.message_strobe_random(pmt.intern("TEST"), blocks.STROBE_POISSON,
                                                                           1000, 100)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_random_0, 'strobe'), (self.blocks_random_pdu_0, 'generate'))
        self.msg_connect((self.blocks_random_pdu_0, 'pdus'), (self.liquiddsp_flex_tx_0, 'pdus'))
        self.msg_connect((self.liquiddsp_flex_tx_0, 'pdus'), (self.es_source_0, 'schedule_event'))
        self.connect((self.blocks_throttle_0, 0), (self.liquiddsp_flex_rx_0, 0))
        self.connect((self.es_source_0, 0), (self.blocks_throttle_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def send_packet(self, modulation, inner_code, outer_code, payload):
        self.liquiddsp_flex_tx_0.set_modulation(modulation)
        self.liquiddsp_flex_tx_0.set_inner_code(inner_code)
        self.liquiddsp_flex_tx_0.set_outer_code(outer_code)
        msg = pmt.cons(pmt.PMT_NIL, pmt.to_pmt(np.array(payload, dtype=np.uint8)))
        self.liquiddsp_flex_tx_0.to_basic_block()._post(pmt.intern("pdus"), msg)

