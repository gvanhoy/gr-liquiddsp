from PyQt4 import Qt
from gnuradio import digital, gr, qtgui
from gnuradio.filter import firdes
import PyQt4.Qwt5 as Qwt
import sip
from apps.flex_ota import *


class TopBlockGui(FlexOTA, Qt.QWidget):
    def __init__(self):
        Qt.QWidget.__init__(self)
        FlexOTA.__init__(self)

        gr.enable_realtime_scheduling()

        self._qt_init()

        # Variable that stores the current AWGN level in mV (0-15 mV)
        self.noise = noise = 0

        # constellation plot
        self.qtgui_const_sink = self._qt_make_constellation_sink()
        self.top_grid_layout.addLayout(self.qtgui_const_sink, 0, 1, 1, 1)

        # frequency sink
        self.qtgui_freq_sink = self._qt_make_frequency_sink()
        self.top_grid_layout.addLayout(self.qtgui_freq_sink, 1, 1, 3, 1)

        self.connect(self.blocks_message_source_0, self.qtgui_const_sink_plot)
        self.connect(self.blocks_message_source_0, self.qtgui_freq_sink_plot)

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

        self.settings = Qt.QSettings("GNU Radio", "flex_ota_gui")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

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

    def _qt_make_frequency_sink(self):
        qtgui_freq_sink_layout = Qt.QVBoxLayout()

        qtgui_freq_sink_title = Qt.QLabel('Channel Spectrum')
        qtgui_freq_sink_title.setAlignment(Qt.Qt.AlignHCenter | Qt.Qt.AlignTop)

        self.qtgui_freq_sink_plot = qtgui.freq_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS,
            0, #fc
            self.samp_rate,
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
        self._noise_layout.addWidget(self._noise_label)
        self._noise_knob = Qwt.QwtKnob()
        self._noise_knob.setRange(0, 15, 1)
        self._noise_knob.setValue(self.noise)
        self._noise_knob.setKnobWidth(100)
        self._noise_knob.valueChanged.connect(self.set_noise)
        self._noise_layout.addWidget(self._noise_knob)

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "rx_transceiver_gui")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()
        self.watcher.keep_running = False
        self.watcher.join()

    def get_noise(self):
        return self.noise

    def set_noise(self, noise):
        self.noise = noise
        Qt.QMetaObject.invokeMethod(self._noise_knob, "setValue", Qt.Q_ARG("double", self.noise))
        #self.awgn_source.set_amplitude(self.noise/10000.0)
        self.channels_channel_model_0.set_noise_voltage(self.noise)

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    #parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    #(options, args) = parser.parse_args()
    Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui', 'style', 'raster'))
    qapp = Qt.QApplication(sys.argv)

    top_block = TopBlockGui()
    top_block.start()
    top_block.show()

    num_packets = 0

    print "Top block started."
    while True:
        qapp.processEvents()
        # rx_transceiver.pr_tx.switch_costas_loop()
        for m in range(11):
            for o in range(8):
                random_bits = numpy.random.randint(255, size=(2000,))
                if not top_block.liquiddsp_flex_tx_c_0.msgq().full_p():
                    top_block.send_packet(m, 0, o, range(9), random_bits)
                    num_packets += 1
        time.sleep(0.1)

    print "Stopping top block..."
    top_block.stop()
    top_block.wait()
    print "RX top block stopped."