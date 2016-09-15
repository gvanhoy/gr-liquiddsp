#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sat Jul 30 13:04:17 2016
##################################################

import gnuradio.gr.gr_threading as _threading
import time
import struct
from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import channels
from gnuradio import gr
from gnuradio import qtgui
import liquiddsp
import numpy
import sip
from CE import *
from Database_Control import *
from Configuration_map import *
from Reset_databases import *


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
                time.sleep(0.01)
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
            if self.callback:
                self.callback(header_valid, payload_valid, mod_scheme, inner_code, outer_code, evm, header, payload)
        print "Watcher stopped"


class TopBlock(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 200000
        self.num_transmitted_payloads = 0
        self.num_received_payloads = 0
        self.transmitted_payloads = numpy.empty((1024, 1000))
        self.received_payloads = numpy.empty((1024, 1000))
        self.num_packets = 0

        ##################################################
        # Message Queues
        ##################################################
        self.transmit_queue = gr.msg_queue(100)
        self.receive_queue = gr.msg_queue(100)
        self.constellation_queue = gr.msg_queue(100)

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_const_sink_x_0 = self._qt_make_constellation_sink()
        self.top_grid_layout.addLayout(self.qtgui_const_sink_x_0, 0, 1, 1, 1)
        self.liquiddsp_flex_tx_c_0 = liquiddsp.flex_tx_c(1, self.transmit_queue)
        self.liquiddsp_flex_rx_c_0 = liquiddsp.flex_rx_c(self.receive_queue)
        self.liquiddsp_flex_rx_c_constel_0 = liquiddsp.flex_rx_c_constel(self.constellation_queue)
        self.blocks_message_source_0 = blocks.message_source(gr.sizeof_gr_complex*1, self.constellation_queue)

        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=0.0,
            frequency_offset=0.00000,
            epsilon=1.000001,
            taps=(1.0,),
            noise_seed=0,
            block_tags=False
        )
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex, self.samp_rate, True)
        self.watcher = QueueWatcherThread(self.receive_queue, self.callback)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.liquiddsp_flex_tx_c_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.liquiddsp_flex_rx_c_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.liquiddsp_flex_rx_c_constel_0, 0))
        self.connect((self.blocks_message_source_0, 0), (self.qtgui_const_sink_plot, 0))

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
        c1 = header_valid[0]
        c2 = payload_valid[0]
        c3 = packet_num[0]
        c4 = mod_scheme[0]
        c5 = inner_code[0]
        c6 = outer_code[0]
        print "============== RECEIVED =================="
        print "Header Valid", c1, "Payload valid", c2, "Mod Scheme", c4, \
            "Inner Code", c5, "Outer Code", c6, "EVM", evm, "Packet Num", c3
        ID = c4*8+c6+1
        configuration = make_Conf(ID, c4, c5, c6)
        config11 = Conf_map(c4, c5, c6)
        if c1 > 0:
            packet_success_rate = float(c2)/float(c1)
        else:
            packet_success_rate = 0

        goodput = packet_success_rate * self.samp_rate * math.log(config11.constellationN, 2) * (float(config11.outercodingrate)) * (float(config11.innercodingrate))
        print "goodput is ", goodput
        WRITE_Conf(configuration, c1, c2, goodput)
        self.num_packets += 1
        print "Packets received number: ", self.num_packets

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()
        self.watcher.keep_running = False
        self.watcher.join()

    def cleanup(self):
        print "Stopping Watcher"
        self.watcher.keep_running = False
        self.watcher.join()

    def _qt_make_constellation_sink(self):
        qtgui_const_sink_layout = Qt.QVBoxLayout()

        qtgui_const_sink_title = Qt.QLabel('Constellation Plot')
        qtgui_const_sink_title.setAlignment(Qt.Qt.AlignHCenter | Qt.Qt.AlignTop)

        # Allow access to this plot for connections
        self.qtgui_const_sink_plot = qtgui.const_sink_c(1024, '', 1)
        self.qtgui_const_sink_plot.set_update_time(0.10)
        self.qtgui_const_sink_plot.set_y_axis(-3, 3)
        self.qtgui_const_sink_plot.set_x_axis(-3, 3)
        self.qtgui_const_sink_plot.enable_autoscale(False)
        qtgui_const_sink_plot_widget = sip.wrapinstance(
            self.qtgui_const_sink_plot.pyqwidget(), Qt.QWidget
        )
        qtgui_const_sink_layout.addWidget(qtgui_const_sink_title)
        qtgui_const_sink_layout.addWidget(qtgui_const_sink_plot_widget)

        return qtgui_const_sink_layout


def main(top_block_cls=TopBlock, options=None):
    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()
    inner_code = 0
    outer_code = 0
    modulation = 0

    def quitting():
        tb.watcher.keep_running = False
        tb.stop()
        tb.wait()

    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    RESET_Tables(tb.samp_rate)
    num_packets = 0
    while num_packets < 11 * 8 * 2:
        qapp.processEvents()
        for m in range(11):
            for o in range(8):
                random_bits = numpy.random.randint(255, size=(2000,))
                if not tb.liquiddsp_flex_rx_c_0.msgq().full_p():
                    tb.send_packet(m, 0, o, range(9), random_bits)
                    num_packets += 1

    while True:
        qapp.processEvents()
        if tb.liquiddsp_flex_rx_c_0.msgq().full_p():
            print "queue full"

        if (num_packets % 20) == 0:
            print "CE Decision is "
            epsilon = 0.01
            bandwidth = tb.samp_rate
            ce_configuration = EGreedy(num_packets, epsilon, bandwidth)
            random_bits = numpy.random.randint(255, size=(2000,))
            if ce_configuration is not None:
                new_ce_configuration = ce_configuration[0]
                modulation = new_ce_configuration.modulation
                inner_code = new_ce_configuration.innercode
                outer_code = new_ce_configuration.outercode
                Conf_map(modulation, inner_code, outer_code)  # prints configuration
        if not tb.liquiddsp_flex_rx_c_0.msgq().full_p():
            tb.send_packet(modulation, inner_code, outer_code, range(9), random_bits)
            num_packets += 1


    time.sleep(5)
    tb.watcher.keep_running = False
    tb.stop()
    tb.wait()

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    try:
        main()
    except KeyboardInterrupt:
        pass
