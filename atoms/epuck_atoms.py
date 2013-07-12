from core.atom import *
from core.atom import _check_active_timer

######################
# Epuck Atoms
######################

class EpuckSensorAtom(SensorAtom):
    """
    The base class for an epuck specific sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,
                 parameters=None,epuck_interface=None,id=None,
                 activate_with_sensory_condition=False,
                 deactivate_with_sensory_condition=False,
                 deactivate_downstream=False):
        super(EpuckSensorAtom, self).__init__(
                                    memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    sensors=sensors,
                                    sensory_conditions=sensory_conditions,
                                    parameters=parameters,id=id
                                    )
        self.epuck_interface = epuck_interface
        self.activate_with_sensory_condition = activate_with_sensory_condition
        self.deactivate_with_sensory_condition = deactivate_with_sensory_condition
        self.deactivate_downstream = deactivate_downstream
    def get_sensor_input(self):
        self.sensor_input = []

    def mutate(self,mutation_rate=None):
        self.mutate_delays(config.mutation_rate)
        if mutation_rate is None:
            self.mutate_sensors(config.mutation_rate)
        else:
            self.mutate_sensors(mutation_rate)

    def mutate_sensors(self,mutation_rate):
        pass

    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "sensors: {0}\n".format(self.sensors)
        output += "sensory_conditions: {0}\n".format(self.sensory_conditions)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "time_active: {0}\n".format(self.time_active)
        output += "time_delayed: {0}\n".format(self.time_delayed)
        return output

    def duplicate(self):
        new_atom = EpuckSensorAtom(
                    memory=self.memory,
                    messages=[],
                    message_delays=copy.deepcopy(self.message_delays),
                    sensors=copy.deepcopy(self.sensors),
                    sensory_conditions=copy.deepcopy(self.sensory_conditions),
                    epuck_interface=self.epuck_interface,
                    parameters=copy.deepcopy(self.parameters),
                    activate_with_sensory_condition=copy.deepcopy(self.activate_with_sensory_condition),
                    deactivate_with_sensory_condition=copy.deepcopy(self.deactivate_with_sensory_condition),
                    deactivate_downstream=copy.deepcopy(self.deactivate_downstream)
                    )
        return new_atom

class EpuckMultiSensor(EpuckSensorAtom):
    """
    The base class for an epuck specific sensor atom
    that accesses all of epucks sensors (camera and proximity)
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,
                 parameters=None,epuck_interface=None,id=None,to_print=False,
                 activate_with_sensory_condition=False,
                 deactivate_with_sensory_condition=False,
                 deactivate_downstream=False):
        super(EpuckMultiSensor, self).__init__(
                                    memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    sensors=sensors,
                                    sensory_conditions=sensory_conditions,
                                    parameters=parameters,id=id ,
                                    epuck_interface=epuck_interface,
                                    activate_with_sensory_condition=activate_with_sensory_condition,
                                    deactivate_with_sensory_condition=deactivate_with_sensory_condition,
                                    deactivate_downstream=deactivate_downstream)
        self.to_print = to_print
    def get_sensor_input(self):
        self.sensor_input = []
        for s in self.sensors:
            self.sensor_input.append(self.epuck_interface.get_multi_sensor_value(s))
        if self.to_print:
            print "[multi] sensors :{0} input:{1}".format(self.sensors,self.sensor_input)

    def get_unique_rand_sensor(self):
        sensor = self.epuck_interface.get_random_multi_sensor()
        while sensor in self.sensors:
            sensor = self.epuck_interface.get_random_multi_sensor()
        return sensor

    def mutate_sensors(self,mutation_rate):
        for i,s in enumerate(self.sensors):
            if random.random() < mutation_rate:
                self.sensors[i] = self.get_unique_rand_sensor()
            for k,sc in enumerate(self.sensory_conditions[i]):
                if random.random() < mutation_rate:
                    self.sensory_conditions[i][k] += random.uniform(-0.1,0.1)
                    if self.sensory_conditions[i][k] > 1.5:
                        self.sensory_conditions[i][k] = 1.5
                    if self.sensory_conditions[i][k] < -0.5:
                        self.sensory_conditions[i][k] = -0.5
        if len(self.sensors) < config.max_sensors_in_s_atom and random.random() < mutation_rate:
            self.sensors.append(self.get_unique_rand_sensor())
            end = random.uniform(0,1)
            self.sensory_conditions.append([random.uniform(0,end),end])
        if len(self.sensors) > config.max_sensors_in_s_atom:
            i = random.randint(0,len(self.sensors)-1)
            self.sensors.pop(i)
            self.sensory_conditions.pop(i)

    def duplicate(self):
        new_atom = EpuckMultiSensor(
                    memory=self.memory,
                    messages=[],
                    message_delays=copy.deepcopy(self.message_delays),
                    sensors=copy.deepcopy(self.sensors),
                    sensory_conditions=copy.deepcopy(self.sensory_conditions),
                    epuck_interface=self.epuck_interface,
                    parameters=copy.deepcopy(self.parameters),
                    activate_with_sensory_condition=copy.deepcopy(self.activate_with_sensory_condition),
                    deactivate_with_sensory_condition=copy.deepcopy(self.deactivate_with_sensory_condition),
                    deactivate_downstream=copy.deepcopy(self.deactivate_downstream)
                    )
        return new_atom


class EpuckProximSensor(EpuckSensorAtom):
    """
    Atom which accesses proximity sensors only
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,
                 parameters=None,epuck_interface=None,id=None,
                 activate_with_sensory_condition=False,
                 deactivate_with_sensory_condition=False,
                 deactivate_downstream=False):
        super(EpuckProximSensor, self).__init__(
									memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    sensors=sensors,
                                    sensory_conditions=sensory_conditions,
                                    parameters=parameters,id=id ,
                                    epuck_interface=epuck_interface,
                                    activate_with_sensory_condition=activate_with_sensory_condition,
                                    deactivate_with_sensory_condition=deactivate_with_sensory_condition,
                                    deactivate_downstream=deactivate_downstream)

    def get_sensor_input(self):
        self.sensor_input = []
        for s in self.sensors:
            print self.epuck_interface
            self.sensor_input.append(self.epuck_interface.get_proximity_sensor_value(s))

    def get_unique_rand_sensor(self):
        sensor = self.epuck_interface.get_random_proximity_sensor()
        while sensor in self.sensors:
            sensor = self.epuck_interface.get_random_proximity_sensor()
        return sensor

    def mutate_sensors(self,mutation_rate):
        for i,s in enumerate(self.sensors):
            if random.random() < mutation_rate:
                self.sensors[i] = self.get_unique_rand_sensor()

    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "sensors: {0}\n".format(self.sensors)
        output += "sensory_conditions: {0}\n".format(self.sensory_conditions)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "time_active: {0}\n".format(self.time_active)
        output += "time_delayed: {0}\n".format(self.time_delayed)
        return output

    def duplicate(self):
        new_atom = EpuckSensorAtom(
                    memory=self.memory,
                    messages=[],
                    message_delays=copy.deepcopy(self.message_delays),
                    sensors=copy.deepcopy(self.sensors),
                    sensory_conditions=copy.deepcopy(self.sensory_conditions),
                    epuck_interface=self.epuck_interface,
                    parameters=copy.deepcopy(self.parameters),
                    activate_with_sensory_condition=copy.deepcopy(self.activate_with_sensory_condition),
                    deactivate_with_sensory_condition=copy.deepcopy(self.deactivate_with_sensory_condition),
                    deactivate_downstream=copy.deepcopy(self.deactivate_downstream)
                    )
        return new_atom

class EpuckFullCameraSensor(EpuckSensorAtom):
    """
    Atom that accesses the full camera input as a PIL image file
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,
                 parameters=None,epuck_interface=None,id=None,
                 activate_with_sensory_condition=False,
                 deactivate_with_sensory_condition=False,
                 deactivate_downstream=False):
        super(EpuckFullCameraSensor, self).__init__(
									memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    sensors=sensors,
                                    sensory_conditions=sensory_conditions,
                                    parameters=parameters,id=id ,
                                    epuck_interface=epuck_interface,
                                    activate_with_sensory_condition=activate_with_sensory_condition,
                                    deactivate_with_sensory_condition=deactivate_with_sensory_condition,
                                    deactivate_downstream=deactivate_downstream
                                    )
        self.sensors = []

    def activate(self):
        self.get_sensor_input()
        conditions_met = True
        if len(self.sensor_input) < 1:
                conditions_met = False
        if conditions_met:
            Atom.activate(self)

    def get_sensor_input(self):
        self.sensor_input = []
        self.sensor_input.append(self.epuck_interface.get_camera_image())

    def mutate(self,mutation_rate=None):
    	if mutation_rate is None:
        	self.mutate_delays(config.mutation_rate)
    	else:
    		self.mutate_delays(mutation_rate)

    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "sensors: {0}\n".format(self.sensors)
        output += "sensory_conditions: {0}\n".format(self.sensory_conditions)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "time_active: {0}\n".format(self.time_active)
        output += "time_delayed: {0}\n".format(self.time_delayed)
        return output

    def duplicate(self):
        new_atom = EpuckFullCameraSensor(
                    memory=self.memory,
                    messages=[],
                    message_delays=copy.deepcopy(self.message_delays),
                    sensors=copy.deepcopy(self.sensors),
                    sensory_conditions=copy.deepcopy(self.sensory_conditions),
                    epuck_interface=self.epuck_interface,
                    parameters=copy.deepcopy(self.parameters),
                    activate_with_sensory_condition=copy.deepcopy(self.activate_with_sensory_condition),
                    deactivate_with_sensory_condition=copy.deepcopy(self.deactivate_with_sensory_condition),
                    deactivate_downstream=copy.deepcopy(self.deactivate_downstream)
                    )
        return new_atom

class EpuckSampledCameraSensor(EpuckFullCameraSensor):
    """
    Atom that accesses only sampled camera information
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,
                 parameters=None,epuck_interface=None,id=None,
                 activate_with_sensory_condition=False,
                 deactivate_with_sensory_condition=False,
                 deactivate_downstream=False):
        super(EpuckSampledCameraSensor, self).__init__(
                                    memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    sensors=sensors,
                                    sensory_conditions=sensory_conditions,
                                    parameters=parameters,id=id ,
                                    epuck_interface=epuck_interface,
                                    activate_with_sensory_condition=activate_with_sensory_condition,
                                    deactivate_with_sensory_condition=deactivate_with_sensory_condition,
                                    deactivate_downstream=deactivate_downstream
                                    )
        self.sensors = []

    def get_sensor_input(self):
        self.sensor_input = []
        self.sensor_input.append(self.epuck_interface.get_camera_image())

    def mutate(self,mutation_rate=None):
        if mutation_rate is None:
            self.mutate_delays(config.mutation_rate)
        else:
            self.mutate_delays(mutation_rate)

    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "sensors: {0}\n".format(self.sensors)
        output += "sensory_conditions: {0}\n".format(self.sensory_conditions)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "time_active: {0}\n".format(self.time_active)
        output += "time_delayed: {0}\n".format(self.time_delayed)
        return output

    def duplicate(self):
        new_atom = EpuckSampledCameraSensor(
                    memory=self.memory,
                    messages=[],
                    message_delays=copy.deepcopy(self.message_delays),
                    sensors=copy.deepcopy(self.sensors),
                    sensory_conditions=copy.deepcopy(self.sensory_conditions),
                    epuck_interface=self.epuck_interface,
                    parameters=copy.deepcopy(self.parameters),
                    activate_with_sensory_condition=copy.deepcopy(self.activate_with_sensory_condition),
                    deactivate_with_sensory_condition=copy.deepcopy(self.deactivate_with_sensory_condition),
                    deactivate_downstream=copy.deepcopy(self.deactivate_downstream)
                    )
        return new_atom

class EpuckMotorAtom(MotorAtom):
    """
    The base class for an Epuck motor atom
    """
    def __init__(self,memory=None,
                messages=None,message_delays=None,
                parameters=None,motors=None,
                epuck_interface=None,
                use_input=False,id=None):
        super(EpuckMotorAtom, self).__init__(
                                    memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    parameters=parameters,
                                    motors=motors,
                                    id=id
                                    )
        self.epuck_interface = epuck_interface
        self.use_input = use_input
        self.speeds = []
    def send_motors_message(self,motors,input,angles):
        self.send_message("motors",motors)
        self.send_message("output",input)
        self.send_message("speeds",angles)

    def motion(self):
        safe_speeds = []
        if self.use_input:
            # here we are using input from another atom, e.g. transfer atom
            speeds = self.get_input()
            while len(speeds) < len(self.motors):
                speeds.append(self.parameters["motor_parameters"][len(speeds)]) 
        else:
            speeds = self.parameters["motor_parameters"]
        for index, i in enumerate(self.motors):
            safe_speeds.append(self.get_safe_speeds(speeds[index]))
        self.epuck_interface.move_wheels(speeds=safe_speeds,wheels=self.motors)
        self.speeds = safe_speeds
        self.send_motors_message(self.motors,speeds,safe_speeds)

    def get_safe_speeds(self,speed):
        if speed < -1.0:
        	speed = -1.0
        elif speed > 1.0:
        	speed = 1.0
        return speed

    def mutate_motors(self,mutation_rate):
        if len(self.motors) < 2:
            for i,motor in enumerate(self.motors):
                if random.random() < mutation_rate:
                    self.motors[i] = self.get_unique_rand_motor()
            if random.random() < mutation_rate:
                self.motors.append(self.get_unique_rand_motor())
                self.parameters["motor_parameters"].append(2*(random.random()-0.5))
        else:
            # swap motors
            if random.random() < mutation_rate:
                temp = copy.deepcopy(self.motors[0])
                self.motors[0] = copy.deepcopy(self.motors[1])
                self.motors[1] = temp
            if random.random() < mutation_rate:
                i = random.randint(0,len(self.motors)-1)
                self.motors.pop(i)
                self.parameters["motor_parameters"].pop(i)

    def mutate_angles(self,mutation_rate):
        speeds = self.parameters["motor_parameters"]
        for i,speed in enumerate(speeds):
            if random.random() < mutation_rate:
                speed = 0.1*(random.random()-0.5) + speed
            self.parameters["motor_parameters"][i] = speed

    def mutate(self):
        self.mutate_delays(config.mutation_rate)
        self.mutate_motors(config.mutation_rate)
        self.mutate_angles(config.mutation_rate)

    def get_unique_rand_motor(self):
        motor = self.epuck_interface.get_random_wheel()
        while motor in self.motors:
            motor = self.epuck_interface.get_random_wheel()
        return motor

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp


    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "time_active: {0}\n".format(self.parameters["time_active"])
        output += "motors: {0}\n".format(self.motors)
        output += "motor_angles: {0}\n".format(
                                        self.parameters["motor_parameters"]
                                        )
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

    def duplicate(self):
        new_atom = EpuckMotorAtom(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters = copy.deepcopy(self.parameters),
                            motors=copy.deepcopy(self.motors),
                            epuck_interface=self.epuck_interface,
                            use_input= copy.deepcopy(self.use_input)
                            )
        return new_atom

    def to_json(self):
        MotorAtom.to_json(self)
        for variable in ["use_input"]:
            self.json[variable] = self.__getattribute__(variable)


