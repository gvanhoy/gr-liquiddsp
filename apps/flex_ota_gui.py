from PyQt4 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import PyQt4.Qwt5 as Qwt
import sip
from apps.flex_ota import *
from Database_Control import *
from Reset_databases import *
import sys

NUM_THROUGHPUT_SAMPLES = 250


class ThroughputPlot(Qwt.QwtPlot):
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

        self.data_burst_no = np.zeros(NUM_THROUGHPUT_SAMPLES, dtype=float)
        self.data_good_acks = np.zeros(NUM_THROUGHPUT_SAMPLES, dtype=float)
        self.data_bad_acks = np.zeros(NUM_THROUGHPUT_SAMPLES, dtype=float)

        # self.setMinimumSize(800, 600)

        self.setCanvasBackground(Qt.Qt.white)
        self._alignScales()

        self.setTitle("")
        self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.RightLegend)

        self.curve_good_acks = Qwt.QwtPlotCurve("Throughput")
        self.curve_good_acks.attach(self)
        self.curve_good_acks.setPen(Qt.QPen(Qt.Qt.blue, 4, Qt.Qt.SolidLine, Qt.Qt.SquareCap, Qt.Qt.RoundJoin))
        self.curve_good_acks.setData(self.data_burst_no, self.data_good_acks)
        self.curve_good_acks.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)

        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Burst No.")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Data Throughput (kbps)")
        # self.setAxisScale(Qwt.QwtPlot.xBottom, 0, 100, 25)
        self.setAxisScale(Qwt.QwtPlot.yLeft, 0, 400, 100)
        # self.setAxisAutoScale(False)



    def _alignScales(self):
        self.canvas().setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Plain)
        self.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = self.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = self.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)

    def add_data_point(self, burst_no, good_acks):
        self.data_burst_no = np.concatenate((self.data_burst_no[1:],
                                             self.data_burst_no[:1]), 1)
        self.data_burst_no[-1] = burst_no

        self.data_good_acks = np.concatenate((self.data_good_acks[1:],
                                              self.data_good_acks[:1]), 1)
        self.data_good_acks[-1] = good_acks
        self.curve_good_acks.setData(self.data_burst_no, self.data_good_acks)

        self.replot()

    def add_marker(self, burst_num, throughput, text):
        m = Qwt.QwtPlotMarker()
        m.setValue(burst_num, throughput)
        m.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        m.setLinePen(Qt.QPen(Qt.Qt.red, 2, Qt.Qt.DashDotLine))
        text = Qwt.QwtText(text)
        text.setColor(Qt.Qt.red)
        text.setBackgroundBrush(Qt.QBrush(self.canvasBackground()))
        text.setFont(Qt.QFont(self.fontInfo().family(), 12, Qt.QFont.Bold))

        m.setLabel(text)
        m.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Diamond,
                                  Qt.QBrush(Qt.Qt.red),
                                  Qt.QPen(Qt.Qt.red),
                                  Qt.QSize(10, 10)))

        m.attach(self)


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
        self.top_grid_layout.addLayout(self.qtgui_const_sink, 1, 1, 1, 1)

        # # frequency sink
        self.qtgui_rx_const_sink = self._qt_make_rx_constellation_sink()
        self.top_grid_layout.addLayout(self.qtgui_rx_const_sink, 1, 0, 1, 1)

        # Create a Vertical Box layout in Qt, and add a large title in lieu of the
        # small automatically added via the Qwt plot.
        self.throughput_plot = ThroughputPlot()
        self.throughput_plot_layout = self._qt_make_throughput_plot(self.throughput_plot)
        self.top_grid_layout.addLayout(self.throughput_plot_layout, 0, 0, 1, 1)

        self.connect(self.blocks_message_source_0, self.qtgui_const_sink_plot)
        self.connect(self.channels_channel_model_0, self.qtgui_rx_const_sink_plot)

        self.information_window = self._qt_make_information_window()
        self.top_grid_layout.addLayout(self.information_window, 0, 1, 1, 1)

        # noise knob
        # self._qt_make_noise_knob()
        # self.top_grid_layout.addLayout(self._noise_layout, 1, 0, 1, 1)

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

    def _qt_make_rx_constellation_sink(self):
        qtgui_const_sink_layout = Qt.QVBoxLayout()

        qtgui_const_sink_title = Qt.QLabel('Constellation Plot')
        qtgui_const_sink_title.setAlignment(Qt.Qt.AlignHCenter | Qt.Qt.AlignTop)

        # Allow access to this plot for connections
        self.qtgui_rx_const_sink_plot = qtgui.const_sink_c(1024, '', 1)
        self.qtgui_rx_const_sink_plot.set_update_time(0.10)
        self.qtgui_rx_const_sink_plot.set_y_axis(-3, 3)
        self.qtgui_rx_const_sink_plot.set_x_axis(-3, 3)
        self.qtgui_rx_const_sink_plot.enable_autoscale(False)
        qtgui_const_sink_plot_widget = sip.wrapinstance(
            self.qtgui_rx_const_sink_plot.pyqwidget(), Qt.QWidget
        )

        qtgui_const_sink_layout.addWidget(qtgui_const_sink_title)
        qtgui_const_sink_layout.addWidget(qtgui_const_sink_plot_widget)

        return qtgui_const_sink_layout


    def _qt_make_information_window(self):
        information_layout = Qt.QGridLayout()

        # Allow these to be accessed later
        self.throughput_slot = Qt.QLabel('Current Throughput: 0.00 kbps')
        self.time_taken_slot = Qt.QLabel('Last Burst Time: 0 ms')
        self.coding_label_slot = Qt.QLabel('Coding: None')

        information_layout.addWidget(self.throughput_slot, 0, 0, 1, 1)
        information_layout.addWidget(self.time_taken_slot, 1, 0, 1, 1)
        information_layout.addWidget(self.coding_label_slot, 2, 0, 1, 1)

        return information_layout

    def set_current_throughput(self, throughput):
        self.throughput_slot.setText(('Current Throughput: %d kbps' % throughput))

    def set_time_taken(self, time):
        self.time_taken_slot.setText(('Last Burst Time: %d ms' % time))

    def set_coding(self, coding):
        self.coding_label_slot.setText(('Coding: %s' % coding))

    def _qt_make_throughput_plot(self, throughput_plot):
        throughput_plot_layout = Qt.QVBoxLayout()
        throughput_plot_title = Qt.QLabel('Round Trip Packet Throughput')
        throughput_plot_title.setAlignment(Qt.Qt.AlignHCenter | Qt.Qt.AlignTop)
        throughput_plot_layout.addWidget(throughput_plot_title)
        throughput_plot_layout.addWidget(throughput_plot)

        return throughput_plot_layout

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
        # self.channels_channel_model_0.set_noise_voltage(self.noise)

    def process_queue(self):
        while not self.packet_info_queue.empty():
            packet_info = self.packet_info_queue.get()
            self.database.write_configuration(packet_info['config'],
                                              packet_info['header_valid'],
                                              packet_info['payload_valid'],
                                              packet_info['goodput'])

if __name__ == '__main__':
    from distutils.version import StrictVersion

    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    top_block = TopBlockGui()
    top_block.start()
    top_block.show()
    inner_code = 0
    outer_code = 0
    modulation = 0

    def quitting():
        top_block.watcher.keep_running = False
        top_block.stop()
        top_block.wait()

    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    RESET_Tables(top_block.samp_rate)
    num_packets = 0
    while num_packets < 11 * 8 * 4:
        qapp.processEvents()
        for m in range(11):
            for o in range(8):
                random_bits = numpy.random.randint(255, size=(1024,))
                while top_block.liquiddsp_flex_tx_c_0.msgq().full_p():
                    qapp.processEvents()
                    pass
                top_block.send_packet(m, 0, o, range(9), random_bits)
                num_packets += 1

    while True:
        qapp.processEvents()
        top_block.process_queue()
        top_block.throughput_plot.add_data_point(top_block.burst_number - 249, numpy.mean(top_block.packet_history)/1000.0)
        if (num_packets % 50) == 0:
            ce_configuration = EGreedy(num_packets, .01, top_block.samp_rate/2) # using half total bandwidth
            random_bits = numpy.random.randint(255, size=(1024,))
            if ce_configuration is not None:
                new_ce_configuration = ce_configuration[0]
                modulation = new_ce_configuration.modulation
                inner_code = new_ce_configuration.innercode
                outer_code = new_ce_configuration.outercode
                map = Conf_map(modulation, inner_code, outer_code)  # prints configuration
                top_block.throughput_plot.add_marker(top_block.burst_number - 249,
                                                     numpy.mean(top_block.packet_history) / 1000.0,
                                                     map.modulationtype +
                                                     str(map.innercodingrate *
                                                         map.outercodingrate))
        while top_block.liquiddsp_flex_tx_c_0.msgq().full_p():
            qapp.processEvents()
            top_block.process_queue()
            pass
        top_block.send_packet(modulation, inner_code, outer_code, range(9), random_bits)
        num_packets += 1

    print "Stopping top block..."
    top_block.stop()
    top_block.wait()
    print "RX top block stopped."