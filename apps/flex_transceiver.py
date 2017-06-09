#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sat Jul 30 13:04:17 2016
##################################################

import numpy
import struct
import gnuradio.gr.gr_threading as _threading
import liquiddsp
from gnuradio import blocks
from gnuradio import gr


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
            while self.receive_queue.empty_p():
                pass
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
            if self.callback:
                self.callback(header_valid, payload_valid, mod_scheme, inner_code, outer_code, evm, header, payload)
        print "Watcher stopped"


class FlexTransceiver(gr.hier_block2):
    def __init__(self, samp_rate=200000):
        gr.hier_block2.__init__(self,
                              "Flex Transceiver",
                              gr.io_signature(1, 1, gr.sizeof_gr_complex),
                              gr.io_signature(1, 1, gr.sizeof_gr_complex))

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate

        ##################################################
        # Message Queues
        ##################################################
        self.transmit_queue = gr.msg_queue(100)
        self.receive_queue = gr.msg_queue(100)
        self.constellation_queue = gr.msg_queue(100)

        ##################################################
        # Blocks
        ##################################################
        self.liquiddsp_flex_rx_msgq_0 = liquiddsp.flex_rx_msgq(self.receive_queue, self.constellation_queue)
        self.liquiddsp_flex_tx_c_0 = liquiddsp.flex_tx_c(1, self.transmit_queue)
        self.blocks_message_source_0 = blocks.message_source(gr.sizeof_gr_complex*1, self.constellation_queue)

        self.watcher = QueueWatcherThread(self.receive_queue, self.callback)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.liquiddsp_flex_tx_c_0, 0), (self, 0))
        self.connect((self, 0), (self.liquiddsp_flex_rx_msgq_0, 0))

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
        self.liquiddsp_flex_tx_c_0.msgq().insert_tail(gr.message_from_string(bit_string))

    def callback(self, header_valid, payload_valid, mod_scheme, inner_code, outer_code, evm, header, payload):
        '''
        :param header_valid: 1 if CRC check passes, 0 otherwise
        :param payload_valid: 1 if CRC check passes, 0 otherwise
        :param evm: Error Vector Magnitude (similar to SNR)
        :param header: First four bytes are the packet number, 10 are assigned by user
        :param payload: Bitstring with payload
        :return:
        '''
        packet_num = struct.unpack("<L", header[:4]) # interprets first four bytes as long integer little endian
        if header_valid[0] and payload_valid[0]:
            print "Got packet {0}.".format(packet_num)

    def cleanup(self):
        print "Stopping Watcher"
        self.watcher.keep_running = False
        self.watcher.join()

