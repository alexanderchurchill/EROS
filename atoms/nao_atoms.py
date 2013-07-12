from core.atom import *
from core.atom import _check_active_timer
from atoms.transform_atoms import SHCLTransAtom
######################
# Nao Atoms
######################

class NaoSensorAtom(SensorAtom):
    """
    The base class for a Nao specific sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,
                 parameters=None,nao_memory=None,id=None,
                 activate_with_sensory_condition=False,
                 deactivate_with_sensory_condition=False,
                 deactivate_downstream=False):
        super(NaoSensorAtom, self).__init__(
                                    memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    sensors=sensors,
                                    sensory_conditions=sensory_conditions,
                                    parameters=parameters,id=id
                                    )
        self.nao_memory = nao_memory
        self.activate_with_sensory_condition = activate_with_sensory_condition
        self.deactivate_with_sensory_condition = deactivate_with_sensory_condition
        self.deactivate_downstream = deactivate_downstream
    def get_sensor_input(self):
        self.sensor_input = []
        for s in self.sensors:
            self.sensor_input.append(self.nao_memory.getSensorValue(s))

    def duplicate(self):
        new_atom = NaoSensorAtom(
                    memory=self.memory,
                    messages=[],
                    message_delays=copy.deepcopy(self.message_delays),
                    sensors=copy.deepcopy(self.sensors),
                    sensory_conditions=copy.deepcopy(self.sensory_conditions),
                    nao_memory=self.nao_memory,
                    parameters=copy.deepcopy(self.parameters),
                    activate_with_sensory_condition=copy.deepcopy(self.activate_with_sensory_condition),
                    deactivate_with_sensory_condition=copy.deepcopy(self.deactivate_with_sensory_condition),
                    deactivate_downstream=copy.deepcopy(self.deactivate_downstream)
                    )
        return new_atom

    def get_unique_rand_sensor(self): 
        sensor = self.nao_memory.getRandomSensor()
        while sensor in self.sensors:
            sensor = self.nao_memory.getRandomSensor()
        return sensor

    def mutate_sensors(self,mutation_rate):
        for i,s in enumerate(self.sensors):
            if random.random() < mutation_rate:
                self.sensors[i] = self.get_unique_rand_sensor()
            for k, sc in enumerate(self.sensory_conditions[i]):
                if random.random() < mutation_rate:
                    original = self.sensory_conditions[i][k]
                    self.sensory_conditions[i][k] += random.uniform(-0.1,0.1)
                    if k == 0 and self.sensory_conditions[i][0] >= self.sensory_conditions[i][1]:
                        self.sensory_conditions[i][k] = original
                    if k == 1 and self.sensory_conditions[i][1] <= self.sensory_conditions[i][0]:
                        self.sensory_conditions[i][k] = original
                    elif self.sensory_conditions[i][k] > 1.0:
                        self.sensory_conditions[i][k] = 1.0
                    elif self.sensory_conditions[i][k] < 0.0:
                        self.sensory_conditions[i][k] = 0.0
        if len(self.sensors) < config.max_sensors_in_s_atom and random.random() < mutation_rate:
            self.sensors.append(self.get_unique_rand_sensor())
            end = random.uniform(0,1)
            self.sensory_conditions.append([random.uniform(0,end),end])
        if len(self.sensors) > config.max_sensors_in_s_atom:
            i = random.randint(0,len(self.sensors)-1)
            self.sensors.pop(i)
            self.sensory_conditions.pop(i)

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

class NaoMotorAtom(MotorAtom):
    """
    The base class for a Nao specific sensor atom
    """
    def __init__(self,memory=None,
                messages=None,message_delays=None,
                parameters=None,motors=None,
                nao_motion=None,nao_memory=None,
                use_input=False,id=None):
        super(NaoMotorAtom, self).__init__(
                                    memory=memory,
                                    messages=messages,
                                    message_delays=message_delays,
                                    parameters=parameters,
                                    motors=motors,
                                    id=id
                                    )
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        self.use_input = use_input
        self.angles = []
    def send_motors_message(self,motors,input,angles):
        self.send_message("motors",motors)
        self.send_message("output",input)
        self.send_message("angles",angles)

    def motion(self):
        real_angles = []
        names = []
        if self.use_input:
            # here we are using input from another atom, e.g. transfer atom
            angles = self.get_input()
            while len(angles) < len(self.motors):
                angles.append(self.parameters["motor_parameters"][len(angles)]) 
        else:
            angles = self.parameters["motor_parameters"]
        for index, i in enumerate(self.motors):
            name = self.nao_memory.getMotorName(i)
            names.append(name)
            real_angles.append(self.get_real_angles(i,angles[index]))
        self.nao_motion.motion.setAngles(names,real_angles,1)
        self.angles = angles
        self.send_motors_message(self.motors,angles,real_angles)

    def get_real_angles(self,motor,angle):
        if angle > 1.0:
            angle = 1.0
        elif angle < 0.0:
            angle = 0.0
        real_angle = self.nao_memory.get_real_motor_value(motor,angle)
        return real_angle

    def mutate_motors(self,mutation_rate):
        for i,motor in enumerate(self.motors):
            if random.random() < mutation_rate:
                self.motors[i] = self.get_unique_rand_motor()

    def mutate_angles(self,mutation_rate):
        angles = self.parameters["motor_parameters"]
        for i,angle in enumerate(angles):
            if random.random() < mutation_rate:
                angle = 0.5*(random.random()-0.5) + angle
            self.parameters["motor_parameters"][i] = angle

    def mutate(self):
        self.mutate_delays(config.mutation_rate)
        self.mutate_motors(config.mutation_rate)
        self.mutate_angles(config.mutation_rate)

    def get_unique_rand_motor(self):
        motor = self.nao_memory.getRandomMotor()
        while motor in self.motors:
            motor = self.nao_memory.getRandomMotor()
        return motor
###############################Deprecate this:
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
        new_atom = NaoMotorAtom(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters = copy.deepcopy(self.parameters),
                            motors=copy.deepcopy(self.motors),
                            nao_motion=self.nao_motion,
                            nao_memory=self.nao_memory,
                            use_input= copy.deepcopy(self.use_input)
                            )
        return new_atom

    def to_json(self):
        MotorAtom.to_json(self)
        for variable in ["use_input"]:
            self.json[variable] = self.__getattribute__(variable)

class SHCLtInternalSensor(SHCLTransAtom):
    """
    Atom used to transform sensor input to output
    """
    def __init__(self,memory=None,nao_memory=None,messages=None,message_delays=None,
                parameters=None,id=None,n=5,m=None,function="max",sensors=None):
        super(SHCLtInternalSensor, self).__init__(memory=memory,messages=messages,
                                    message_delays=message_delays,id=id,
                                    parameters=parameters,n=n,m=m,function=function)
        self.nao_memory = nao_memory
        self.sensors = sensors
        if self.sensors is None:
            self.sensors = []

    def get_sensor_input(self):
        self.sensor_input = []
        for s in self.sensors:
            self.sensor_input.append(self.nao_memory.getSensorValue(s))
        return self.sensor_input

    def get_unique_rand_sensor(self): 
        sensor = self.nao_memory.getRandomSensor()
        while sensor in self.sensors:
            sensor = self.nao_memory.getRandomSensor()
        return sensor

    def mutate(self):
        self.mutate_delays(config.mutation_rate)
        self.mutate_t_matrix(config.mutation_rate)

    def mutate_sensors(self,mutation_rate):
        for i,s in enumerate(self.sensors):
            if random.random() < mutation_rate:
                self.sensors[i] = self.get_unique_rand_sensor()
        if len(self.sensors) < config.max_sensors_in_s_atom and random.random() < mutation_rate:
            self.sensors.append(self.get_unique_rand_sensor())
        if len(self.sensors) > config.max_sensors_in_s_atom:
            i = random.randint(0,len(self.sensors)-1)
            self.sensors.pop(i)

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        if self.time_active > 2 and self.timer_count>1:
            self.timer_count = 0
            if len(inp) > 0:
                self.get_fitness(self.get_sensor_input())
                if self.curr_fitness > self.prev_fitness:
                    self.prev_t_matrix = copy.deepcopy(self.t_matrix)
                    self.shc_mutate_t_matrix()
                else:
                    self.t_matrix = copy.deepcopy(self.prev_t_matrix)
                    if random.random() < 0.7:
                        self.shc_mutate_t_matrix()
                    else:
                        self.prev_fitness = self.curr_fitness
                    self.curr_fitness = self.prev_fitness
        else:
            self.timer_count += 1
        output = self.get_output(inp,5)
        self.send_message("output",output)

    def duplicate(self):
        new_atom = SHCLtInternalSensor(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            n=self.n,
                            m=self.m,
                            function=copy.deepcopy(self.function),
                            sensors = copy.deepcopy(self.sensors),
                            nao_memory=self.nao_memory
                            )
        new_atom.set_t_matrix(copy.deepcopy(self.get_t_matrix()))
        return new_atom

    def to_json(self):
        SHCLTransAtom.to_json(self)
        for variable in ["function","sensors"]:
            self.json[variable] = self.__getattribute__(variable)
    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "parameters: {0}\n".format(self.parameters)
        output += "n: {0}\n".format(self.n)
        output += "t_matrix: {0}\n".format(self.t_matrix)
        output += "function: {0}\n".format(self.function)
        return output

