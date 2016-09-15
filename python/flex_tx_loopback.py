#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sat Jul 30 13:04:17 2016
##################################################

from gnuradio import blocks
from gnuradio import channels
from gnuradio import gr
import gnuradio.gr.gr_threading as _threading
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
                time.sleep(0.001)
                continue
            msg = self.receive_queue.delete_head_nowait()
            if msg.__deref__() is None or msg.length() <= 0:
                if msg.length() <= 0:
                    print("Message length is 0")
                continue
            message = msg.to_string()
            header_valid = struct.unpack("<B", message[0])
            payload_valid = struct.unpack("<B", message[1])
            mod_scheme = struct.unpack("<B", message[2])
            inner_code = struct.unpack("<B", message[3])
            outer_code = struct.unpack("<B", message[4])
            evm = struct.unpack("f", message[5:9])[0]
            header = message[9:24]
            payload = message[24:]
            print "test"
            # print("Received Header ", header_num)
            # print("Length ", msg.length() - 4, " Received Payload ", payload, )
            if self.callback:
                self.callback(header_valid, payload_valid, mod_scheme, inner_code, outer_code, evm, header, payload)
        print("Watcher stopped")


class TopBlock(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 200000
        self.num_transmitted_payloads = 0
        self.num_received_payloads = 0
        self.transmitted_payloads = numpy.empty((1024, 1000))
        self.received_payloads = numpy.empty((1024, 1000))

        ##################################################
        # Message Queues
        ##################################################
        self.transmit_queue = gr.msg_queue()
        self.receive_queue = gr.msg_queue()

        ##################################################
        # Blocks
        ##################################################
        self.liquiddsp_flex_tx_c_0 = liquiddsp.flex_tx_c(1, self.transmit_queue)
        self.liquiddsp_flex_rx_c_0 = liquiddsp.flex_rx_c(self.receive_queue)

        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=0.1,
            frequency_offset=0.00000,
            epsilon=1.000000,
            taps=(1.0,),
            noise_seed=0,
            block_tags=False
        )
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex, samp_rate, True)
        self.watcher = QueueWatcherThread(self.receive_queue, self.callback)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.liquiddsp_flex_tx_c_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.liquiddsp_flex_rx_c_0, 0))
        # self.connect((self.blocks_throttle_0, 0), (self.liquiddsp_flex_rx_c_0, 0))

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
        # TODO: Not sure if this helps at all...
        while self.liquiddsp_flex_tx_c_0.msgq().full_p():
            pass
        self.liquiddsp_flex_tx_c_0.msgq().insert_tail(gr.message_from_string(bit_string))

    def insert_message(self, msg):
        for index in range(len(msg) - 3):
            self.transmitted_payloads[index, self.num_transmitted_payloads] = struct.unpack('B', msg[index + 3])[0]
        self.liquiddsp_flex_tx_c_0.msgq().insert_tail(gr.message_from_string(msg))
        self.num_transmitted_payloads += 1

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def callback(self, header_valid, payload_valid, mod_scheme, inner_code, outer_code, evm, header, payload):
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
        print "Header Valid", header_valid, "Payload valid", payload_valid, "Mod Scheme", mod_scheme, \
            "Inner Code", inner_code, "Outer Code", outer_code, "EVM", evm, "Packet Num", packet_num

    def cleanup(self):
        print "Stopping Watcher"
        self._watcher.keep_running = False
        self._watcher.join()


def main(top_block_cls=TopBlock, options=None):
    tb = top_block_cls()
    tb.start()
    num_packets = 0
    while True:
        if (tb.num_packets % 20) == 0:
            print "CE Decision is "
            epsilon = 0.01
            BW = tb.samp_rate
            Conf = EGreedy(num_packets, epsilon, BW)
            new_Conf = Conf[0]
            m = new_Conf.modulation
            i = new_Conf.innercode
            o = new_Conf.outercode
            config_map = Conf_map(m, i, o)
        tb.send_packet(m, i, o, range(9), random_bits)
    time.sleep(5)
    print "Transmission is done **********************************"
    print "Transmission is done **********************************"
    tb.watcher.keep_running = False
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()



