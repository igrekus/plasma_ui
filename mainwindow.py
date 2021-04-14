import os
import serial
from PyQt6 import uic
from PyQt6.QtCore import QTimer, QTime, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow
# from easymodbus.run import modbusClient
from easymodbus.modbusClient import ModbusClient as modbusClient

from Recipe import Recipe
from Settings import Settings
from Valve import GasValve
from Valve import Valve


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._ui = uic.loadUi("mainwindow.ui", self)

        # - private void MainForm_Load(object sender, EventArgs e)
        self.recipe = Recipe()  # -   recipies
        self.settings = Settings()  # -   settings
        # self.settings.initialize()

        self.gas_out_valve = Valve(self.settings.gas_out_valve, False, QPixmap)
        self.ar_valve = GasValve(self.settings.ar_valve, False, 0, self.settings.ar_mfc, self.settings.ar_sccm, QPixmap)
        self.o2_valve = GasValve(self.settings.o2_valve, False, 0, self.settings.o2_mfc, self.settings.o2_sccm,
                                 QPixmap())
        self.cf4_valve = GasValve(self.settings.cf4_valve, False, 0, self.settings.cf4_mfc, self.settings.cf4_sccm,
                                  QPixmap())
        self.n2_valve = GasValve(self.settings.n2_valve, False, 0, self.settings.n2_mfc, self.settings.n2_sccm,
                                 QPixmap())
        self.vent_valve = Valve(self.settings.vent_valve, False, QPixmap())
        self.pump_valve = Valve(self.settings.pump_valve, False, QPixmap())

        # -  public partial class MainForm : Form
        self.modbusClient = modbusClient(self.settings.plc_ip_adress, self.settings.plc_port)  # -   plc connecting
        self.valve_port = serial.Serial(self.settings.comport_name)  # -   com port variable
        self.recipe_part = os.path.abspath('./recipies')
        self.throttle_valve_angle = 0.0
        self.timer_pump_for_vent = QTimer()  # -  pre_vent timer

        # -  private static Valve VentValve;
        self.timer_send_receive_modbus = QTimer()  # -   plc call timer
        self.timer_check_trhrottle = QTimer()
        self.timer_pressure_read = QTimer()  # - pressure call timer
        self.timer_for_vent = QTimer()  # - vent timer
        self.timer_process = QTimer()  # -   process timer
        self.timer_ignition = QTimer()  # -   ignition process timer

        # - private static string SerialMessage
        self.pressure_read = 0.0  # -   baratron pressure
        self.pressure_angle = False  # -   pressure and status of the drosel valve's call
        self.process_time = QTimer()  # -   process time
        self.process_time_start = QTimer()  # -   starting process time
        self.process_time_end = QTimer()  # -   ending process time
        self.last_time = QTime()  # process remain time
        self.proccess_started = False  # process status
        self.pre_pump_process_started = False  # pre pump process status
        self.pressure_input = 0.0  # reading value from the recipe
        self.throttle_valve = False  # throttle valve variable
        self.pump_for_vent = False  # venting
        self.lid_up_button = False
        self.lid_down_button = False
        self.vent_button = False
        self.pump_button = False
        self.ignition_start = False
        self.start_button = False
        self.stop_button = False
        self.safe_button = False
        self.lid_down_bit = False  # lid's bit status
        self.process_end = False
        self.venting = False
        self.lid_closing = False
        self.mfc_read = []
        self.ar_mfc_read = []
        self.o2_mfc_read = []
        self.cf4_mfc_read = []
        self.n2_mfc_read = []
        self.sccm_ar = 0
        self.sccm_o2 = 0
        self.sccm_cf4 = 0
        self.sccm_n2 = 0
        self.mw_power = 0
        self.generator_hb = []

        self.read_recipes_from_folder()

    def read_recipes_from_folder(self):  # reading recipes from the folder
        path = "recipes"

        dir_list = os.listdir(path)
        rcp_list = []

        if dir_list:    #  checking emptylness list
            for file_name in os.listdir(path):  #   addiing rcp to list
                if file_name.endswith('.rcp'):
                    rcp_list.append(file_name)

        for rcp in rcp_list:    #   adding list to comborecipies
            self._ui.comboRecipes.addItem(rcp)

    def on_serial_data_received(self):
        # TODO getting data from com port
        pass

    #   timers' functions
    def on_timed_process_event(self, source):
        self.process_end = True
        # todo remake

    def on_timed_ignition_event(self, source, event):
        self.ignition_start = False
        # todo remake

    def on_timed_send_received_modbus(self, source, event):
        modbusClient.connect()
        self.generator_hb = modbusClient.read_coils(self.settings.generator_hb,1)

        if self.lid_up_button:
            modbusClient.WriteSingleCoil(self.settings.lid_up_button, True)
            self.lid_up_button = False

        if self.lid_down_button:
            modbusClient.WriteSingleCoil(self.settings.lid_up_button, False)
            self.lid_down_button = False

        if self.vent_button:
            self.close_all_gas_valves()
            self.pump_valve.open()
            self.vent_valve.open()
            self.gas_out_valve.open()
          #  todo self.timer_pump_for_vent.start()
            self.vent_button = False

        if self.process_end:
            self.process_end = False
            self.proccess_started = False
            self.process_time = 0
            self.close_all_gas_valves()
            modbusClient.write_single_register(self.settings.mw_onoff,0)
            modbusClient.write_single_coil(self.settings.mw_apply_bit, True)
            modbusClient.write_single_coil(self.settings.ignition, False)
            self.valve_port.write('P90\r\n')
            # todo update labelState text => 'process is ended'

    def close_all_gas_valves(self):
        pass
