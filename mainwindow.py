import os
import serial

import time

from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow
import json

from easymodbus.modbusClient import ModbusClient, Parity, Stopbits, convert_registers_to_float, \
    convert_float_to_two_registers

from Recipe import Recipe
from Settings import Settings
from Valve import GasValve
from Valve import Valve


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self._ui = uic.loadUi("mainwindow.ui", self)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # - private void MainForm_Load(object sender, EventArgs e)
        self.recipe = Recipe()  # -   recipies
        self.settings = Settings()  # -   settings
        # self.settings.initialize()

        # - ModbusClient PLC Connect
        self.modbusClient = ModbusClient('192.168.0.10', 502)
        self.modbusClient.parity = Parity.even
        self.modbusClient.unitidentifier = 2
        self.modbusClient.baudrate = 9600
        self.modbusClient.stopbits = Stopbits.one
        self.modbusClient.connect()

        self.gas_out_valve = Valve(self.settings.gas_out_valve, False, modbus_client=self.modbusClient)
        self.ar_valve = GasValve(self.settings.ar_valve, False, 0, self.settings.ar_mfc, self.settings.ar_sccm)
        self.o2_valve = GasValve(self.settings.o2_valve, False, 0, self.settings.o2_mfc, self.settings.o2_sccm)
        self.cf4_valve = GasValve(self.settings.cf4_valve, False, 0, self.settings.cf4_mfc, self.settings.cf4_sccm)
        self.n2_valve = GasValve(self.settings.n2_valve, False, 0, self.settings.n2_mfc, self.settings.n2_sccm)
        self.vent_valve = Valve(self.settings.vent_valve, False, modbus_client = self.modbusClient)
        self.pump_valve = Valve(self.settings.pump_valve, False, modbus_client = self.modbusClient)

        # -  public partial class MainForm : Form

        self.discreteInputs = self.modbusClient.read_discreteinputs(0, 8)

        self.holdingRegisters = convert_registers_to_float(self.modbusClient.read_holdingregisters(0, 2))
        print(self.holdingRegisters)
        self.inputRegisters = self.modbusClient.read_inputregisters(0, 8)
        print(self.inputRegisters)
        self.coils = self.modbusClient.read_coils(0, 8)
        print(self.coils)

        self.modbusClient.write_single_coil(0, True)
        self.modbusClient.write_single_register(0, 777)
        self.modbusClient.write_multiple_coils(0, [True, True, True, True, True, False, True, True])
        self.modbusClient.write_multiple_registers(0, convert_float_to_two_registers(3.141517))
        self.modbusClient.close()


        self.recipe_part = os.path.abspath('./recipies')
        self.throttle_valve_angle = 0.0
        self.timer_pump_for_vent = QTimer()  # -  pre_vent timer
        self.valve_port = serial.Serial(
            port=self.settings.comport_name,
            baudrate=self.settings.comport_baudrate,
            timeout=500,
            write_timeout=500,
        )  # -   com port variable
        # todo comport checking initialization

        # -  private static Valve VentValve;
        self.timer_send_receive_modbus = QTimer()  # -   plc call timer
        self.timer_check_trhrottle = QTimer()
        self.timer_pressure_read = QTimer()  # - pressure call timer
        self.timer_for_vent = QTimer()  # - vent timer
        self.timer_process = QTimer()  # -   process timer
        self.timer_ignition = QTimer()  # -   ignition process timer

        self.process_time_start = 0  # -   starting process time
        self.process_time_end = 0  # -   ending process time

        self.process_time = 0  # -   process time
        self.last_time = 0  # process remain time

        # - private static string SerialMessage
        self.pressure_read = 0.0  # -   baratron pressure
        self.pressure_angle = False  # -   pressure and status of the drosel valve's call
        self.process_started = False  # process status
        self.pre_pump_process_started = False  # pre pump process status
        self.pressure_input = 0  # reading value from the recipe
        self.throttle_valve = False  # throttle valve variable
        self.pump_for_vent = False  # venting
        self.vent_for_vent = False
        self.lid_up_button = False
        self.lid_down_button = False
        self.vent_button = False
        self.pump_button = False
        self.ignition_start = False
        self.start_button = False
        self.stop_button = False
        self.safe_button = False
        self.chiller_ok = False
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

        self.timer_send_receive_modbus.start(300)

    def read_recipes_from_folder(self):  # reading recipes from the folder
        path = "./Recipies"

        dir_list = os.listdir(path)
        rcp_list = []

        if dir_list:  # checking emptylness list
            for file_name in os.listdir(path):  # addiing rcp to list
                if file_name.endswith('.rcp'):
                    rcp_list.append(file_name)

        for rcp in rcp_list:  # adding list to comborecipies
            self._ui.comboRecipes.addItem(rcp)

    def switch_fields(self, parameter):
        pass
        # todo Color
        # formColor = SystemColors.Control;
        #
        # if (parameter) {formColor = Color.White;}
        # textBoxAr.Invoke((MethodInvoker)(() = > textBoxAr.Enabled = parameter));
        # textBoxO2.Invoke((MethodInvoker)(() = > textBoxO2.Enabled = parameter));
        # textBoxCF4.Invoke((MethodInvoker)(() = > textBoxCF4.Enabled = parameter));
        # textBoxN2.Invoke((MethodInvoker)(() = > textBoxN2.Enabled = parameter));
        # textBoxPower.Invoke((MethodInvoker)(() = > textBoxPower.Enabled = parameter));
        # textBoxTime.Invoke((MethodInvoker)(() = > textBoxTime.Enabled = parameter));
        # textBoxPressure.Invoke((MethodInvoker)(() = > textBoxPressure.Enabled = parameter));
        # textBoxPurge.Invoke((MethodInvoker)(() = > textBoxPurge.Enabled = parameter));
        # textBoxRecipeName.Invoke((MethodInvoker)(() = > textBoxRecipeName.Enabled = parameter));
        # listBoxRecipes.Invoke((MethodInvoker)(() = > listBoxRecipes.Enabled = parameter));
        # textBoxArLarge.Invoke((MethodInvoker)(() = > textBoxArLarge.BackColor = formColor));
        # textBoxO2Large.Invoke((MethodInvoker)(() = > textBoxO2Large.BackColor = formColor));
        # textBoxCF4Large.Invoke((MethodInvoker)(() = > textBoxCF4Large.BackColor = formColor));
        # textBoxN2Large.Invoke((MethodInvoker)(() = > textBoxN2Large.BackColor = formColor));
        # textBoxPowerLarge.Invoke((MethodInvoker)(() = > textBoxPowerLarge.BackColor = formColor));
        # textBoxTimeLarge.Invoke((MethodInvoker)(() = > textBoxTimeLarge.BackColor = formColor));
        # textBoxPressureLarge.Invoke((MethodInvoker)(() = > textBoxPressureLarge.BackColor = formColor));
        # textBoxPurgeLarge.Invoke((MethodInvoker)(() = > textBoxPurgeLarge.BackColor = formColor));
        # textBoxRecipeNameLarge.Invoke((MethodInvoker)(() = > textBoxRecipeNameLarge.BackColor = formColor));

    def on_serial_data_received(self):
        self.timer_check_trhrottle.stop()
        self.timer_check_trhrottle.start(2000)
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
        self.modbusClient.connect()
        self.generator_hb = self.modbusClient.read_coils(self.settings.generator_hb, 1)

        if self.lid_up_button:
            self.modbusClient.write_single_coil(self.settings.lid_up_button, True)
            self.lid_up_button = False

        if self.lid_down_button:
            self.modbusClient.write_single_coil(self.settings.lid_up_button, False)
            self.lid_down_button = False

        if self.vent_button:
            self.close_all_gas_valves()
            self.pump_valve.open()
            self.vent_valve.open()
            self.gas_out_valve.open()
            self.timer_pump_for_vent.start(10000)
            self.vent_button = False

        if self.process_end:
            self.process_end = False
            self.process_started = False
            self.process_time = 0
            self.close_all_gas_valves()
            self.modbusClient.write_single_register(self.settings.mw_onoff, 0)
            self.modbusClient.write_single_coil(self.settings.mw_apply_bit, True)
            self.modbusClient.write_single_coil(self.settings.ignition, False)
            self.valve_port.write('P90\r\n')
            # todo update labelState text => 'process is ended'

        if self.ignition_start == True:
            self.modbusClient.write_single_coil(self.settings.ignition, True)  # ignition turn-on
            # todo update labelstate text => 'ignition'
            self.timer_ignition.stop()
            self.timer_ignition.start(1000) #   ignition timer start
        else:
            self.modbusClient.write_single_coil(self.settings.ignition, False)  # ignition turn-off

        if self.pressure_read >= 100:
            vacuum = self.modbusClient.read_inputregisters(28696, 2)
            vac = convert_registers_to_float(vacuum)
            vac_round = round((vac / 10 - 1) * 200, 0)

            if vac_round >= 980:
                # todo textBoxPressureRead.Invoke((MethodInvoker)(() = > textBoxPressureRead.Text = "Атм."));
                # todo pictureBoxChamber.Invoke(
                # todo (MethodInvoker)(() = > pictureBoxChamber.Image = PLC_TEST.Properties.Resources.ChamberVent));
                #  todo buttonOpen.Invoke((MethodInvoker)(() = > buttonOpen.Enabled = true));
                #  todo buttonStart.Invoke((MethodInvoker)(() = > buttonStart.Enabled = false));
                pass

                if not self.venting:
                    # todo labelState.Invoke((MethodInvoker)(() => labelState.Text = "Напуск завершен"));
                    pass

            else:
                # todo textBoxPressureRead.Invoke((MethodInvoker)(() = > textBoxPressureRead.Text = "< Атм."));
                # todo pictureBoxChamber.Invoke(
                # todo     (MethodInvoker)(() = > pictureBoxChamber.Image = PLC_TEST.Properties.Resources.ChamberWarning));
                # todo buttonOpen.Invoke((MethodInvoker)(() = > buttonOpen.Enabled = false));
                # todo buttonStart.Invoke((MethodInvoker)(() = > buttonStart.Enabled = false));
                pass

        else:
            # todo buttonOpen.Invoke((MethodInvoker)(() = > buttonOpen.Enabled = false));

            if self.pressure_read > 1:
                # todo buttonStart.Invoke((MethodInvoker)(() = > buttonStart.Enabled = false));
                # todo pictureBoxChamber.Invoke((MethodInvoker)(() = > pictureBoxChamber.Image = PLC_TEST.Properties.Resources.ChamberWarning));
                pass

            else:
                if self.generator_hb[0] != 0:
                    # todo buttonStart.Invoke((MethodInvoker)(() = > buttonStart.Enabled = true));
                    pass
                else:
                    pass
                    # todo buttonStart.Invoke((MethodInvoker)(() = > buttonStart.Enabled = false));

                # todo pictureBoxChamber.Invoke((MethodInvoker)(() = > pictureBoxChamber.Image = PLC_TEST.Properties.Resources.ChamberPressure))
            pass

        if self.pre_pump_process_started:

            self.switch_fields(False)

            if not self.process_started:
                pass
                # todo labelState.Invoke((MethodInvoker)(() => labelState.Text = "Подача газа"));

            if self.pressure_input - 0.2 <= self.pressure_read <= self.pressure_input + 0.2 and self.process_started:   # if the pressure in chamber is equal to input value and the process is not started

                self.process_time_start = time.time()
                self.process_time_end = self.process_time_start + self.process_time
                self.timer_process.start(self.process_time)


                self.modbusClient.write_single_coil(self.settings.mw_apply_bit, True)

                self.ignition_start = True
                self.process_started = True


            if self.process_started:
                self.last_time = self.process_time_end - time.time()
                self._ui.processprogressBar.setValue(100 - ((self.last_time * 100) / self.process_time))
                self._ui.processtimelcdNumber.setValue(self.last_time)


                # todo last time
                # todo label time remain
                # todo progress bar


        if self.process_started:
            # todo inactive buttons
            # todo labelState.Invoke((MethodInvoker)(() => labelState.Text = "Процесс запущен"));
            self.modbusClient.write_single_coil(16413, True)  # reading forwarded and reflected power from PLC
            mw_read = self.modbusClient.read_inputregisters(3, 2)
            fow_power = mw_read[0]
            ref_power = mw_read[1]

            if fow_power / 10 >= ref_power:
                # todo pictureBoxChamber.Invoke((MethodInvoker)(() = > pictureBoxSource.Image = PLC_TEST.Properties.Resources.PlasmaSourceOn));
                pass

            else:
                pass
                # todo pictureBoxChamber.Invoke(
                #     (MethodInvoker)(() = > pictureBoxSource.Image = PLC_TEST.Properties.Resources.PlasmaSourceWarning));
                # todo }
                # todo textBoxFPowerRead.Invoke((MethodInvoker)(() = > textBoxFPowerRead.Text = FowPower.ToString()));
                # todo textBoxRPowerRead.Invoke((MethodInvoker)(() = > textBoxRPowerRead.Text = RefPower.ToString()));


        else:

            # todo pictureBoxChamber.Invoke(
            # todo    (MethodInvoker)(() = > pictureBoxSource.Image = PLC_TEST.Properties.Resources.PlasmaSourceOff));
            # todo textBoxFPowerRead.Invoke((MethodInvoker)(() = > textBoxFPowerRead.Text = "0"));
            # todo textBoxRPowerRead.Invoke((MethodInvoker)(() = > textBoxRPowerRead.Text = "0"));
            pass

        if self.pump_button:
            self.close_all_gas_valves()
            self.pump_valve.open()
            self.timer_pump_for_vent.stop()
            self.pump_button = False

        if self.start_button:
            self.modbusClient.write_single_register(self.settings.mw_fow, self.mw_power)  # sending power to generator
            self.modbusClient.write_single_register(self.settings.mw_ref, 100)  # sending reflected power to generator
            self.modbusClient.write_single_register(self.settings.mw_onoff, 210)  # setting generator's on-parameter

            if self.sccm_ar > 0:
                self.ar_valve.start_flow(self.sccm_ar)  # opening Ar line
            if self.sccm_o2 > 0:
                self.o2_valve.start_flow(self.sccm_o2)  # opening O2 line
            if self.sccm_cf4 > 0:
                self.cf4_valve.start_flow(self.sccm_cf4)  # opening CF4 line
            if self.sccm_n2 > 0:
                self.n2_valve.start_flow(self.sccm_n2)  # opening N2 line

            self.pump_valve.open()
            self.gas_out_valve.open()
            self.start_button = False

        if self.stop_button:
            # todo labelState.Invoke((MethodInvoker)(() => labelState.Text = "Процесс остановлен"));
            self.switch_fields(True)
            self.valve_port.write('P90\r\n')
            self.close_all_gas_valves()
            self.modbusClient.write_single_register(self.settings.mw_onoff, 0)  # turn off generator
            self.modbusClient.write_single_coil(self.settings.mw_apply_bit, True)  # using mw_apply_bit
            self.modbusClient.write_single_coil(self.settings.ignition, False)  # ignition
            self.process_started = False  # process is not run
            self.pre_pump_process_started = False  # process is not run
            self.stop_button = False

        self.descrete_read = self.modbusClient.read_discreteinputs(self.settings.discrete_read,
                                                              4)  # reading discrete values from plc (safe button and lid position)
        self.chiller_ok = self.discrete_read[3]  # reading flow detector cooling system
        self.safe_button = self.discrete_read[2]  # reading pressing safe button
        self.lid_down_button = self.discrete_read[1]  # reading lid low position

        if self.pump_for_vent:  # vent-before-pump
            self.pump_valve.close()  # close pump valve
            self.timer_for_vent.start()  # N2 stop-timer start
            self.pump_for_vent = False  # vent-before-pump turn-off

        if self.vent_for_vent:
            self.vent_valve.close()
            self.gas_out_valve.close()
            self.vent_for_vent = False

        if not self.process_started and not self.pre_pump_process_started and self.lid_down_bit:
            # todo buttons
            # todo buttons
            pass

        if not self.lid_down_bit:
            #  todo buttonVent.Invoke((MethodInvoker)(() = > buttonVent.Enabled = false));
            #  todo labelState.Invoke((MethodInvoker)(() = > labelState.Text = "Камера открыта"));
            #  todo buttonStart.Invoke((MethodInvoker)(() = > buttonStart.Enabled = false));
            #  todo buttonPump.Invoke((MethodInvoker)(() = > buttonPump.Enabled = false));
            #  todo pictureBoxLid.Invoke((MethodInvoker)(() = > pictureBoxLid.Image = PLC_TEST.Properties.Resources.LidOpen));

            if not self.safe_button:
                self.lid_up_button = True

        else:

            if self.lid_closing:
                self.lid_closing = False
                # todo labelState.Invoke((MethodInvoker)(() => labelState.Text = "Камера закрыта"));

            # todo pictureBoxLid.Invoke((MethodInvoker)(() => pictureBoxLid.Image = PLC_TEST.Properties.Resources.LidClose));

        try:
            self.mfc_read = self.modbusClient.read_inputregisters(28690, 6)

        except Exception as ex:
            # todo Console.WriteLine(ex.Message);
            # todo Console.WriteLine(MFC_READ[0] + ' ' + MFC_READ[1]+' ' + MFC_READ[2] + ' ' + MFC_READ[3] + ' ' + MFC_READ[4] + ' ' + MFC_READ[5]);
            pass
        ar_sccm_read = round(convert_registers_to_float(self.ar_mfc_read), 2)
        o2_sccm_read = round(convert_registers_to_float(self.o2_mfc_read), 2)
        cf4_sccm_read = round(convert_registers_to_float(self.cf4_mfc_read), 2)
        n2_mfc_read = self.modbusClient.read_inputregisters(28672, 2)
        n2_sccm_read = round(convert_registers_to_float(self.n2_mfc_read))

        # todo textBoxArRead.Invoke((MethodInvoker)(() = > textBoxArRead.Text = AR_SCCM_READ.ToString()));
        # todo textBoxO2Read.Invoke((MethodInvoker)(() = > textBoxO2Read.Text = O2_SCCM_READ.ToString()));
        # todo textBoxCF4Read.Invoke((MethodInvoker)(() = > textBoxCF4Read.Text = CF4_SCCM_READ.ToString()));
        # todo extBoxN2Read.Invoke((MethodInvoker)(() = > textBoxN2Read.Text = N2_SCCM_READ.ToString()));
        self.modbusClient.close()

    def on_timed_check_throttle_event(self):  # pump-before-vent timer triggering
        self.throttle_valve = False

    def on_timed_pump_for_vent_event(self):  # vent timer triggering
        self.pump_for_vent = True

    def on_timed_pressure_read_event(self):  # pressure and angle call timer triggering

        if self.throttle_valve:  # checking connection to throttle valve

            if self.pressure_angle:

                self.valve_port.write('R5\r\n')  # pressure read command send via Serial
                self.pressure_angle = False

            else:
                self.valve_port.write('R6\r\n')  # pressure read command send via Serial
                self.pressure_angle = True

    # connections

    def plc_connect(self):
        try:
            self.modbusClient.connect()

        except Exception as ex:
            print('error had happened during connection to PLC', ex)
            # todo writeLog("Ошибка подключения к ПЛК: ", ex.Message);
            return False

        return True

    def close_all_gas_valves(self):
        self.ar_valve.close()
        self.o2_valve.close()
        self.cf4_valve.close()
        self.n2_valve.close()
        self.vent_valve.close()
        self.gas_out_valve.close()

    def picture_box_throttle_valve_paint(self):  # throttle valve status drawing
        pass

    def text_box_key_press(self):  # only numbers are allowed
        pass

    # todo get ... number from gui

    def load_recipe(self):
        file_add = './Recipies/' + self._ui.comboRecipes.currentText()
        with open(file_add, 'r') as json_file:
            data = json.load(json_file)
        self._ui.ArspinBox.setValue(data['ar'])
        self._ui.O2spinBox.setValue(data['o2'])
        self._ui.CF4spinBox.setValue(data['cf4'])
        self._ui.N2spinBox.setValue(data['n2'])
        self._ui.tspinBox.setValue(data['process_time'])
        self._ui.WspinBox.setValue(data['power'])
        self._ui.pspinBox.setValue(data['pressure'])
        self._ui.tvspinBox.setValue(data['purge_time'])

    def save_recipe(self):
        data = {
            "ar": self._ui.ArspinBox.value(),
            "o2": self._ui.O2spinBox.value(),
            "cf4": self._ui.CF4spinBox.value(),
            "n2": self._ui.N2spinBox.value(),
            "power": self._ui.tspinBox.value(),
            "process_time": self._ui.WspinBox.value(),
            "pressure": self._ui.pspinBox.value(),
            "purge_time": self._ui.tvspinBox.value()
        }

        with open(self._ui.RecipeNameEdit.value() + '.rcp', 'wt') as outfile:
            json.dump(data, outfile)

    def main_form_load(self):
        # COMPORT Setup
        if self.valve_port.is_open:
            self.valve_port.write('D\r\n')
            self.throttle_valve = True
        # todo ValvePort.DataReceived += new SerialDataReceivedEventHandler(OnSerialDataReceived);

        if self.plc_connect:
            self.close_all_gas_valves()
            self.pump_valve.close()
            self.modbusClient.write_single_coil(self.settings.com_bit, True)  #
            self.modbusClient.close()




        # timers initialization
        #   check throttle valve timer
        self.timer_check_trhrottle.timeout.connect(self.on_timed_check_throttle_event)
        self.timer_check_trhrottle.setSingleShot(True)

        #   ignition timer initialization
        self.timer_ignition.timeout.connect(self.on_timed_ignition_event)
        self.timer_ignition.setSingleShot(True)

        #   process timer initialization
        self.timer_process.timeout.connect(self.on_timed_process_event)
        self.timer_process.setSingleShot(True)

        #   pump_for_vent timer inialization
        self.timer_pump_for_vent.timeout.connect(self.on_timed_pump_for_vent_event)
        self.timer_pump_for_vent.setSingleShot(True)

        #   pressure call timer initialization
        self.timer_pressure_read.timeout.connect(self.on_timed_pressure_read_event)
        self.timer_pressure_read.setSingleShot(False)

        #   vent timer initialization
        self.timer_for_vent.timeout.connect(self.on_timed_for_vent_event)
        self.timer_for_vent.setSingleShot(True)

        #   plc timer initialization
        self.timer_send_receive_modbus.timeout.connect(self.on_timed_send_received_modbus)
        self.timer_send_receive_modbus.setSingleShot(False)




    def main_form_form_closing(self):
        # todo ValvePort.DataReceived -= new SerialDataReceivedEventHandler(OnSerialDataReceived);
        self.timer_check_trhrottle.stop()
        self.timer_ignition.stop()
        self.timer_process.stop()
        self.timer_pump_for_vent.stop()
        self.timer_pressure_read.stop()
        self.timer_for_vent.stop()
        self.timer_send_receive_modbus.stop()


    #   SPINBOXES TO INT VALUES

    @pyqtSlot(int)
    def on_ArspinBox_valueChanged(self, value):
        print(value)

    @pyqtSlot(int)
    def on_O2spinBox_valueChanged(self, value):
        print(value)

    @pyqtSlot(int)
    def on_CF4spinBox_valueChanged(self, value):
        print(value)

    @pyqtSlot(int)
    def on_N2spinBox_valueChanged(self, value):
        print(value)

    @pyqtSlot(int)
    def on_tspinBox_valueChanged(self, value):
        print(value)

    @pyqtSlot(int)
    def on_WspinBox_valueChanged(self, value):
        print(value)

    @pyqtSlot(int)
    def on_pspinBox_valueChanged(self, value):
        print(value)

    @pyqtSlot(int)
    def on_tvspinBox_valueChanged(self, value):
        print(value)





    #   BUTTONS TRIGGERING

    @pyqtSlot()
    def on_PumpButton_clicked(self):  # pump button single click
        self.pump_button = True
        # todo labelState.Invoke((MethodInvoker)(() = > labelState.Text = "Производится откачка камеры"));
        if self.throttle_valve:
            self.valve_port.write('P90\r\n')
        print('Pump button is clicked')

    @pyqtSlot()
    def on_VentButton_clicked(self):  # vent button single click
        self.vent_button = True
        # todo labelState.Invoke((MethodInvoker)(() => labelState.Text = "Производится напуск камеры"));
        self.venting = True

        if self.throttle_valve:
            self.valve_port.write('P90\r\n')
        print('Vent button is clicked')

    @pyqtSlot()
    def on_StartButton_clicked(self):  # Start button single click
        self.sccm_ar = self._ui.ArspinBox.value()
        self.sccm_o2 = self._ui.O2spinBox.value()
        self.sccm_cf4 = self._ui.CF4spinBox.value()
        self.sccm_n2 = self._ui.N2spinBox.value()
        self.mw_power = self._ui.WspinBox.value()
        self.pressure_input = self._pspinBox.value()/100
        self.process_time = self._ui.tspinBox.value()/1000
        self.expultion_time = self._tvspinBox.value()/1000

        self.start_button = True

        if self.throttle_valve:
            self.valve_port.write('D\r\n')
            self.valve_port.write('D' + str(self.pressure_input) + '\r\n')
            # todo labelTimeLasts.Invoke((MethodInvoker)(() => labelTimeLasts.Text = (processtime / 1000).ToString()));
            self.pre_pump_process_started = True

        print('Start button is clicked')

    @pyqtSlot()
    def on_StopButton_clicked(self):  # Stop button single click
        self.stop_button = True
        # todo labelState.Invoke((MethodInvoker)(() => labelState.Text = "Процесс остановлен"));
        print('Stop button is clicked')

    @pyqtSlot()
    def on_LidUpButton_clicked(self):  # LidUp button single click
        self.lid_up_button = True
        print('LidUp button is clicked')

    @pyqtSlot()
    def on_LidDownButton_clicked(self):  # LidDown button single click
        if self.safe_button:
            self.lid_down_button = True
            self.lid_closing = True
        print('LidDown button is clicked')

    @pyqtSlot()
    def on_SaveRecipeButton_clicked(self):  # SaveRecipe button single click
        print('SaveRecipe button is clicked')

    # todo SaveRecipe

    @pyqtSlot()
    def on_LoadRecipeButton_clicked(self):  # LoadRecipe button single click
        print('LoadRecipe button is clicked')

    # todo LoadRecipe

    @pyqtSlot()
    def on_DeleteRecipeButton_clicked(self):  # DeleteRecipe button single click
        print('DeleteRecipe button is clicked')
    # todo deleteRecipe

# self.setAttribute(Qt.WA_QuitOnClose)
# self.setAttribute(Qt.WA_DeleteOnClose)



