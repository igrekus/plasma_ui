class Valve:

    def __init__(self,
                 valve_address,
                 valve_opened,
                 picture_image):
        self.valve_address = valve_address
        self.valve_opened = valve_opened
        self.picture_image = picture_image

    def close(self):
        self.valve_opened = False
        ##TODO implement valve state close

    def open(self):
        self.valve_opened = True
        ##TODO implement valve state open

    def is_opened(self):
        ##TODO implement valve state is_open
        pass


class GasValve(Valve):

    def __init__(self,
                 mfc_enable_address,
                 mfc_flow_address,
                 flow_rate,
                 valve_address,
                 valve_opened,
                 picture_image):
        super().__init__(valve_address,
                         valve_opened,
                         picture_image)
        self.mfc_enable_address = mfc_enable_address
        self.mfc_flow_address = mfc_flow_address
        self.mfc_flow_address = flow_rate

    def start_flow(self, new_flow_rate):
        self.valve_opened = True
        self.flow_rate = new_flow_rate
        ##TODO implement valve state start_flow

    def close(self):
        self.valve_opened = False
        self.flow_rate = 0
        ##TODO implement valve state start_flow_close
