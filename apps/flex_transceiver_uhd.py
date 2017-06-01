import flex_transceiver


class FlexTranceiverUHD(flex_transceiver):
    def __init__(self, samp_rate, center_frequency, tx_ip_addr, rx_ip_addr, tx_gain_db, rx_gain_db):
        flex_transceiver.__init__(samp_rate)

        ##################################################
        # Variables
        ##################################################
        self.center_frequency = center_frequency
        self.tx_ip_addr = tx_ip_addr
        self.tx_gain_db = tx_gain_db
        self.rx_ip_addr = rx_ip_addr
        self.rx_gain_db = rx_gain_db

        ##################################################
        # Blocks
        ##################################################
        self.transmitter_uhd = uhd.usrp_sink(
            ",".join(("addr=" + self.tx_ip_addr, "")),
            uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )
        self.transmitter_uhd.set_samp_rate(samp_rate)
        self.transmitter_uhd.set_center_freq(center_frequency, 0)
        self.transmitter_uhd.set_gain(self.tx_gain_db, 0)

        self.receiver_uhd = uhd.usrp_source(
            ",".join(("addr=" + self.rx_ip_addr, "")),
            uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )
        self.receiver_uhd.set_samp_rate(samp_rate)
        self.receiver_uhd.set_center_freq(center_frequency, 0)
        self.receiver_uhd.set_gain(self.rx_gain_db, 0)

        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((.25, ))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.liquiddsp_flex_tx_c_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.transmitter_uhd, 0))
        self.connect((self.receiver_uhd, 0), (self.liquiddsp_flex_rx_msgq_0, 0))

