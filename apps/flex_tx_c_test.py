#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sun Jul 31 04:13:13 2016
##################################################
from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.filter import firdes
import liquiddsp
import sip
import numpy
import time


if __name__ == '__main__':
    import ctypes
    import sys

    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"


class top_block(gr.top_block, Qt.QWidget):
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

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024,  # fftsize
            firdes.WIN_BLACKMAN_hARRIS,  # wintype
            0,  # fc
            samp_rate,  # bw
            "",  # name
            True,  # plotfreq
            True,  # plotwaterfall
            True,  # plottime
            True,  # plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0 / 10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_sink_x_0_win)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex * 1, samp_rate, True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.liquiddsp_flex_tx_c_0, 0), (self.blocks_throttle_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

    def insert_message(self, msg):
        self.liquiddsp_flex_tx_c_0.msgq().insert_tail(gr.message_from_string(msg))

    def insert_packets(self, mod, inner, outer):
        num_packets = 0
        while num_packets < 100:
            random_bits = numpy.random.randint(0x10000, size=(1024,))
            random_bits[0] = mod
            random_bits[1] = inner
            random_bits[2] = outer
            bit_string = random_bits.astype(numpy.uint8).tostring()
            self.insert_message(bit_string)
            num_packets += 1


def main(top_block_cls=top_block, options=None):
    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()

    for m in range(0, 10):
        for i in range(0, 6):
            for o in range(0, 7):
                tb.insert_packets(m, i, o)
                time.sleep(5)

    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
