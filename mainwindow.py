import os
import serial
from PyQt6 import uic
from PyQt6.QtCore import QTimer, QTime
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow
from easymodbus.run import modbusClient

from Recipe import Recipe
from Settings import Settings
from Valve import GasValve
from Valve import Valve


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # - private void MainForm_Load(object sender, EventArgs e)

        self.gas_out_valve = Valve(self.settings.gas_out_valve, False, QPixmap)
        self.ar_valve = GasValve(self.setting.ar_valve, False, 0, self.settings.ar_mfc, self.settings.ar_sccm, QPixmap)
        self.o2_valve = GasValve(self.settings.o2_valve, False, 0, self.settings.o2_mfc, self.settings.o2_sccm,
                                 QPixmap())
        self.cf4_valve = GasValve(self.settings.cf4_valve, False, 0, self.settings.cf4_mfc, self.settings.cf4_sccm,
                                  QPixmap())
        self.n2_valve = GasValve(self.settings.n2_valve, False, 0, self.settings.n2_mfc, self.settings.n2_sccm,
                                 QPixmap())
        self.vent_valve = Valve(self.settings.vent_valve, False, QPixmap())
        self.pump_valve = Valve(self.settings.pump_valve, False, QPixmap())

        # -  public partial class MainForm : Form
        self.recipe = Recipe()  # -   recipies
        self.settings = Settings()  # -   settings
        self.settings.initialize()
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
        self.timer.ignition = QTimer()  # -   ignition process timer

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

        # self.setAttribute(Qt.WA_QuitOnClose)
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self._ui = uic.loadUi("mainwindow.ui", self)
