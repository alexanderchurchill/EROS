######################
# Epuck Molecules
######################
from core.molecule import *
from atoms.input_atoms import *
from atoms.game_atoms import *
from atoms.transform_atoms import *
from atoms.epuck_atoms import *

class EpuckActorMolecule(ActorMolecule):
    """
    The data structure for a EpuckActorMolecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckActorMolecule, self).__init__(memory,atoms)
        self.epuck_interface = epuck_interface
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()
    def activate(self):
        """
        activate molecule
        """
        self.times_tested += 1
        disjoint_units = self.get_connected_components(self.molecular_graph)
        activation_map = {}
        longest_active = 0
        longest_active_group = 0
        for i,unit in enumerate(disjoint_units):
            for atom_id in unit:
                atom = self.get_atom(atom_id)
                if atom.type == "sensory" and len(atom.messages) == 0:
                    atom.activate()
                    if atom.active:
                        if i in activation_map:
                            activation_map[i] += [atom]
                        else:
                            activation_map[i] = [atom]
                        if atom.time_active > longest_active:
                            longest_active = atom.time_active
                            longest_active_group = i
        if len(activation_map) > 0:
            deactivate = []
            if longest_active > 10 and len(activation_map) > 1:
                activate = random.choice([key for key in activation_map.keys() if key != longest_active_group])
                deactivate = [key for key in activation_map.keys() if key != activate]
            if longest_active > 0 and longest_active <= 10:
                activate = longest_active_group
                deactivate = [key for key in activation_map.keys() if key != activate]
            if longest_active == 0:
                activate = random.choice([key for key in activation_map.keys()])
            for group in deactivate:
                for atom_id in disjoint_units[group]:
                    self.get_atom(atom_id).deactivate()
            self.active = True
            self.active_hist = True
        if self.active:
            self.conditional_activate()
        # print "activation_map:",activation_map

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

    def get_random_motors(self,epuck_interface,n_motors):
        motors = []
        for i in range(0,n_motors):
            motor = epuck_interface.get_random_wheel()
            while motor in motors:
                motor = epuck_interface.get_random_wheel()
            motors.append(motor)
        return motors

    def get_random_sensors(self,epuck_interface,n_sensors):
        sensors = []
        for i in range(0,n_sensors):
            sensor = epuck_interface.get_random_multi_sensor()
            while sensor in sensors:
                sensor = epuck_interface.get_random_multi_sensor()
            sensors.append(sensor)
        return sensors

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()

    def create_random_motor_atom(self,add=True):
        no_motors = self.get_random_motor_length()
        atom = EpuckMotorAtom(
            memory=self.memory,
            epuck_interface=self.epuck_interface,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            motors = self.get_random_motors(self.epuck_interface,no_motors),
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
        atom = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=self.get_random_sensors(self.epuck_interface,no_sensors),
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
        new_molecule = EpuckActorMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckGameMolecule(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckGameMolecule, self).__init__(memory,atoms)
        self.epuck_interface = epuck_interface
        self.id = self.create_id()
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[0,1,2,3,4,5,6,7],
            sensory_conditions=[-10000.0],
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
        new_molecule = EpuckGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckDistanceGameMolecule(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckDistanceGameMolecule, self).__init__(memory,atoms)
        self.epuck_interface = epuck_interface
        self.id = self.create_id()
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[200,201],
            sensory_conditions=[[0.0,1.0],[0.0,1.0]],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            },
            to_print=False)
        atom_2 = DistanceGameAtom(
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
        new_molecule = EpuckDistanceGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckDistanceProximityGameMolecule(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckDistanceProximityGameMolecule, self).__init__(memory,atoms)
        self.epuck_interface = epuck_interface
        self.id = self.create_id()
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[200,201],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            },
            to_print=False)
        atom_2 = DistanceGameAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        atom_3 = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[0,1,2,3,4,5,6,7],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            },
            to_print=False)
        atom_4 = MaxSensorGame(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        atom_5 = LinearTransformAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            },
            n=1,
            m=2)
        atom_5.t_matrix = [[1],
                           [0.01],
                           [0]]
        atom_6 = LastOutputGameAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5,atom_6]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id())
        self.molecular_graph.add_node(atom_2.get_id())
        self.molecular_graph.add_node(atom_3.get_id())
        self.molecular_graph.add_node(atom_4.get_id())
        self.molecular_graph.add_node(atom_5.get_id())
        self.molecular_graph.add_node(atom_6.get_id())
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_3.get_id(),atom_4.get_id()),
            (atom_2.get_id(),atom_5.get_id()),
            (atom_4.get_id(),atom_5.get_id()),
            (atom_5.get_id(),atom_6.get_id()),
            ])
        self.game_atoms.append(atom_2.get_id())

    def get_fitness(self):
        fitness = -999999
        for game in [a for a in self.get_atoms_as_list()
                        if a.type =="game"]:
            fitness = game.get_fitness()
            if a.__class__.__name__ == "LastOutputGameAtom":
                return fitness
        return fitness

    def duplicate(self):
        new_molecule = EpuckDistanceGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckDistProximMovingGame(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckDistanceProximityGameMolecule, self).__init__(memory,atoms)
        self.epuck_interface = epuck_interface
        self.id = self.create_id()
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[200,201],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            },
            to_print=False)
        atom_2 = TimeNotMovingAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        atom_3 = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[0,1,2,3,4,5,6,7],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            },
            to_print=False)
        atom_4 = MaxSensorGame(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        atom_5 = LinearTransformAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            },
            n=1,
            m=3)
        atom_5.t_matrix = [[-10],
                           [0.01],
                           [0]]
        atom_6 = LastOutputGameAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5,atom_6,
        ]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id())
        self.molecular_graph.add_node(atom_2.get_id())
        self.molecular_graph.add_node(atom_3.get_id())
        self.molecular_graph.add_node(atom_4.get_id())
        self.molecular_graph.add_node(atom_5.get_id())
        self.molecular_graph.add_node(atom_6.get_id())
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_3.get_id(),atom_4.get_id()),
            (atom_2.get_id(),atom_5.get_id()),
            (atom_4.get_id(),atom_5.get_id()),
            (atom_5.get_id(),atom_6.get_id()),
            ])
        self.game_atoms.append(atom_2.get_id())

    def get_fitness(self):
        fitness = -999999
        for game in [a for a in self.get_atoms_as_list()
                        if a.type =="game"]:
            fitness = game.get_fitness()
            if a.__class__.__name__ == "LastOutputGameAtom":
                return fitness
        return fitness

    def duplicate(self):
        new_molecule = EpuckDistanceGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckMaxPixelsGameMolecule(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckGameMolecule, self).__init__(memory,atoms)
        self.epuck_interface = epuck_interface
        self.id = self.create_id()
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = EpuckFullCameraSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            })

        atom_2 = AveragePixelAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":"always",
            })
        atom_3 = MaxSensorGame(
            memory=self.memory,
            messages=[],
            message_delays=[1]
            )
        for a in [atom_1,atom_2,atom_3]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id())
        self.molecular_graph.add_node(atom_2.get_id())
        self.molecular_graph.add_node(atom_3.get_id())
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id())
            ])
        self.game_atoms.append(atom_3.get_id())

    def duplicate(self):
        new_molecule = EpuckGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckCameraActorMolecule(EpuckActorMolecule):
    """
    The data structure for a EpuckActorMolecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckCameraActorMolecule, self).__init__(memory,atoms,epuck_interface)
        self.epuck_interface = epuck_interface
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        Start with 2 sensors, an Izhikevich and 3 motors
        """
        atom_1 = EpuckFullCameraSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            })
        atom_2 = AveragePixelAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            })
        atom_3 = SumInputAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            },
            normalise=1000)
        atom_4 = LinearTransformAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            },
            n=2,
            m=1)
        atom_5 = self.create_random_motor_atom(add=False)
        atom_5.use_input = True
        atom_5.parameters["time_active"] = 1000
        atom_5.message_delays = [1]
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_4.get_id(),color=graph_colours[atom_4.type])
        self.molecular_graph.add_node(atom_5.get_id(),color=graph_colours[atom_5.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_3.get_id(),atom_4.get_id()),
            (atom_4.get_id(),atom_5.get_id()),
            ])
    def duplicate(self):
        new_molecule = EpuckCameraActorMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckSampledCamActorMolecule(EpuckActorMolecule):
    """
    The data structure for a EpuckActorMolecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckSampledCamActorMolecule, self).__init__(memory,atoms,epuck_interface)
        self.epuck_interface = epuck_interface
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        Start with 2 sensors, an Izhikevich and 3 motors
        """
        atom_1 = EpuckMultiSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            })
        atom_2 = AveragePixelAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            })
        atom_3 = SumInputAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            },
            normalise=1000)
        atom_4 = LinearTransformAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            },
            n=2,
            m=1)
        atom_5 = self.create_random_motor_atom(add=False)
        atom_5.use_input = True
        atom_5.parameters["time_active"] = 1000
        atom_5.message_delays = [1]
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_4.get_id(),color=graph_colours[atom_4.type])
        self.molecular_graph.add_node(atom_5.get_id(),color=graph_colours[atom_5.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_3.get_id(),atom_4.get_id()),
            (atom_4.get_id(),atom_5.get_id()),
            ])
    def duplicate(self):
        new_molecule = EpuckSampledCamActorMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class EpuckSHCActorMolecule(EpuckActorMolecule):
    """
    The data structure for a EpuckActorMolecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckSHCActorMolecule, self).__init__(memory,atoms,epuck_interface)
        self.epuck_interface = epuck_interface
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        Start with 2 sensors, an Izhikevich and 3 motors
        """
        atom_1 = EpuckFullCameraSensor(memory=self.memory,epuck_interface=self.epuck_interface,
            sensors=[],
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters={
            "time_active":1000
            })
        atom_2 = AveragePixelAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            })
        atom_3 = SumInputAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            })
        atom_4 = SHCLTransAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":1000,
            },
            n=1,
            m=2)
        atom_5 = self.create_random_motor_atom(add=False)
        atom_5.use_input = False
        atom_5.parameters["time_active"] = 1000
        atom_5.message_delays = [1]
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_4.get_id(),color=graph_colours[atom_4.type])
        self.molecular_graph.add_node(atom_5.get_id(),color=graph_colours[atom_5.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_3.get_id(),atom_4.get_id()),
            (atom_4.get_id(),atom_5.get_id()),
            ])

class EpuckTestMolecule(EpuckActorMolecule):
    """
    The data structure for a EpuckActorMolecule
    """
    def __init__(self, memory,atoms,epuck_interface,duplication=False):
        super(EpuckTestMolecule, self).__init__(memory,atoms,epuck_interface)
        self.epuck_interface = epuck_interface
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
        # atom_1.sensors = [0,1]
        atom_1.sensory_conditions = []
        for i in atom_1.sensors:
            end = 1.0
            atom_1.sensory_conditions.append([0.0,end])
        atom_1.activate_with_sensory_condition = True
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
        atom_4 = self.create_random_sensor_atom(add=False)
        print "created random sensor:",atom_1
        atom_4.parameters["time_active"] = 100
        atom_4.sensory_conditions = []
        for i in atom_4.sensors:
            end = 1
            atom_4.sensory_conditions.append([0,end])
        atom_4.activate_with_sensory_condition = True
        atom_5 = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[1],
            n=5,
            parameters={
            "time_active":100
            }
            )
        print "creating motor"
        atom_6 = self.create_random_motor_atom(add=False)
        print "created motor"
        atom_6.use_input = True
        atom_6.parameters["time_active"] = 100
        atom_6.message_delays = [1]
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5,atom_6]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_4.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_5.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_6.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_4.get_id(),atom_5.get_id()),
            (atom_5.get_id(),atom_6.get_id()),
            ])
        print "finished molecule"

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < config.mutation_rate:
            print "adding stm"
            self.create_and_add_stm_group()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_rand_connected_component()
            self.set_connections()

    def create_and_add_stm_group(self):
        sensor = self.create_random_sensor_atom()
        transform = self.create_random_transform_atom()
        motor = self.create_random_motor_atom()
        for n in [sensor,transform,motor]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),transform.get_id())
        self.add_edge(transform.get_id(),motor.get_id())

    def duplicate(self):
        new_molecule = EpuckTestMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        epuck_interface=self.epuck_interface,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

