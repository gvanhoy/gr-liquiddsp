#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sat Jul 30 13:04:17 2016
##################################################

from gnuradio import blocks
from gnuradio import uhd
from gnuradio.filter import pfb
from gnuradio.filter import freq_xlating_fir_filter_ccc
import gnuradio.gr.gr_threading as _threading
from gnuradio.ctrlport.monitor import *
import liquiddsp
import numpy
import time
import struct


class QueueWatcherThread(_threading.Thread):
    def __init__(self, receive_queue, callback):
        _threading.Thread.__init__(self)
        self.receive_queue = receive_queue
        self.callback = callback
        self.keep_running = True
        self.start()

    def run(self):
        print("Watcher started")
        while self.keep_running:
            if self.receive_queue.empty_p():
                time.sleep(0.0001)
                continue
            msg = self.receive_queue.delete_head_nowait()
            if msg.__deref__() is None or msg.length() <= 0:
                if msg.length() <= 0:
                    print("Message length is 0")
                continue
            message = msg.to_string()
            header_valid = struct.unpack("<B", message[0])
            payload_valid = struct.unpack("<B", message[1])
            evm = struct.unpack("f", message[2:6])[0]
            header = message[6:21]
            payload = message[21:]
            # print("Received Header ", header_num)
            # print("Length ", msg.length() - 4, " Received Payload ", payload, )
            if self.callback:
                self.callback(header_valid, payload_valid, evm, header, payload)
        print("Watcher stopped")


class TopBlock(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2000000
        self.num_transmitted_payloads = 0
        self.num_received_payloads = 0
        self.transmitted_payloads = numpy.empty((1024, 1000))
        self.received_payloads = numpy.empty((1024, 1000))

        ##################################################
        # Message Queues
        ##################################################
        self.transmit_queue = gr.msg_queue(100)
        self.receive_queue = gr.msg_queue(4)

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_sink_0_0 = uhd.usrp_sink(
            ",".join(("addr=192.168.10.3", "")),
            uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )
        self.uhd_usrp_sink_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0_0.set_center_freq(915000000, 0)
        self.uhd_usrp_sink_0_0.set_gain(40, 0)

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("addr=192.168.10.2", "")),
            uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(915000000, 0)
        self.uhd_usrp_source_0.set_gain(20, 0)

        self.blocks_ctrlport_probe_c_0 = blocks.ctrlport_probe_c("Transmit Constellation", "Constellation Points")
        self.blocks_ctrlport_probe_c_1 = blocks.ctrlport_probe_c("Receive Signal", "Receive PSD")
        self.blocks_ctrlport_monitor_0 = not True or monitor()
        self.pfb_arb_resampler_xxx_0 = \
            pfb.arb_resampler_ccf(
                .5,
                taps=([1.4439507757030589e-19, 0.004252371843904257, -4.071401172959478e-18, -0.046280305832624435, 1.3662913581633394e-17, 0.29189109802246094, 0.5002737045288086, 0.29189109802246094, 1.3662913581633394e-17, -0.046280305832624435, -4.071401172959478e-18, 0.004252371843904257, 1.4439507757030589e-19]),
                flt_size=16)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)

        self.pfb_interpolator_ccf_0 = pfb.interpolator_ccf(
            10,
            (),
            100)
        self.pfb_interpolator_ccf_0.declare_sample_delay(0)

        self.freq_xlating_fir_filter_xxx_0 = \
            freq_xlating_fir_filter_ccc(
                10,
                ([0.0005655840504914522, 0.0005578328855335712, 0.0005056450027041137, 0.00040094327414408326, 0.00023455471091438085, -4.1977167189775776e-19, -0.00030191324185580015, -0.0006586489616893232, -0.001042728079482913, -0.0014107513707131147, -0.0017054135678336024, -0.0018608389655128121, -0.0018110291566699743, -0.0015006389003247023, -0.0008967587491497397, 1.207792261782818e-18, 0.0011470154859125614, 0.002455565147101879, 0.0037925848737359047, 0.004989100620150566, 0.005855345632880926, 0.0062016393058001995, 0.0058632199652493, 0.004726421553641558, 0.0027530966326594353, -2.4151097218940305e-18, -0.003369914833456278, -0.007086704485118389, -0.010784572921693325, -0.014025082811713219, -0.01633123867213726, -0.017229827120900154, -0.01629827357828617, -0.013211451470851898, -0.007783515378832817, 3.476806791453805e-18, 0.00996379368007183, 0.021740974858403206, 0.03478900343179703, 0.048422858119010925, 0.06186307221651077, 0.07429459691047668, 0.08493141829967499, 0.09308073669672012, 0.09820082038640976, 0.09994695335626602, 0.09820082038640976, 0.09308073669672012, 0.08493141829967499, 0.07429459691047668, 0.06186307221651077, 0.048422858119010925, 0.03478900343179703, 0.021740974858403206, 0.00996379368007183, 3.476806791453805e-18, -0.007783515378832817, -0.013211451470851898, -0.01629827357828617, -0.017229827120900154, -0.01633123867213726, -0.014025082811713219, -0.010784572921693325, -0.007086704485118389, -0.003369914833456278, -2.4151097218940305e-18, 0.0027530966326594353, 0.004726421553641558, 0.0058632199652493, 0.0062016393058001995, 0.005855345632880926, 0.004989100620150566, 0.0037925848737359047, 0.002455565147101879, 0.0011470154859125614, 1.207792261782818e-18, -0.0008967587491497397, -0.0015006389003247023, -0.0018110291566699743, -0.0018608389655128121, -0.0017054135678336024, -0.0014107513707131147, -0.001042728079482913, -0.0006586489616893232, -0.00030191324185580015, -4.1977167189775776e-19, 0.00023455471091438085, 0.00040094327414408326, 0.0005056450027041137, 0.0005578328855335712, 0.0005655840504914522]),
                0,
                samp_rate
            )

        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((.25, ))

        self.liquiddsp_flex_tx_c_0 = liquiddsp.flex_tx_c(1, self.transmit_queue)
        self.liquiddsp_flex_rx_c_0 = liquiddsp.flex_rx_c(self.receive_queue)

        self.watcher = QueueWatcherThread(self.receive_queue, self.callback)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.liquiddsp_flex_tx_c_0, 0), (self.pfb_interpolator_ccf_0, 0))
        self.connect((self.liquiddsp_flex_tx_c_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.pfb_interpolator_ccf_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.uhd_usrp_sink_0_0, 0))
        # self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.blocks_ctrlport_probe_c_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        # self.connect((self.uhd_usrp_source_0, 0), (self.blocks_ctrlport_probe_c_1, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.liquiddsp_flex_rx_c_0, 0))
        # self.connect((self.liquiddsp_flex_tx_bc_0, 0), (self.liquiddsp_flex_rx_c_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def send_packet(self, modulation, inner_code, outer_code, header, payload):
        '''
        :param modulation: integer from 0 to 10
        :param inner_code: integer from 0 to 6
        :param outer_code: integer from 0 to 7
        :param header: list of 10 bytes
        :param payload: list of bytes (length arbitrary)
        :return:
        '''
        packet = []
        packet.append(modulation)
        packet.append(inner_code)
        packet.append(outer_code)
        packet.extend(header)
        packet.extend(payload)
        bit_string = numpy.array(packet).astype(numpy.uint8).tostring()
        #TODO: Not sure if this helps at all...
        while self.liquiddsp_flex_tx_c_0.msgq().full_p():
            pass
        self.liquiddsp_flex_tx_c_0.msgq().insert_tail(gr.message_from_string(bit_string))

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)

    def callback(self, header_valid, payload_valid, evm, header, payload):
        '''
        :param header_valid: 1 if CRC check passes, 0 otherwise
        :param payload_valid: 1 if CRC check passes, 0 otherwise
        :param evm: Error Vector Magnitude (similar to SNR)
        :param header: First four bytes are the packet number, 10 are assigned by user
        :param payload: Bitstring with payload
        :return:
        '''
        #TODO: How to parse header and payload as bitstrings
        packet_num = struct.unpack("<L", header[:4])
        print "Header Valid", header_valid, "Payload valid", payload_valid, "EVM ", evm, "Packet Num", packet_num

        # if header_num <= 100 and header_num > 0:
            # for index in range(len(payload)):
                # self.received_payloads[index, header_num] = struct.unpack('B', payload[index])[0]
            # ber = numpy.sum(numpy.bitwise_xor(numpy.uint8(self.received_payloads[:, 1:]),
            #                                   numpy.uint8(self.transmitted_payloads[:, 1:])))
            # self.num_received_payloads += 1

    def cleanup(self):
        print "Stopping Watcher"
        self._watcher.keep_running = False
        self._watcher.join()


def main(top_block_cls=TopBlock, options=None):

    tb = top_block_cls()
    tb.start()
    # (tb.blocks_ctrlport_monitor_0).start()
    while True:
        for m in range(10):
            for i in range(6):
                for o in range(7):
                    random_bits = numpy.random.randint(2, size=(1000,))
                    tb.send_packet(m, i, o, range(9), random_bits)
    time.sleep(5)
    tb.watcher.keep_running = False
    tb.stop()
    # (tb.blocks_ctrlport_monitor_0).stop()
    tb.wait()


if __name__ == '__main__':
    main()




