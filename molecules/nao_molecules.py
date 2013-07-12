######################
# Nao Molecules
######################
from core.molecule import *
from atoms.input_atoms import *
from atoms.game_atoms import *
from atoms.transform_atoms import *
from atoms.nao_atoms import *
class NaoMaxSensorGameMolecule(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,nao_memory,sensors=None,duplication=False):
        super(NaoMaxSensorGameMolecule, self).__init__(memory,atoms)
        self.nao_memory = nao_memory
        self.id = self.create_id()
        if sensors==None:
            self.sensors=[143]
        else:
            self.sensors=sensors
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = NaoSensorAtom(
            memory=self.memory,
            nao_memory=self.nao_memory,
            sensors=self.sensors,
            sensory_conditions=[-10000.0],
            messages=[],
            message_delays=[0],
            parameters = {
            "time_active":"always",
            })
        atom_2 = TransformAtom(
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


    def create_and_add_atom(self):
        atom = self.create_random_sensor_atom()
        for node in self.molecular_graph.nodes():
            if self.get_atom(node).type == "transform":
                connecting_atom = node
                break
        self.add_atom_to(atom.get_id(),connecting_atom)
        self.set_connections()

    def get_random_sensors(self,nao_memory,n_sensors):
        sensors = []
        for i in range(0,n_sensors):
            sensor = nao_memory.getRandomSensor()
            while sensor in sensors:
                sensor = nao_memory.getRandomSensor()
            sensors.append(sensor)
        return sensors

    def create_random_sensor_atom(self,add=True):
        no_sensors = random.randint(1,3)
        atom = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=self.get_random_sensors(self.nao_memory,no_sensors),
            sensory_conditions=[-10000.0 for s in range(0,no_sensors)],
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            })
        if add:
            self.memory.add_atom(atom)
        return atom

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            if atom.type in ["sensory"]:
                atom.mutate(0.25)
            if atom.type == "transform":
                atom.mutate(large=True)
        if random.random() < 0.25:
            self.create_and_add_atom()
        self.remove_random_atom_of_types("sensory")
        self.set_connections()

    def duplicate(self):
        new_molecule = NaoMaxSensorGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        sensors=self.sensors,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class NaoMaxDistanceGameMolecule(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,nao_memory,sensors=None,duplication=False):
        super(NaoMaxDistanceGameMolecule, self).__init__(memory,atoms)
        self.nao_memory = nao_memory
        self.id = self.create_id()
        if sensors==None:
            self.sensors=[200,202]
        else:
            self.sensors=sensors
        if duplication == False:
            self.constructor()
            self.set_connections()

    def constructor(self):
        atom_1 = NaoSensorAtom(
            memory=self.memory,
            nao_memory=self.nao_memory,
            sensors=[200,202],
            sensory_conditions=[-100000.0],
            messages=[],
            message_delays=[0],
            parameters = {
            "time_active":"always",
            })
        atom_2 = TransformAtom(
            memory=self.memory,
            messages=[],
            message_delays=[1],
            parameters = {
            "time_active":"always",
            })
        atom_3 = DistanceGameAtom(
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


    def create_and_add_atom(self):
        atom = self.create_random_sensor_atom()
        for node in self.molecular_graph.nodes():
            if self.get_atom(node).type == "transform":
                connecting_atom = node
                break
        self.add_atom_to(atom.get_id(),connecting_atom)
        self.set_connections()

    def get_random_sensors(self,nao_memory,n_sensors):
        sensors = []
        for i in range(0,n_sensors):
            sensor = nao_memory.getRandomSensor()
            while sensor in sensors:
                sensor = nao_memory.getRandomSensor()
            sensors.append(sensor)
        return sensors

    def create_random_sensor_atom(self,add=True):
        no_sensors = random.randint(1,3)
        atom = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=self.get_random_sensors(self.nao_memory,no_sensors),
            sensory_conditions=[-10000.0 for s in range(0,no_sensors)],
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            })
        if add:
            self.memory.add_atom(atom)
        return atom

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            if atom.type in ["sensory"]:
                atom.mutate(0.25)
            if atom.type == "transform":
                atom.mutate(large=True)
        if random.random() < 0.25:
            self.create_and_add_atom()
        self.remove_random_atom_of_types("sensory")
        self.set_connections()

    def duplicate(self):
        new_molecule = NaoMaxDistanceGameMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        sensors=self.sensors,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class NAOActorMolecule(ActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(NAOActorMolecule, self).__init__(memory,atoms)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        Start with 2 sensors, an Izhikevich and 3 motors
        """
        atom_1 = self.create_random_sensor_atom(add=False)
        atom_2 = self.create_random_sensor_atom(add=False)
        atom_3 = IzhikevichTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters = {
            "time_active":1000
            },
            assign_inputs_to_neurons=[[random.sample(range(100), 5)] for i in range(0,10)],
            weight_spikes=[[random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)]],
            no_outputs=5)
        atom_4 = self.create_random_motor_atom(add=False)
        atom_5 = self.create_random_motor_atom(add=False)
        atom_6 = self.create_random_motor_atom(add=False)
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5,atom_6]:
            self.memory.add_atom(a)
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_4.get_id(),color=graph_colours[atom_4.type])
        self.molecular_graph.add_node(atom_5.get_id(),color=graph_colours[atom_5.type])
        self.molecular_graph.add_node(atom_6.get_id(),color=graph_colours[atom_6.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_3.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_3.get_id(),atom_4.get_id()),
            (atom_3.get_id(),atom_5.get_id()),
            (atom_3.get_id(),atom_6.get_id()),
            ])

    def get_random_motors(self,nao_memory,n_motors):
        motors = []
        for i in range(0,n_motors):
            motor = nao_memory.getRandomMotor()
            while motor in motors:
                motor = nao_memory.getRandomMotor()
            motors.append(motor)
        return motors

    def get_random_sensors(self,nao_memory,n_sensors):
        sensors = []
        for i in range(0,n_sensors):
            sensor = nao_memory.getRandomSensor()
            while sensor in sensors:
                sensor = nao_memory.getRandomSensor()
            sensors.append(sensor)
        return sensors

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < config.mutation_rate:
            self.create_and_add_atom()
        if random.random() < 0.025:
            self.create_and_add_stm_group()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.add_random_edge()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_random_edge()
            self.set_connections()
        self.remove_random_atom()
        self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_rand_connected_component()
            self.set_connections()

    def create_random_motor_atom(self,add=True):
        no_motors = self.get_random_motor_length()
        atom = NaoMotorAtom(
            memory=self.memory,
            nao_memory=self.nao_memory,
            nao_motion=self.nao_motion,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            motors = self.get_random_motors(self.nao_memory,no_motors),
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
            atom = self.create_random_motor_atom()
        elif a_type == "sensory":
            atom = self.create_random_sensor_atom()
        elif a_type == "transform":
            atom = self.create_random_transform_atom()
        connecting_atom = random.choice(self.molecular_graph.nodes())
        if random.random() < 0.5:
            self.add_atom_from(atom.get_id(),connecting_atom)
        else:
            self.add_atom_to(atom.get_id(),connecting_atom)
        self.set_connections()

    def create_random_sensor_atom(self,add=True):
        no_sensors = self.get_random_sensor_length()
        atom = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=self.get_random_sensors(self.nao_memory,no_sensors),
            sensory_conditions=[],
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            })
        for i in atom.sensors:
            start = random.uniform(0,0.5)
            end = random.uniform(0.5,1)
            atom.sensory_conditions.append([start,end])
        atom.activate_with_sensory_condition=True
        atom.deactivate_with_sensory_condition=True
        if add:
            self.memory.add_atom(atom)
        return atom
    # TODO:
    # add creation information to individual atom classes
    def create_random_transform_atom(self):
        atom_to_create = random.choice(["linear",
                                        "euclidian",
                                        "pca",
                                        # "lwpr",
                                        "k_means_class",
                                        "izhikevich"
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
                    no_outputs=5)
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

    def duplicate(self):
        new_molecule = NAOActorMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class SMMActorMolecule(NAOActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(SMMActorMolecule, self).__init__(memory,atoms,nao_memory,nao_motion,duplication=True)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        50% of the time use a SMM, 50% use a LinearTransformAtom
        """
        if random.random() < 0.5:
            atom_1 = self.create_random_sensor_atom(add=False)
            atom_1.sensors = []
            message_delays = self.get_random_message_delays()
            atom_2 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,use_input=False,add=False)
            atom_3 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,motors=copy.deepcopy(atom_2.motors),use_input=False,add=False)

        else:
            atom_1 = self.create_random_sensor_atom(add=False)
            atom_2 = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
            atom_3 = self.create_random_motor_atom(add=False)
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

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < config.mutation_rate:
            if random.random() < 0.5:
                self.create_and_add_stm_group()
                self.set_connections()
            else:
                self.create_and_add_smm_group()
                self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_rand_connected_component()
            self.set_connections()

    def create_random_motor_atom(self,use_input=True,message_delays=None,time_active=None,motors=None,add=True):
        if message_delays == None:
            message_delays = self.get_random_message_delays()
        if time_active == None:
            time_active = self.get_random_time_active()
        if motors == None:
            no_motors = self.get_random_motor_length()
            motors = self.get_random_motors(self.nao_memory,no_motors)
        else:
            motors = motors
            no_motors = len(motors)
        atom = NaoMotorAtom(
            memory=self.memory,
            nao_memory=self.nao_memory,
            nao_motion=self.nao_motion,
            messages=[],
            message_delays=[message_delays],
            motors = motors,
            parameters = {
            "time_active":time_active,
            "motor_parameters":[2*(random.random()-0.5)
                                for i in range(0,no_motors)],
            "times":[1, 1, 1]
            },
            use_input=use_input)
        if add:
            self.memory.add_atom(atom)
        return atom

    def create_random_transform_atom(self):
        random_number = random.random()
        if random_number < 0.5:
            atom = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        else:
            atom = KMeansClassifyAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                K=random.randint(1,5),
                parameters={
                "time_active":self.get_random_time_active()
                },
                )
        self.memory.add_atom(atom)
        return atom

    def create_and_add_stm_group(self,disjoint=True):
        sensor = self.create_random_sensor_atom()
        transform = self.create_random_transform_atom()
        motor = self.create_random_motor_atom()
        if disjoint == False:
            allowed_connectors = self.find_atoms_of_types(
                                                    self.molecular_graph,
                                                    sensor.can_connect_to()
                                                    )
            parent = random.choice(allowed_connectors)
        for n in [sensor,transform,motor]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),transform.get_id())
        self.add_edge(transform.get_id(),motor.get_id())
        if disjoint == False:
            self.add_atom_from(sensor.get_id(),parent=parent)

    def create_and_add_smm_group(self,disjoint=True):
        sensor = self.create_random_sensor_atom()
        sensor.sensors = []
        message_delays = random.randint(3,int(config.max_message_delay/3))
        motor_1 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,use_input=False)
        motor_2 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,motors=copy.deepcopy(motor_1.motors),use_input=False)
        if disjoint == False:
            allowed_connectors = self.find_atoms_of_types(
                                            self.molecular_graph,
                                            sensor.can_connect_to()
                                            )
            parent = random.choice(allowed_connectors)
        for n in [sensor,motor_1,motor_2]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),motor_1.get_id())
        self.add_edge(motor_1.get_id(),motor_2.get_id())
        if disjoint == False:
            self.add_atom_from(sensor.get_id(),parent=parent)

    def duplicate(self):
        new_molecule = SMMActorMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class IzhiDistanceMovingMolecule(NAOActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(IzhiDistanceMovingMolecule, self).__init__(memory,atoms,nao_memory,nao_motion,duplication=False)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        50% chance of izhikevich, 50% LinearTransformAtom
        """
        atom_1 = self.create_random_sensor_atom(add=False)
        if random.random() < 0.5:
            atom_2 = IzhikevichTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                parameters = {
                "time_active":self.get_random_time_active()
                },
                assign_inputs_to_neurons=[[random.sample(range(100), 5)] for i in range(0,10)],
                weight_spikes=[[random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)]],
                no_outputs=5)
        else:
            atom_2 = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        atom_3 = self.create_random_motor_atom(add=False)
        atom_3.parameters["time_active"] = 50
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

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
    def create_random_transform_atom(self):
        random_number = random.random()
        if random_number < 0.5:
            atom = IzhikevichTransformAtom(memory=self.memory,messages=[],message_delays=[1],
                    parameters = {
                    "time_active":1000
                    },
                    assign_inputs_to_neurons=[
                    [random.sample(range(100), 5)] for i in range(0,10)],
                    weight_spikes=[[random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)],
                    [random.random()-0.5 for x in range(0, 5)]],
                    no_outputs=5)
        elif random_number >= 0.5 and random_number < 0.75:
            atom = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        else:
            atom = KMeansClassifyAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                K=random.randint(1,5),
                parameters={
                "time_active":self.get_random_time_active()
                },
                )
        self.memory.add_atom(atom)
        return atom

    def create_and_add_stm_group(self,disjoint=True):
        sensor = self.create_random_sensor_atom()
        transform = self.create_random_transform_atom()
        motor = self.create_random_motor_atom()
        motor.parameters["time_active"] = random.randint(30,config.max_time_active)
        if disjoint == False:
            allowed_connectors = self.find_atoms_of_types(
                                                    self.molecular_graph,
                                                    sensor.can_connect_to()
                                                    )
            parent = random.choice(allowed_connectors)
        for n in [sensor,transform,motor]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),transform.get_id())
        self.add_edge(transform.get_id(),motor.get_id())
        if disjoint == False:
            self.add_atom_from(sensor.get_id(),parent=parent)
    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < config.mutation_rate:
            self.create_and_add_stm_group()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_rand_connected_component()
            self.set_connections()

    def duplicate(self):
        new_molecule = IzhiDistanceMovingMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class IzhiSMMMolecule(NAOActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(IzhiSMMMolecule, self).__init__(memory,atoms,nao_memory,nao_motion,duplication=False)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        50% chance of izhikevich, 50% LinearTransformAtom
        """
        if random.random() < 0.5:
            atom_1 = self.create_random_sensor_atom(add=False)
            atom_2 = IzhikevichTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                parameters = {
                "time_active":30
                },
                assign_inputs_to_neurons=[[random.sample(range(100), 5)] for i in range(0,10)],
                weight_spikes=[[random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)],
                [random.random()-0.5 for x in range(0, 5)]],
                no_outputs=5)
            atom_3 = self.create_random_motor_atom(add=False)
            atom_3.parameters["time_active"] = 50
        else:
            atom_1 = self.create_random_sensor_atom(add=False)
            atom_1.sensors = []
            message_delays = random.randint(1,int(config.max_message_delay/3))
            atom_2 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,use_input=False,add=False)
            atom_3 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,motors=copy.deepcopy(atom_2.motors),use_input=False,add=False)
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

    def create_random_motor_atom(self,use_input=True,message_delays=None,time_active=None,motors=None,add=True):
        if message_delays == None:
            message_delays = self.get_random_message_delays()
        if time_active == None:
            time_active = self.get_random_time_active()
        if motors == None:
            no_motors = self.get_random_motor_length()
            motors = self.get_random_motors(self.nao_memory,no_motors)
        else:
            motors = motors
            no_motors = len(motors)
        atom = NaoMotorAtom(
            memory=self.memory,
            nao_memory=self.nao_memory,
            nao_motion=self.nao_motion,
            messages=[],
            message_delays=[message_delays],
            motors = motors,
            parameters = {
            "time_active":time_active,
            "motor_parameters":[2*(random.random()-0.5)
                                for i in range(0,no_motors)],
            "times":[1, 1, 1]
            },
            use_input=use_input)
        if add:
            self.memory.add_atom(atom)
        return atom
    def create_random_transform_atom(self):
        random_number = random.random()
        if random_number < 0.5:
            atom = IzhikevichTransformAtom(memory=self.memory,messages=[],message_delays=[1],
                    parameters = {
                    "time_active":30
                    },
                    assign_inputs_to_neurons=[
                    [random.sample(range(100), 5)] for i in range(0,10)],
                    weight_spikes=[[random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)],
                    [random.random()-0.5 for x in range(0, 5)]],
                    no_outputs=5)
        elif random_number >= 0.75 and random_number < 0.85:
            atom = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        else:
            atom = KMeansClassifyAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                K=random.randint(1,5),
                parameters={
                "time_active":self.get_random_time_active()
                },
                )
        self.memory.add_atom(atom)
        return atom

    def create_and_add_stm_group(self,disjoint=True):
        sensor = self.create_random_sensor_atom()
        transform = self.create_random_transform_atom()
        motor = self.create_random_motor_atom()
        if transform.__class__.__name__ == "IzhikevichTransformAtom":
            motor.parameters["time_active"] = random.randint(30,config.max_time_active)
        if disjoint == False:
            allowed_connectors = self.find_atoms_of_types(
                                                    self.molecular_graph,
                                                    sensor.can_connect_to()
                                                    )
            parent = random.choice(allowed_connectors)
        for n in [sensor,transform,motor]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),transform.get_id())
        self.add_edge(transform.get_id(),motor.get_id())
        if disjoint == False:
            self.add_atom_from(sensor.get_id(),parent=parent)

    def create_and_add_smm_group(self,disjoint=True):
        sensor = self.create_random_sensor_atom()
        sensor.sensors = []
        message_delays = random.randint(1,int(config.max_message_delay/3))
        motor_1 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,use_input=False)
        motor_2 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,motors=copy.deepcopy(motor_1.motors),use_input=False)
        if disjoint == False:
            allowed_connectors = self.find_atoms_of_types(
                                            self.molecular_graph,
                                            sensor.can_connect_to()
                                            )
            parent = random.choice(allowed_connectors)
        for n in [sensor,motor_1,motor_2]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),motor_1.get_id())
        self.add_edge(motor_1.get_id(),motor_2.get_id())
        if disjoint == False:
            self.add_atom_from(sensor.get_id(),parent=parent)

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < config.mutation_rate:
            if random.random() < 0.5:
                self.create_and_add_stm_group()
                self.set_connections()
            else:
                self.create_and_add_smm_group()
                self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_rand_connected_component()
            self.set_connections()

    def duplicate(self):
        new_molecule = IzhiSMMMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class OSCMolecule(NAOActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(OSCMolecule, self).__init__(memory,atoms,nao_memory,nao_motion,duplication=False)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        50% chance of izhikevich, 50% LinearTransformAtom
        """
        atom_1 = self.create_random_sensor_atom(add=False)
        atom_1.sensors = []
        atom_1.sensory_conditions = []
        atom_1.activate_with_sensory_condition=False
        atom_1.deactivate_with_sensory_condition=False
        atom_2 = self.create_random_osc_atom(add=False)
        atom_3 = self.create_random_transform_atom(add=False)
        atom_4 = self.create_random_motor_atom(add=False)
        atom_5 = self.create_random_osc_atom(add=False)
        atom_6 = self.create_random_transform_atom(add=False)
        atom_7 = self.create_random_motor_atom(add=False)
        atom_8 = self.create_random_osc_atom(add=False)
        atom_9 = self.create_random_transform_atom(add=False)
        atom_10 = self.create_random_motor_atom(add=False)
        self.molecular_graph = nx.DiGraph()
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5,atom_6,atom_7,atom_8,atom_9,atom_10]:
            a.parameters["time_active"] = 30
            self.memory.add_atom(a)
            self.molecular_graph.add_node(a.get_id())
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_3.get_id(),atom_4.get_id()),
            (atom_1.get_id(),atom_5.get_id()),
            (atom_5.get_id(),atom_6.get_id()),
            (atom_6.get_id(),atom_7.get_id()),
            (atom_1.get_id(),atom_8.get_id()),
            (atom_8.get_id(),atom_9.get_id()),
            (atom_9.get_id(),atom_10.get_id()),
            ])

    def create_random_motor_atom(self,use_input=True,message_delays=None,time_active=None,motors=None,add=True):
        if message_delays == None:
            message_delays = self.get_random_message_delays()
        if time_active == None:
            time_active = self.get_random_time_active()
        if motors == None:
            no_motors = self.get_random_motor_length()
            motors = self.get_random_motors(self.nao_memory,no_motors)
        else:
            motors = motors
            no_motors = len(motors)
        atom = NaoMotorAtom(
            memory=self.memory,
            nao_memory=self.nao_memory,
            nao_motion=self.nao_motion,
            messages=[],
            message_delays=[message_delays],
            motors = motors,
            parameters = {
            "time_active":time_active,
            "motor_parameters":[2*(random.random()-0.5)
                                for i in range(0,no_motors)],
            "times":[1, 1, 1]
            },
            use_input=use_input)
        if add:
            self.memory.add_atom(atom)
        return atom
    def create_random_transform_atom(self,add=True):
        atom = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            n=5,
            parameters={
            "time_active":self.get_random_time_active()
            }
            )
        if add:
            self.memory.add_atom(atom)
        return atom

    def create_random_osc_atom(self,add=True):
        atom = OscillatorAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            },
            speed = random.uniform(0.5,5),
            no_outputs = random.randint()
            )
        if add:
            self.memory.add_atom(atom)
        return atom

    def create_and_add_otm_group(self,disjoint=True):
        sensor = self.create_random_osc_atom()
        sensor.sensors = []
        message_delays = random.randint(1,int(config.max_message_delay/3))
        motor_1 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,use_input=False)
        motor_2 = self.create_random_motor_atom(message_delays=message_delays,time_active=message_delays,motors=copy.deepcopy(motor_1.motors),use_input=False)
        if disjoint == False:
            allowed_connectors = self.find_atoms_of_types(
                                            self.molecular_graph,
                                            sensor.can_connect_to()
                                            )
            parent = random.choice(allowed_connectors)
        for n in [sensor,motor_1,motor_2]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),motor_1.get_id())
        self.add_edge(motor_1.get_id(),motor_2.get_id())
        if disjoint == False:
            self.add_atom_from(sensor.get_id(),parent=parent)

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()

    def duplicate(self):
        new_molecule = OSCMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class FernandoMolecule(NAOActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(FernandoMolecule, self).__init__(memory,atoms,nao_memory,nao_motion,duplication=False)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        """
        50% chance of izhikevich, 50% LinearTransformAtom
        """
        atom_1 = self.create_random_sensor_atom(add=False)
        atom_2 = IzhikevichTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters = {
            "time_active":self.get_random_time_active()
            },
            assign_inputs_to_neurons=[[random.sample(range(100), 5)] for i in range(0,10)],
            weight_spikes=[[random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)]],
            no_outputs=5)
        atom_3 = self.create_random_motor_atom(add=False)
        #LTM
        atom_4 = self.create_random_sensor_atom(add=False)
        atom_5 = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            n=5,
            parameters={
            "time_active":self.get_random_time_active()
            }
            )
        atom_6 = self.create_random_motor_atom(add=False)
        atom_7 = self.create_random_sensor_atom(add=False)
        atom_8 = OscillatorAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            },
            speed = random.uniform(0.5,5),
            no_outputs = random.randint(1,5)
            )
        atom_9 = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            n=5,
            parameters={
            "time_active":self.get_random_time_active()
            }
            )
        atom_10 = self.create_random_motor_atom(add=False)
        self.molecular_graph = nx.DiGraph()
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5,atom_6,atom_7,atom_8,atom_9,atom_10]:
            self.memory.add_atom(a)
            self.molecular_graph.add_node(a.get_id())
        self.molecular_graph.add_edges_from([
            # Izhi
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            # LTM
            (atom_4.get_id(),atom_5.get_id()),
            (atom_5.get_id(),atom_6.get_id()),
            # OSC
            (atom_7.get_id(),atom_8.get_id()),
            (atom_8.get_id(),atom_9.get_id()),
            (atom_9.get_id(),atom_10.get_id()),
            ])

    def create_and_add_SIzhM(self):
        atom_1 = self.create_random_sensor_atom()
        atom_2 = IzhikevichTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters = {
            "time_active":self.get_random_time_active()
            },
            assign_inputs_to_neurons=[[random.sample(range(100), 5)] for i in range(0,10)],
            weight_spikes=[[random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)]],
            no_outputs=5)
        self.memory.add_atom(atom_2)
        atom_3 = self.create_random_motor_atom()
        for n in [atom_1,atom_2,atom_3]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(atom_1.get_id(),atom_2.get_id())
        self.add_edge(atom_2.get_id(),atom_3.get_id())

    def create_and_add_SLtM(self):
        atom_1 = self.create_random_sensor_atom()

        atom_2 = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        self.memory.add_atom(atom_2)
        atom_3 = self.create_random_motor_atom()
        for n in [atom_1,atom_2,atom_3]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(atom_1.get_id(),atom_2.get_id())
        self.add_edge(atom_2.get_id(),atom_3.get_id())

    def create_and_add_OSLtM(self):
        atom_1 = self.create_random_sensor_atom()
        atom_2 = OscillatorAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            },
            speed = random.uniform(0.5,5),
            no_outputs = random.randint(1,5)
            )
        self.memory.add_atom(atom_2)
        atom_3 = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        self.memory.add_atom(atom_3)
        atom_4 = self.create_random_motor_atom()
        for n in [atom_1,atom_2,atom_3,atom_4]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(atom_1.get_id(),atom_2.get_id())
        self.add_edge(atom_2.get_id(),atom_3.get_id())
        self.add_edge(atom_3.get_id(),atom_4.get_id())

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < config.mutation_rate:
            rn = random.random()
            if rn < 0.33:
                self.create_and_add_SIzhM()
            elif rn >= 0.33 and rn < 0.66:
                self.create_and_add_SLtM()
            else:
                self.create_and_add_OSLtM()
            self.set_connections()
        if random.random() < (0.01 * len(self.get_connected_components(self.molecular_graph))):
            self.remove_rand_connected_component()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.add_random_edge()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_random_edge()
            self.set_connections()

    def duplicate(self):
        new_molecule = FernandoMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule

class SHCLtMolecule(NAOActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(SHCLtMolecule, self).__init__(memory,atoms,nao_memory,nao_motion,duplication=False)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        self.id = self.create_id()

    def constructor(self):
        atom_1 = self.create_random_sensor_atom(add=False)
        atom_2 = IzhikevichTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters = {
            "time_active":self.get_random_time_active()
            },
            assign_inputs_to_neurons=[[random.sample(range(100), 5)] for i in range(0,10)],
            weight_spikes=[[random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)]],
            no_outputs=5)
        atom_3 = self.create_random_motor_atom(add=False)
        atom_4 = self.create_random_sensor_atom(add=False)
        atom_5 = SHCLtInternalSensor(
            memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            n=5,
            parameters={
            "time_active":self.get_random_time_active()
            },
            function="max",
            sensors = [143],
            nao_memory=self.nao_memory
            )
        atom_6 = self.create_random_motor_atom(add=False)
        atom_7 = self.create_random_sensor_atom(add=False)
        atom_8 = OscillatorAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            },
            speed = random.uniform(0.5,5),
            no_outputs = random.randint(1,5)
            )
        atom_9 = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            n=5,
            parameters={
            "time_active":self.get_random_time_active()
            }
            )
        atom_10 = self.create_random_motor_atom(add=False)
        self.molecular_graph = nx.DiGraph()
        for a in [atom_1,atom_2,atom_3,
        atom_4,atom_5,atom_6,atom_7,atom_8,atom_9,atom_10
        ]:
            self.memory.add_atom(a)
            self.molecular_graph.add_node(a.get_id())
        self.molecular_graph.add_edges_from([
            # Izhi
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            # # LSTM
            (atom_4.get_id(),atom_5.get_id()),
            (atom_5.get_id(),atom_6.get_id()),
            # # OSC
            (atom_7.get_id(),atom_8.get_id()),
            (atom_8.get_id(),atom_9.get_id()),
            (atom_9.get_id(),atom_10.get_id()),
            ])

    def create_and_add_SIzhM(self):
        atom_1 = self.create_random_sensor_atom()
        atom_2 = IzhikevichTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters = {
            "time_active":self.get_random_time_active()
            },
            assign_inputs_to_neurons=[[random.sample(range(100), 5)] for i in range(0,10)],
            weight_spikes=[[random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)],
            [random.random()-0.5 for x in range(0, 5)]],
            no_outputs=5)
        self.memory.add_atom(atom_2)
        atom_3 = self.create_random_motor_atom()
        for n in [atom_1,atom_2,atom_3]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(atom_1.get_id(),atom_2.get_id())
        self.add_edge(atom_2.get_id(),atom_3.get_id())

    def create_and_add_SSHCLtM(self):
        atom_1 = self.create_random_sensor_atom()

        atom_2 = SHCLtInternalSensor(
            memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            n=5,
            parameters={
            "time_active":self.get_random_time_active()
            },
            function="max",
            sensors = [143],
            nao_memory=self.nao_memory
            )
        self.memory.add_atom(atom_2)
        atom_3 = self.create_random_motor_atom()
        for n in [atom_1,atom_2,atom_3]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(atom_1.get_id(),atom_2.get_id())
        self.add_edge(atom_2.get_id(),atom_3.get_id())

    def create_and_add_SLtM(self):
        atom_1 = self.create_random_sensor_atom()

        atom_2 = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        self.memory.add_atom(atom_2)
        atom_3 = self.create_random_motor_atom()
        for n in [atom_1,atom_2,atom_3]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(atom_1.get_id(),atom_2.get_id())
        self.add_edge(atom_2.get_id(),atom_3.get_id())

    def create_and_add_OSLtM(self):
        atom_1 = self.create_random_sensor_atom()
        atom_2 = OscillatorAtom(memory=self.memory,
            messages=[],
            message_delays=[self.get_random_message_delays()],
            parameters={
            "time_active":self.get_random_time_active()
            },
            speed = random.uniform(0.5,5),
            no_outputs = random.randint(1,5)
            )
        self.memory.add_atom(atom_2)
        atom_3 = LinearTransformAtom(memory=self.memory,
                messages=[],
                message_delays=[self.get_random_message_delays()],
                n=5,
                parameters={
                "time_active":self.get_random_time_active()
                }
                )
        self.memory.add_atom(atom_3)
        atom_4 = self.create_random_motor_atom()
        for n in [atom_1,atom_2,atom_3,atom_4]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(atom_1.get_id(),atom_2.get_id())
        self.add_edge(atom_2.get_id(),atom_3.get_id())
        self.add_edge(atom_3.get_id(),atom_4.get_id())

    def mutate(self):
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < config.mutation_rate:
            rn = random.random()
            if rn < 0.25:
                self.create_and_add_SIzhM()
            elif rn >= 0.25 and rn < 0.50:
                self.create_and_add_SLtM()
            elif rn >= 0.50 and rn < 0.75:
                self.create_and_add_SSHCLtM()
            else:
                self.create_and_add_OSLtM()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_rand_connected_component()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.add_random_edge()
            self.set_connections()
        if random.random() < config.mutation_rate:
            self.remove_random_edge()
            self.set_connections()

    def duplicate(self):
        new_molecule = SHCLtMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        self.set_up_new_molecule(new_molecule)
        return new_molecule



