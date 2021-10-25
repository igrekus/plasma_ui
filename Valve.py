from easymodbus.run import ModbusClient


class Valve:

    def __init__(self, valve_address, valve_opened, ):
        self.valve_address = valve_address
        self.valve_opened = valve_opened

    def close(self):
        self.valve_opened = False
        self.modbusClient.write_single_coil(self.valve_address, self.valve_opened)
        ##TODO implement valve state close

    def open(self):
        self.valve_opened = True
        modbusClient.write_single_coil(self.valve_address, self.valve_opened)
        ##TODO implement valve state open

    def is_opened(self):
        self.valve_opened = modbusClient.read_coils(self.valve_address, 0)
        return self.valve_opened


class GasValve(Valve):

    def __init__(self, valve_address, valve_opened, flow_rate, mfc_enable_address, mfc_flow_address, new_flow_rate=0.0):
        super().__init__(valve_address, valve_opened)
        self.flow_rate = new_flow_rate
        self.mfc_enable_address = mfc_enable_address
        self.mfc_flow_address = mfc_flow_address
        self.mfc_flow_rate = flow_rate

    def start_flow(self):
        self.valve_opened = True
        modbusClient.write_single_coil(self.valve_address, self.valve_opened)
        modbusClient.write_single_coil(self.mfc_enable_address, self.valve_opened)
        modbusClient.write_multiple_registers(self.mfc_flow_address,
                                              modbusClient.convert_registers_to_float(self.flow_rate))

    def close(self):
        self.valve_opened = False
        self.flow_rate = 0.0
        modbusClient.write_single_coil(self.valve_address, self.valve_opened)
        modbusClient.write_single_coil(self.mfc_enable_address, self.valve_opened)
        modbusClient.write_multiple_registers(self.mfc_flow_address,
                                              modbusClient.convert_registers_to_float(self.flow_rate))
