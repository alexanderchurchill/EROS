######################
# Arduino Molecules
######################
from core.molecule import *
from atoms.input_atoms import *
from atoms.game_atoms import *
from atoms.transform_atoms import *
from atoms.arduino_atoms import *

class ArduinoActorMolecule(ActorMolecule):
    """
    The data structure for an ArduinoActorMolecule
    """
    def __init__(self, memory,atoms,arduino_interface,duplication=False):
        super(ArduinoActorMolecule, self).__init__(memory,atoms)
        self.arduino_interface = arduino_interface
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        Start with 2 sensors, an Izhikevich and 3 motors
        """
        print "creating random sensor"
        atom_1 = self.create_random_sensor_atom(add=False)
        print "created random sensor:",atom_1
        atom_1.parameters["time_active"] = 100
        atom_2 = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[1],
            n=5,
            parameters={
            "time_active":100
            }
            )
        print "creating motor"
        atom_3 = self.create_random_motor_atom(add=False)
        print "created motor"
        atom_3.use_input = True
        atom_3.parameters["time_active"] = 100
        atom_3.message_delays = [1]
        for a in [atom_1,atom_2,atom_3]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            ])
        print "finished molecule"

    def get_random_motors(self,arduino_interface,n_motors):
        motors = []
        for i in range(0,n_motors):
            motor = arduino_interface.get_random_motor()
            while motor in motors:
                motor = arduino_interface.get_random_motor()
            motors.append(motor)
        return motors

    def get_random_sensors(self,arduino_interface,n_sensors):
        sensors = []
        for i in range(0,n_sensors):
            sensor = arduino_interface.get_random_sensor()
            while sensor in sensors:
                sensor = arduino_interface.get_random_sensor()
            sensors.append(sensor)
        return sensors

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()

    def create_random_motor_atom(self,add=True):
        no_motors = self.get_random_motor_length()
        atom = ArduinoMotorAtom(
            memory=self.memory,
            arduino_interface=self.arduino_interface,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            motors = self.get_random_motors(self.arduino_interface,no_motors),
            parameters = {
            "time_active":self.get_random_time_active(),
            "motor_parameters":[2*(random.random()-0.5)
                                for i in range(0,no_motors)],
            "times":[1, 1, 1]
            },
            use_input=True)
        if add:
            self.memory.add_atom(atom)
        return atom

    def create_and_add_atom(self,a_type=None):
        if a_type is None:
            a_type = random.choice(["motor","sensory","transform"])
        if a_type == "motor":
            print "adding motor atom"
            atom = self.create_random_motor_atom()
        elif a_type == "sensory":
            print "adding sensory atom"
            atom = self.create_random_sensor_atom()
        elif a_type == "transform":
            print "adding transform atom"
            atom = self.create_random_transform_atom()
        connecting_atom = random.choice(self.molecular_graph.nodes())
        if random.random() < 0.5:
            self.add_atom_from(atom.get_id(),connecting_atom)
            print "adding from"
        else:
            self.add_atom_to(atom.get_id(),connecting_atom)
            print "adding to"
        self.set_connections()

    def create_random_sensor_atom(self,add=True):
        no_sensors = self.get_random_sensor_length()
        atom = ArduinoSensorDataAtom(memory=self.memory,arduino_interface=self.arduino_interface,
            sensors=self.get_random_sensors(self.arduino_interface,no_sensors),
            sensory_conditions=[],
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active(),
            },
            )
        for i in atom.sensors:
            end = random.uniform(0,1.5)
            atom.sensory_conditions.append([random.uniform(-0.5,end),end])
        atom.activate_with_sensory_condition=True
        if add:
            self.memory.add_atom(atom)
        return atom

    def create_random_transform_atom(self):
        atom_to_create = random.choice(["linear",
                                        # "euclidian",
                                        # "pca",
                                        # "lwpr",
                                        # "k_means_class",
                                        # "izhikevich"
                                        ])
        if atom_to_create == "linear":
            atom = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        elif atom_to_create == "euclidian":
            no_goals = random.randint(1,4)
            atom = EuclidianDistanceAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                goal_output=[5*(random.random()-0.5)
                                for i in range(0,no_goals)],
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        elif atom_to_create == "pca":
            atom = PCATranformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                N=random.randint(1,4),
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        elif atom_to_create == "lwpr":
            atom = LWPRTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                N=random.randint(3,20),
                parameters={
                "time_active":self.get_random_time_active()
                },
                inputs = random.randint(1,5)
                )
        elif atom_to_create == "k_means_class":
            atom = KMeansClassifyAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                K=random.randint(1,5),
                parameters={
                "time_active":self.get_random_time_active()
                },
                )
        elif atom_to_create == "izhikevich":
            atom = IzhikevichTransformAtom(memory=self.memory,messages=[],message_delays=[1],
                    parameters = {
                    "time_active":1000
                    },
                    assign_inputs_to_neurons=[
                    [random.sample(range(100), 5)] for i in range(0,10)],
                    weight_spikes=[[random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)],
                    [random.random()-0.5 for x in range(0, 5)]],
                    no_outputs=random.randint(1,5))
        print "adding:",atom_to_create
        self.memory.add_atom(atom)
        return atom

    def create_and_add_stm_group(self):
        sensor = self.create_random_sensor_atom()
        transform = self.create_random_transform_atom()
        motor = self.create_random_motor_atom()
        allowed_connectors = self.find_atoms_of_types(
                                                self.molecular_graph,
                                                sensor.can_connect_to()
                                                )
        parent = random.choice(allowed_connectors)
        for n in [sensor,transform,motor]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),transform.get_id())
        self.add_edge(transform.get_id(),motor.get_id())
        self.add_atom_from(sensor.get_id(),parent=parent)

    def deactivate(self):
        for atom in self.get_atoms_as_list():
            atom.deactivate(clear=True)

    def duplicate(self):
        new_molecule = ArduinoActorMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        arduino_interface=self.arduino_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class ArduinoGameMolecule(GameMolecule):
    """
    The data structure for a basic Arduino game molecule
    """
    def __init__(self, memory,atoms,arduino_interface,duplication=False):
        super(ArduinoGameMolecule, self).__init__(memory,atoms)
        self.arduino_interface = arduino_interface
        self.id = self.create_id()
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = ArduinoSensorDataAtom(memory=self.memory,arduino_interface=self.arduino_interface,
            sensors=[0],
            sensory_conditions=[[-0.5,1.5]],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            },
            to_print=False)
        atom_2 = MaxSensorGame(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        for a in [atom_1,atom_2]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id())
        self.molecular_graph.add_node(atom_2.get_id())
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            ])
        self.game_atoms.append(atom_2.get_id())

    def duplicate(self):
        new_molecule = ArduinoGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        arduino_interface=self.arduino_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class ArduinoTestActor(ArduinoActorMolecule):
    """
    The data structure for an ArduinoActorMolecule
    """
    def __init__(self, memory,atoms,arduino_interface,duplication=False):
        super(ArduinoTestActor, self).__init__(memory,atoms,arduino_interface)
        self.arduino_interface = arduino_interface
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        Start with 2 sensors, an Izhikevich and 3 motors
        """
        print "creating random sensor"
        atom_1 = self.create_random_sensor_atom(add=False)
        atom_1.sensors = [0]
        print "created random sensor:",atom_1
        atom_1.parameters["time_active"] = 100
        atom_2 = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[1],
            n=5,
            parameters={
            "time_active":100
            }
            )
        print "creating motor"
        atom_3 = self.create_random_motor_atom(add=False)
        print "created motor"
        atom_3.motors = [0]
        atom_3.use_input = False
        atom_3.parameters["time_active"] = 100
        atom_3.message_delays = [1]
        for a in [atom_1,atom_2,atom_3]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            ])
        print "finished molecule"


