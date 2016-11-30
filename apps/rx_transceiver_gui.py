#!/usr/bin/python

from PyQt4 import Qt
from gnuradio import digital, gr, qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from math import pi
from optparse import OptionParser
import config
import PyQt4.Qwt5 as Qwt
import sip
import time

import rx_transceiver

from state_widget import state_widget

running = True

class pkt_receiver_rx_gui(rx_transceiver.pkt_receiver_rx, Qt.QWidget):
    def __init__(self):
        rx_transceiver.pkt_receiver_rx.__init__(self, rx_transceiver.rx_callback)
        Qt.QWidget.__init__(self)

        self._qt_init()

        # Variable that stores the current AWGN level in mV (0-15 mV)
        self.noise = noise = 0

        # constellation plot
        self.qtgui_const_sink = self._qt_make_constellation_sink()
        self.top_grid_layout.addLayout(self.qtgui_const_sink, 0, 1, 1, 1)

        # frequency sink
        self.qtgui_freq_sink = self._qt_make_frequency_sink()
        self.top_grid_layout.addLayout(self.qtgui_freq_sink, 1, 1, 3, 1)

        # Create an 8th order costas loop for fine frequnecy tuning
        self.costas_loop = digital.costas_loop_cc(2*pi/100, 8)

        # connect to post-timing debug port added to generic_demod
        self.connect(self.demodulator, self.costas_loop, self.qtgui_const_sink_plot)

        # connect the frequency sink to the output of the noise adder
        self.connect(self.noise_adder, self.qtgui_freq_sink_plot)

        # state widget
        self.state_widget = state_widget()
        self.state_widget.set_active_state(rx_transceiver.state)
        self.top_grid_layout.addWidget(self.state_widget, 0, 0, 1, 1)

        # noise knob
        self._qt_make_noise_knob()
        self.top_grid_layout.addLayout(self._noise_layout, 1, 0, 1, 1)

    def _qt_init(self):
        self.setWindowTitle("RX Transceiver")
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

        self.settings = Qt.QSettings("GNU Radio", "rx_transceiver_gui")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

    def _qt_make_constellation_sink(self):
        qtgui_const_sink_layout = Qt.QVBoxLayout()

        qtgui_const_sink_title = Qt.QLabel('Constellation Plot')
        qtgui_const_sink_title.setStyleSheet(config.QT_STYLESHEET_PLOT_TITLE)
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

    def _qt_make_frequency_sink(self):
        qtgui_freq_sink_layout = Qt.QVBoxLayout()

        qtgui_freq_sink_title = Qt.QLabel('Channel Spectrum')
        qtgui_freq_sink_title.setStyleSheet(config.QT_STYLESHEET_PLOT_TITLE)
        qtgui_freq_sink_title.setAlignment(Qt.Qt.AlignHCenter | Qt.Qt.AlignTop)

        self.qtgui_freq_sink_plot = qtgui.freq_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS,
            0, #fc
            config.FORWARD_SAMPLE_RATE,
            '', #name
            1 #number of inputs
        )

        self.qtgui_freq_sink_plot.set_update_time(0.10)
        self.qtgui_freq_sink_plot.set_y_axis(-140, 10)
        self.qtgui_freq_sink_plot.enable_autoscale(False)
        self.qtgui_freq_sink_plot.enable_grid(False)
        self.qtgui_freq_sink_plot.set_fft_average(1.0)
        qtgui_freq_sink_plot_widget = sip.wrapinstance(
            self.qtgui_freq_sink_plot.pyqwidget(), Qt.QWidget
        )

        qtgui_freq_sink_layout.addWidget(qtgui_freq_sink_title)
        qtgui_freq_sink_layout.addWidget(qtgui_freq_sink_plot_widget)

        return qtgui_freq_sink_layout


    def _qt_make_noise_knob(self):
        self._noise_layout = Qt.QVBoxLayout()
        self._noise_label = Qt.QLabel("Noise (mV)")
        self._noise_label.setAlignment(Qt.Qt.AlignTop | Qt.Qt.AlignHCenter)
        self._noise_label.setStyleSheet(config.QT_STYLESHEET_NOISE_TITLE)
        self._noise_layout.addWidget(self._noise_label)
        self._noise_knob = Qwt.QwtKnob()
        self._noise_knob.setRange(0, 15, 1)
        self._noise_knob.setValue(self.noise)
        self._noise_knob.setKnobWidth(100)
        self._noise_knob.valueChanged.connect(self.set_noise)
        self._noise_layout.addWidget(self._noise_knob)

    def closeEvent(self, event):
        global running

        self.settings = Qt.QSettings("GNU Radio", "rx_transceiver_gui")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

        running = False

    def get_noise(self):
        return self.noise

    def set_noise(self, noise):
        self.noise = noise
        Qt.QMetaObject.invokeMethod(self._noise_knob, "setValue", Qt.Q_ARG("double", self.noise))
        self.awgn_source.set_amplitude(self.noise/10000.0)
        # super(pkt_receiver_rx_gui, self).set_noise_floor()

    def reconfigure_rx(self, constellation=None):
        self.disconnect(self.demodulator, self.costas_loop)

        super(pkt_receiver_rx_gui, self).reconfigure_rx(constellation)

        self.connect(self.demodulator, self.costas_loop)

        # update state widget
        self.state_widget.set_active_state(constellation)

    def switch_costas_loop(self):
        self.lock()
        self.disconnect(self.demodulator, self.costas_loop)
        self.costas_loop = None
        self.costas_loop = digital.costas_loop_cc(2*pi/100, rx_transceiver.constel_points)
        self.connect(self.demodulator, self.costas_loop)
        self.unlock()

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui', 'style', 'raster'))
    qapp = Qt.QApplication(sys.argv)

    rx_transceiver.pr_tx = rx_transceiver.pkt_receiver_tx()
    rx_transceiver.pr_rx = pkt_receiver_rx_gui()

    print "Starting TX top block..."
    rx_transceiver.pr_tx.start()
    print "Starting RX top block..."
    rx_transceiver.pr_rx.start()

    rx_transceiver.pr_rx.show()
    # rx_transceiver.pr_rx.set_noise_floor()

    print "Entering main loop..."

    # rx_transceiver.pr_rx.set_noise_floor()

    print "Initial Noise Floor = %.2f" % rx_transceiver.pr_rx.noise_floor

    while running:
        qapp.processEvents()
        rx_transceiver.reconfigure_if_state_changed()
        # rx_transceiver.pr_tx.switch_costas_loop()
        time.sleep(0.001)

    print "Main loop exited."

    print "Stopping TX top block..."
    rx_transceiver.pr_tx.stop()
    print "Stopping RX top block..."
    rx_transceiver.pr_rx.stop()
    print "Waiting for TX top block to stop..."
    rx_transceiver.pr_tx.wait()
    print "TX top block stopped."
    print "Waiting for RX top block to stop..."
    rx_transceiver.pr_rx.wait()
    print "RX top block stopped."

    print "Cleaning up..."
    rx_transceiver.pr_tx = None
    rx_transceiver.pr_rx = None #to clean up Qt widgets
