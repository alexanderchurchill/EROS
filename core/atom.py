"""
Everything related to an atom is in here
"""
import random,copy,string,math
import config # from folder below
from numpy import mean,cov,double,cumsum,dot,linalg,array,rank,zeros,eye,ones,arange,vstack,r_,c_,set_printoptions,nan
from numpy.random import rand
from scipy.cluster.vq import kmeans,vq
from pylab import plot,subplot,axis,stem,show,figure,find, rand, randn,ion
import copy

# so we can store numpy arrays:
set_printoptions(threshold=nan)

######################
# decorators
######################

def _check_active_timer(f):
    """
    This is a decorator to make sure
    the should still be active
    """
    def wrapped(self,*args):
        self.time_active += 1
        if (self.parameters["time_active"] is not "always"
            and self.time_active >= self.parameters["time_active"]
            ):
            self.deactivate()
            self.active = False
            self.time_delayed = 0
            self.time_active = 0
        else:
            return f(self,*args)
    return wrapped

######################
# Base atom classes
######################

class Atom(object):
    """
    The base class for an atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        self.memory = memory
        self.messages = messages
        self.message_delays = message_delays
        self.active = False
        self.times_tested = 0
        self.fitness = 0 
        self.time_delayed = 0
        self.time_active = 0
        if id == None:
            self.id = self.create_id()
        else:
            self.id = id
        self.type = "base"
        self.json = {}

    def act(self):
        pass

    def mutate(self):
        pass

    def send_message(self,key,value):
        """
        Stores data centrally for other atoms
        to access
        """
        self.memory.send_message(self.id,key,value)

    def add_atom_to_memory(self):
        self.memory.add_key_to_memory(self.id)

    def send_active_message(self):
        """
        Sends active message to memory
        """
        self.send_message("active",True)

    def send_deactivate_message(self):
        """
        Sends deactive message to memory
        """
        self.send_message("active",False)

    def create_id(self,count=None):
        if count == None:
            id = "a-{0}-{1}".format(random.randint(1,5000),self._rand_char())
            while id in self.memory.atoms:
                id = "a-{0}-{1}".format(random.randint(1,5000),
                                    self._rand_char())
        else:
            id = "a-{0}".format(count)
        return id

    def set_id(self,id):
        self.id = id
    def get_id(self):
        return self.id

    def deactivate(self,clear=False):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        if clear:
            self.memory.clear_all_from_memory(self.id)
        self.send_deactivate_message()

    def activate(self):
        self.active = True
        self.send_active_message()

    def register_atom(self):
        self.add_atom_to_memory()
        self.send_deactivate_message()

    def conditional_activate(self):
        any_parent_active = False
        activated = False
        if self.messages is not None:
            for index, atom_id in enumerate(self.messages):
                if self.memory.get_message(atom_id,"active"):
                    if self.active is False:
                        if self.time_delayed >= self.message_delays[0]:
                            self.activate()
                            activated = True
                        # Incremement timer
                        self.time_delayed += 1
                        return activated
            if self.time_delayed > 0:
                if self.time_delayed >= self.message_delays[0]:
                    self.activate()
                self.time_delayed += 1
            return activated

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in self.messages:
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def mutate_delays(self,mutation_rate):
        if random.random() < mutation_rate and self.parameters["time_active"] != "always":
            self.parameters["time_active"] += random.randint(-2,2)
        if self.parameters["time_active"] < config.min_time_active:
            self.parameters["time_active"] = config.min_time_active
        elif self.parameters["time_active"] > config.max_time_active:
            self.parameters["time_active"] = config.max_time_active

        for i,delay in enumerate(self.message_delays):
            if random.random() < mutation_rate:
                self.message_delays[i]+= random.randint(-2,2)
                if self.message_delays[i] < config.min_message_delay:
                    self.message_delays[i] = config.min_message_delay
                elif self.message_delays[i] > config.max_message_delay:
                    self.message_delays[i] = config.max_message_delay

    def can_connect_to(self):
        return []
    def _rand_char(self):
        return ""+random.choice(string.letters)+random.choice(string.letters)

    def to_json(self):
        for variable in ["id","message_delays","type","time_active"]:
            self.json[variable] = self.__getattribute__(variable)
        self.json["class"]=self.__class__.__name__

    def get_json(self):
        # save to json
        self.to_json()
        return self.json

    def __str__(self):
        return str(self.get_id())

class SensorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,parameters=None,id=None):
        super(SensorAtom, self).__init__(memory=memory,messages=messages,
                                    message_delays=message_delays,id=id
                                    )
        self.sensors = sensors
        if self.sensors == None:
            self.sensors = []
        self.sensory_conditions = sensory_conditions
        if self.sensory_conditions == None:
            sensory_conditions = []
        self.sensor_input = None
        self.type = "sensory"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.activate_with_sensory_condition = False
        self.deactivate_with_sensory_condition = False
        self.deactivate_downstream = False

    def act(self):
        self.time_active += 1
        sensory_conditions = self.test_sensory_conditions()
        if ((self.parameters["time_active"] is not "always"
            and self.time_active >= self.parameters["time_active"]
            and len(self.messages) > 0
            ) or (sensory_conditions == False and self.deactivate_with_sensory_condition == True)):
            self.deactivate()
            self.active = False
            self.time_delayed = 0
            self.time_active = 0
            if sensory_conditions == False:
                # print "[atom] deactivating downstream"
                self.deactivate_downstream = True
        self.times_tested = self.times_tested + 1
        self.get_sensor_input()
        self.send_message("output",[sensor for sensor in self.sensor_input])

    def activate(self):
        self.get_sensor_input()
        conditions_met = self.test_sensory_conditions()
        # print "conditions_met:",conditions_met
        # print "atom active:",self.active
        if conditions_met:
            Atom.activate(self)

    def test_sensory_conditions(self):
        conditions_met = True
        if config.use_sensory_conditions and self.activate_with_sensory_condition:
            for sensor,condition in zip(self.sensor_input,self.sensory_conditions):
                # print "[test_sensory_conditions] sensor:",sensor
                # print "[test_sensory_conditions] condition:",condition
                if sensor < condition[0] or sensor > condition[1]:
                    conditions_met = False
                # print "conditions_met:",conditions_met
        return conditions_met

    def mutate(self,mutation_rate=None):
        self.mutate_delays(config.mutation_rate)
        if mutation_rate is None:
            self.mutate_sensors(config.mutation_rate)
        else:
            self.mutate_sensors(mutation_rate)

    def mutate_sensors(self):
        pass
    def get_sensor_input(self):
        pass

    def can_connect_to(self):
        return ["sensory","motor","transform"]

    def to_json(self):
        Atom.to_json(self)
        for variable in ["sensors","sensory_conditions","parameters",
                         "activate_with_sensory_condition",
                         "deactivate_with_sensory_condition"]:
            self.json[variable] = self.__getattribute__(variable)


class TransformAtom(Atom):
    """
    The base class for a transform atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None):
        super(TransformAtom, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        output = inp
        self.send_message("output",inp)

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in self.messages:
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def duplicate(self):
        new_atom = TransformAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters)
                            )
        return new_atom

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

    def can_connect_to(self):
        return ["sensory","motor","transform"]

    def to_json(self):
        Atom.to_json(self)
        for variable in ["parameters"]:
            self.json[variable] = self.__getattribute__(variable)


class MotorAtom(Atom):
    """
    The base class for a motor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 parameters=None,motors=None,id=None):
        super(MotorAtom, self).__init__(memory,messages,message_delays,id=id)
        self.motors = motors
        self.parameters = parameters
        self.type = "motor"

    @_check_active_timer
    def act(self):
        self.motion()

    def motion(self):
        pass

    def can_connect_to(self):
        return ["sensory","motor","transform"]

    def to_json(self):
        Atom.to_json(self)
        for variable in ["motors","parameters"]:
            self.json[variable] = self.__getattribute__(variable)


class GameAtom(Atom):
    """
    The base class for a game atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(GameAtom, self).__init__(memory=memory,messages=messages,
            message_delays=message_delays,id=id)
        self.type = "game"
        self.state = []

    def get_fitness(self):
        pass

    def clear_game_history(self):
        self.state = []

