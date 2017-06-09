import numpy
from gnuradio import gr
from gnuradio import blocks
from flex_transceiver import FlexTransceiver


class SimpleTxRx(gr.top_block):
    def __init__(self, samp_rate=200000, num_packets_to_send=1000):
        gr.top_block.__init__(self, name="Simple Flex Tx Rx")
        self.num_packets_to_send = num_packets_to_send
        self.transmitter = FlexTransceiver(samp_rate=samp_rate)
        self.receiver = FlexTransceiver(samp_rate=samp_rate)
        self.throttle = blocks.throttle(gr.sizeof_gr_complex * 1, samp_rate, True)
        self.connect(self.transmitter, self.throttle, self.receiver)

    def simulate(self):
        for x in range(self.num_packets_to_send):
            random_bits = numpy.random.randint(255, size=(1000,))
            self.transmitter.send_packet(0, 0, 0, range(10), random_bits)
        while not self.receiver.liquiddsp_flex_rx_msgq_0.bit_msgq().empty_p():
            pass

if __name__ == '__main__':
    simple_tx_rx = SimpleTxRx()
    simple_tx_rx.simulate()

