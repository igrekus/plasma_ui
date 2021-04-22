import json


class Settings:
    def __init__(self,
                 plc_ip_address="192.168.0.10",
                 comport_name="COM4",
                 plc_port=502,
                 comport_baudrate=9600,
                 gas_out_valve=16387,
                 pump_valve=16388,
                 vent_valve=16393,
                 ignition=16391,
                 com_bit=16384,
                 ar_valve=16388,
                 ar_mfc=16393,
                 ar_sccm=28712,
                 o2_valve=16389,
                 o2_mfc=16394,
                 o2_sccm=28714,
                 cf4_valve=16390,
                 cf4_mfc=16395,
                 cf4_sccm=28716,
                 n2_valve=16398,
                 n2_mfc=16399,
                 n2_sccm=28718,
                 mw_apply_bit=16408,
                 mw_ref=1,
                 mw_fow=0,
                 mw_onoff=2,
                 mw_read_bit=16413,
                 mw_fow_read=3,
                 mw_ref_read=4,
                 discrete_read=0,
                 lid_up_button=0,
                 generator_hb=0
                 ):
        self.plc_ip_address = plc_ip_address
        self.comport_name = comport_name
        self.plc_port = plc_port
        self.comport_baudrate = comport_baudrate
        self.gas_out_valve = gas_out_valve
        self.pump_valve = pump_valve
        self.vent_valve = vent_valve
        self.ignition = ignition
        self.com_bit = com_bit
        self.ar_valve = ar_valve
        self.ar_mfc = ar_mfc
        self.ar_sccm = ar_sccm
        self.o2_valve = o2_valve
        self.o2_mfc = o2_mfc
        self.o2_sccm = o2_sccm
        self.cf4_valve = cf4_valve
        self.cf4_mfc = cf4_mfc
        self.cf4_sccm = cf4_sccm
        self.n2_valve = n2_valve
        self.n2_mfc = n2_mfc
        self.n2_sccm = n2_sccm
        self.mw_apply_bit = mw_apply_bit
        self.mw_ref = mw_ref
        self.mw_fow = mw_fow
        self.mw_onoff = mw_onoff
        self.mw_read_bit = mw_read_bit
        self.mw_fow_read = mw_fow_read
        self.mw_ref_read = mw_ref_read
        self.discrete_read = discrete_read
        self.lid_up_button = lid_up_button
        self.generator_hb = generator_hb

    def write(self):
        data = self.__dict__
        with open('settings.json', 'wt') as outfile:
            json.dump(data, outfile)

    def initialize(self):
        with open('setting.json') as json_file:
            data = json.load(json_file)

        self.plc_ip_address = data['plc_ip_address']
        self.comport_name = data['comport_name']
        self.plc_port = data['plc_port']
        self.comport_baudrate = data['comport_baudrate']
        self.gas_out_valve = data['gas_out_valve']
        self.pump_valve = data['pump_valve']
        self.vent_valve = data['vent_valve']
        self.ignition = data['ignition']
        self.com_bit = data['com_bit']
        self.ar_valve = data['ar_valve']
        self.ar_mfc = data['ar_mfc']
        self.ar_sccm = data['ar_sccm']
        self.o2_valve = data['o2_valve']
        self.o2_mfc = data['o2_mfc']
        self.o2_sccm = data['o2_sccm']
        self.cf4_valve = data['cf4_valve']
        self.cf4_mfc = data['cf4_mfc']
        self.cf4_sccm = data['cf4_sccm']
        self.n2_valve = data['n2_valve']
        self.n2_mfc = data['n2_mfc']
        self.n2_sccm = data['n2_sccm']
        self.mw_apply_bit = data['mw_apply_bit']
        self.mw_ref = data['mw_ref']
        self.mw_fow = data['mw_fow']
        self.mw_onoff = data['mw_onoff']
        self.mw_read_bit = data['mw_read_bit']
        self.mw_fow_read = data['mw_fow_read']
        self.mw_ref_read = data['mw_ref_read']
        self.discrete_read = data['discrete_read']
        self.lid_up_button = data['lid_up_button']
        self.lid_down_button = data['lid_down_button']
        self.generator_hb = data['generator_hb']

# - code check file generation
# if __name__ == '__main__':
#     settings = Settings()
#     settings.write()
