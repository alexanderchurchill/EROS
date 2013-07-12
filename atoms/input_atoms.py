from core.atom import *
from core.atom import _check_active_timer
from numpy import sin
class OscillatorAtom(SensorAtom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 amplitude=1,speed=1,no_outputs=1,parameters=None,id=None):
        super(OscillatorAtom, self).__init__(
            memory=memory,
            messages=messages,
            message_delays=message_delays,
            id=id,
            sensors=None,
            sensory_conditions=None
            )
        self.type = "sensory"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.activate_with_sensory_condition = False
        self.deactivate_with_sensory_condition = False
        self.amplitude = 0.5
        self.init_speed = speed
        self.speed = speed
        self.t = 0
        self.no_outputs = no_outputs
    def act(self):
        self.time_active += 1
        if (self.parameters["time_active"] is not "always"
            and self.time_active >= self.parameters["time_active"]
            and len(self.messages) > 0
            ):
            self.deactivate()
            self.active = False
            self.time_delayed = 0
            self.time_active = 0
        self.times_tested = self.times_tested + 1
        self.get_sensor_input()
        self.send_message("output",[sensor for sensor in self.sensor_input])

    def activate(self):
        self.get_sensor_input()
        conditions_met = True
        if conditions_met:
            Atom.activate(self)

    def mutate(self,mutation_rate=None):
        self.mutate_delays(config.mutation_rate)
        if mutation_rate is None:
            self.mutate_oscillator(config.mutation_rate)
        else:
            self.mutate_oscillator(mutation_rate)

    def mutate_oscillator(self,mutation_rate):
    	self.speed += random.uniform(-0.5,0.5)
    	if self.speed < 0.01:
    		self.speed = 0.01
		if self.speed > 5.0:
			self.speed = 5.0
        self.no_outputs += random.choice([-1,1])
        if self.no_outputs > 5:
            self.no_outputs = 5
        elif self.no_outputs < 1:
            self.no_outputs = 1

    def duplicate(self):
        new_atom = OscillatorAtom(
                    memory=self.memory,
                    messages=[],
                    message_delays=copy.deepcopy(self.message_delays),
                    parameters=copy.deepcopy(self.parameters),
                    amplitude = copy.deepcopy(self.amplitude),
                    speed = copy.deepcopy(self.speed),
                    no_outputs = copy.deepcopy(self.no_outputs),
                    )
        return new_atom

    def mutate_sensors(self):
        pass
    def get_sensor_input(self):
        self.sensor_input = [self.amplitude*sin(self.t*self.speed)+0.5]*self.no_outputs
        self.t += 1

    def can_connect_to(self):
        return ["sensory","motor","transform"]

    def deactivate(self,clear=False):
    	Atom.deactivate(self,clear)
    	if clear:
    		self.t = 0

    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "time_active: {0}\n".format(self.parameters["time_active"])
        output += "speed: {0}\n".format(self.speed)
        output += "amplitude: {0}\n".format(self.amplitude)
        output += "no_outputs: {0}\n".format(self.no_outputs)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

    def to_json(self):
        SensorAtom.to_json(self)
        for variable in ["amplitude","speed","no_outputs"]:
            self.json[variable] = self.__getattribute__(variable)
