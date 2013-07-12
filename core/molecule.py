"""
Everything related to a molecule is in here
"""
from .atom import *
import random
import networkx as nx
import pygraphviz as pgv
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import re
import config

graph_colours = {
        "motor":"red",
        "sensory":"blue",
        "transform":"green",
        "game":"purple"
        }

######################
# Base Molecules
######################

class Molecule(object):
    """
    Base class for a Molecule
    """
    def __init__(self,memory,atoms,id=None):
        self.atoms = atoms
        self.molecular_graph = None
        self.active = False
        self.active_hist = False
        self.memory = memory
        self.type = "base"
        self.times_tested = 0
        self.id = ""
        self.fitness = -999999
        self.json = {}

    def act(self):
        self.times_tested += 1
        for atom in sorted([atom for atom in self.get_atoms_as_list()
                        if atom.active is True],
                        key=lambda k:int(re.match('.*-([0-9]+).*',k.get_id()).group(1))):
            if atom.active is True:
                atom.act()
                if atom.type == "sensory" and atom.deactivate_downstream:
                    print "[molecule] deactivating downstream"
                    self.deactivate_downstream(atom)


    def create_id(self,count=None):
        if count == None:
            id = "m-{0}-{1}".format(random.randint(1,50000000),"m")
            while id in self.memory.atoms:
                id = "m-{0}-{1}".format(random.randint(1,50000000),"m")
        else:
            id = "m-{0}".format(count)
        return id

    def get_id(self):
        return self.id

    def set_id(self,id):
        self.id = id

    def constructor(self):
        pass

    def activate(self):
        """
        activate molecule
        """
        self.times_tested += 1
        for atom in self.get_atoms_as_list():
            if atom.type == "sensory" and len(atom.messages) == 0:
                atom.activate()
                # check to see if sensory conditions have been met
                if atom.active:
                    self.active = True
                    self.active_hist = True
        if self.active:
            self.conditional_activate()

    def conditional_activate(self):
        just_activated = []
        for atom in [atom for atom in self.get_atoms_as_list()
                        if atom.active is False]:
            if atom.conditional_activate():
                just_activated.append(atom.get_id())
        while len(just_activated) > 0:
            atom_id = just_activated.pop(0)
            for successor_id in self.molecular_graph.successors(atom_id):
                atom = self.get_atom(successor_id)
                if atom.time_delayed == 0:
                    if atom.conditional_activate():
                        just_activated.append(atom.get_id())

    def set_connections(self):
        """
        takes graph connections between nodes and
        converts them to atom.messages
        """
        for n in self.molecular_graph:
            atom = self.atoms[n]
            connections = self.molecular_graph.predecessors(n)
            atom.messages = connections
            atom.messages = sorted(atom.messages,key=lambda k:int(re.match('.*-([0-9]+).*',k).group(1)))

    def get_atoms_as_list(self):
        atoms = []
        for n in self.molecular_graph:
            atom = self.atoms[n]
            atoms.append(atom)
        return atoms

    def get_atom(self,id):
        return self.memory.get_atom(id)

    def get_connected_components(self,graph):
        ug = graph.to_undirected()
        connected_comps = nx.connected_components(ug)
        return connected_comps

    def get_rand_connected_component(self,connected_components):
        return random.choice(connected_components)

    def duplicate_connected_component_and_add_to_graph(
                            self,
                            parent_graph,
                            connected_component,
                            graph
                            ):
        connected_graph_dict = {}
        original_graph_dict = {}
        # duplicate graph with new atoms. Note: sorted used to keep id ordering
        for node in sorted(connected_component):
            connected_graph_dict[node]={}
            connected_graph_dict[node]["predecessors"]=parent_graph.predecessors(node)
            new_atom = self.get_atom(node).duplicate()
            self.memory.add_atom(new_atom)
            connected_graph_dict[node]["child"] = new_atom.get_id()
            original_graph_dict[new_atom.get_id()]={}
            original_graph_dict[new_atom.get_id()]["parent"]=node
            graph.add_node(new_atom.get_id())
        # add edges
        for node in original_graph_dict.keys():
            parent = original_graph_dict[node]["parent"]
            for p in connected_graph_dict[parent]["predecessors"]:
                graph.add_edge(connected_graph_dict[p]["child"],node)
        self.set_connections()

    def crossover_connected_component(self,parent_graph):
        connected_comp = self.get_rand_connected_component(
                                    self.get_connected_components(parent_graph))
        self.duplicate_connected_component_and_add_to_graph(
                                                parent_graph,
                                                connected_comp,
                                                self.molecular_graph)

    def crossover(self,parent):
        self.crossover_connected_component(parent.molecular_graph)

    def remove_connected_component(self,connected_comp):
        for atom_id in connected_comp:
            self.remove_atom(atom_id)

    def remove_rand_connected_component(self):
        connected_comps = self.get_connected_components(self.molecular_graph)
        if len(connected_comps) > 1:
            connected_comp = self.get_rand_connected_component(connected_comps)
            self.remove_connected_component(connected_comp)

    def deactivate(self):
        self.active = False
        self.active_hist = False
        for atom in self.get_atoms_as_list():
            atom.deactivate(clear=True)

    #########################################################
    # Single point crossover methods currently not being used
    def single_point_crossover(self,other_molecule):
        other_atom = random.choice([atom for atom in other_molecule.get_atoms_as_list()
                                    ]).duplicate()
        print "atom being moved:",other_atom.type
        self.memory.add_atom(other_atom)
        self.replace_with_other_atom(other_atom.get_id())
        self.set_connections()


    def add_other_atom(self,other_atom):
        atom = self.get_atom(other_atom.get_id())
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,atom.can_connect_to())
        parent = random.choice(allowed_connectors)
        self.add_atom_from(other_atom,parent)

    def replace_with_other_atom(self,other_atom):
        matched_atom = None
        for atom in self.get_atoms_as_list():
            if atom.__class__.__name__ == self.get_atom(other_atom).__class__.__name__:
                matched_atom = atom
                break
        if matched_atom is None:
            return
        print "matched_atom:",matched_atom
        self.molecular_graph.add_node(other_atom)
        for p in self.molecular_graph.predecessors(matched_atom.get_id()):
            self.molecular_graph.add_edge(p,other_atom)
        for s in self.molecular_graph.successors(matched_atom.get_id()):
            self.molecular_graph.add_edge(other_atom,s)
        self.molecular_graph.remove_node(matched_atom.get_id())

    def _replace_with_other_atom(self,other_atom):
        atom = self.get_atom(atom_id)
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,atom.can_connect_to())
        parent = random.choice(allowed_connectors)
        self.molecular_graph.add_node(other_atom)
        for p in self.molecular_graph.predecessors(parent):
            self.molecular_graph.add_edge(p,other_atom)
        for s in self.molecular_graph.successors(parent):
            self.molecular_graph.add_edge(other_atom,s)
        self.molecular_graph.remove_node(parent)
    #########################################################

    def mutate(self):
        pass

    def delete_atom(self):
        pass

    def atom_connects_to(self,atom_id):
        return self.get_atom(atom_id).can_connect_to()

    def can_connect_atoms(self,from_atom_id,to_atom_id):
        if (self.memory.get_atom(from_atom_id).type 
            in self.memory.get_atom(to_atom_id).can_connect_to()):
            return True
        else:
            return False
    def add_atom(self,atom_id):
        self.molecular_graph.add_node(atom_id)

    def add_atom_to(self,atom_id,child):
        self.add_atom(atom_id)
        self.molecular_graph.add_edge(atom_id,child)

    def add_atom_from(self,atom_id,parent):
        self.add_atom(atom_id)
        self.add_edge(parent,atom_id)

    def add_edge(self,from_atom_id,to_atom_id):
        if self.can_connect_atoms(from_atom_id,to_atom_id):
            self.molecular_graph.add_edge(from_atom_id,to_atom_id)

    def choose_and_add_edge(self,atom_id):
        atoms = [atom for atom in
        find_atoms_of_types(self.molecular_graph,atom_connects_to(atom_id))
        if atom not in self.molecular_graph.predecessors(atom_id)]
        parent = random.choice(atoms)
        self.add_edge(parent,atom_id)

    def add_random_edge(self):
        child = random.choice(self.molecular_graph.nodes())
        parent = random.choice(self.molecular_graph.nodes())
        count = 0
        while ((parent == child
                or child in self.molecular_graph.successors(parent)
                ) and count < 0):
            child = random.choice(self.molecular_graph.nodes())
            count += 1
        self.add_edge(parent,child)

    def remove_random_edge(self):
        atom = random.choice(self.molecular_graph.nodes())
        ins = self.molecular_graph.predecessors(atom)
        outs = self.molecular_graph.successors(atom)
        count = 0
        while (len(ins) == 0 and len(outs) == 0) and count < 150:
            atom = random.choice(self.molecular_graph.nodes())
            ins = self.molecular_graph.predecessors(atom)
            outs = self.molecular_graph.successors(atom)
            # maybe the graph is very disconnected?
            count += 1
        if (len(ins) == 0 and len(outs) == 0):
            return 0
        if len(ins) > 0 and len(outs) > 0:
            remove_type = random.choice(["ins","outs"])
        elif len(ins) > 0:
            remove_type = "ins"
        else:
            remove_type = "outs"
        if remove_type == "ins":
            ch = random.choice(ins)
            self.molecular_graph.remove_edge(ch,atom)
        else:
            ch = random.choice(outs)
            self.molecular_graph.remove_edge(atom,ch)

    def remove_atom(self,atom_id):
        self.molecular_graph.remove_node(atom_id)
        self.set_connections()

    def remove_random_atom(self):
        if len(self.molecular_graph.nodes()) > 1:
            for atom in self.molecular_graph.nodes():
                if random.random() < config.mutation_rate and len(self.molecular_graph.nodes()) > 1:
                    self.remove_atom(atom)

    def remove_random_atom_of_types(self,types):
        if len(self.find_atoms_of_types(self.molecular_graph,types)) > 1:
            for atom in self.find_atoms_of_types(self.molecular_graph,types):
                if (
                random.random() < 0.1
                and len(self.find_atoms_of_types(self.molecular_graph,types)) > 1):
                    self.remove_atom(atom)

    def find_atoms_of_types(self,graph,types):
        nodes = []
        for node in graph.nodes():
            atom = self.get_atom(node)
            if atom.type in types:
                nodes.append(node)
        return nodes

    def deactivate_downstream(self,start_node):
        atom_id = start_node.get_id()
        start_node.deactivate_downstream = False
        closed_list = [atom_id]
        successors = self.molecular_graph.successors(atom_id)
        open_list = successors
        while len(open_list) > 0:
            node = open_list.pop(0)
            self.get_atom(node).deactivate()
            if node not in closed_list:
                closed_list.append(node)
            open_list += [s for s in self.molecular_graph.successors(node)
                            if (s not in open_list) and (s not in closed_list)]

    def get_random_message_delays(self):
        return random.randint(config.min_message_delay,config.max_message_delay)

    def get_random_time_active(self):
        return random.randint(config.min_time_active,config.max_time_active)

    def get_random_motor_length(self):
        return random.randint(config.min_motors_in_m_atom,
                            config.max_motors_in_m_atom)

    def get_random_sensor_length(self):
        return random.randint(config.min_sensors_in_s_atom,
                            config.max_sensors_in_s_atom)

    def print_graph(self,filename):
        graph = nx.to_agraph(self.molecular_graph)
        for n in graph.nodes():
            try:
                colour = graph_colours[self.get_atom(n)].type
            except:
                colour = 'black'
            graph.get_node(n).attr['color'] = colour
        graph.layout()
        graph.draw('{0}.png'.format(filename))

    def to_json(self):
        self.json["molecular_graph"] = json_graph.dumps(self.molecular_graph)
        self.json["type"] = self.type
        self.json["class"]=self.__class__.__name__
        self.json["atoms"] = [a.get_json() for a in self.get_atoms_as_list()]

    def get_json(self):
        self.to_json()
        return self.json

    def duplicate_graph(self,new_molecule):
        graph_dict = {}
        new_graph_dict = {}
        new_graph = nx.DiGraph()
        # duplicate graph with new atoms. Note: sorted used to keep id ordering
        for node in sorted(self.molecular_graph.nodes()):
            graph_dict[node]={}
            graph_dict[node]["predecessors"]=self.molecular_graph.predecessors(node)
            new_atom = self.get_atom(node).duplicate()
            self.memory.add_atom(new_atom)
            graph_dict[node]["child"] = new_atom.get_id()
            new_graph_dict[new_atom.get_id()] = {}
            new_graph_dict[new_atom.get_id()]["parent"] = node
            new_graph.add_node(new_atom.get_id())
        # add edges
        for node in new_graph.nodes():
            parent = new_graph_dict[node]["parent"]
            for p in self.molecular_graph.predecessors(parent):
                new_graph.add_edge(graph_dict[p]["child"],node)
        new_molecule.molecular_graph = new_graph

    def set_up_new_molecule(self,new_molecule):
        self.duplicate_graph(new_molecule)
        new_molecule.set_connections()

    def __str__(self):
        # long oneliner!
        return " - ".join(
            ["[id:{0} active:{1} type:{2}]".format(
                self.atoms[a].id,self.atoms[a].active,self.atoms[a].type)
             for a in self.molecular_graph.nodes()
            ])


class GameMolecule(Molecule):
    """
    The data structure for a game molecule
    """
    def __init__(self,*args):
        super(GameMolecule, self).__init__(*args)
        self.type = "game"
        self.game_atoms = []

    def create_id(self,count=None):
        if count == None:
            id = "gm-{0}-{1}".format(random.randint(1,50000000),"m")
            while id in self.memory.atoms:
                id = "gm-{0}-{1}".format(random.randint(1,50000000),"m")
        else:
            id = "gm-{0}".format(count)
        return id

    def activate(self):
        """
        activate molecule
        """
        self.times_tested += 1
        for atom in self.get_atoms_as_list():
            if atom.type == "sensory" and len(atom.messages) == 0:
                atom.activate()
                # check to see if sensory conditions have been met
                if atom.active:
                    self.active = True
                    self.active_hist = True
        if self.active:
            self.conditional_activate()

    def get_fitness(self):
        fitness = -999999
        for game in [a for a in self.get_atoms_as_list()
                        if a.type =="game"]:
            fitness = game.get_fitness()
        return fitness

    def get_state_history(self):
        for game in [a for a in self.get_atoms_as_list()
                        if a.type =="game"]:
            state = game.state
        return state

    def deactivate(self):
        for game in [a for a in self.get_atoms_as_list()
                        if a.type =="game"]:
            if game is not None:
                game.state = []
        Molecule.deactivate(self)

    def set_up_new_molecule(self,new_molecule):
        self.duplicate_graph(new_molecule)
        new_molecule.set_connections()
        new_molecule.game_atoms = []

class ActorMolecule(Molecule):
    """
    The data structure for an actor molecule
    """
    def __init__(self,*args):
        super(ActorMolecule, self).__init__(*args)
        self.type = "actor_molecule"

    def create_id(self,count=None):
        if count == None:
            id = "am-{0}-{1}".format(random.randint(1,50000000),"m")
            while id in self.memory.atoms:
                id = "am-{0}-{1}".format(random.randint(1,50000000),"m")
        else:
            id = "am-{0}".format(count)
        return id

    def activate(self):
        """
        activate molecule
        """
        self.times_tested += 1
        for atom in self.get_atoms_as_list():
            if atom.type == "sensory" and len(atom.messages) == 0:
                atom.activate()
                # check to see if sensory conditions have been met
                if atom.active:
                    self.active = True
                    self.active_hist = True
        if self.active:
            self.conditional_activate()

    def deactivate(self):
        for atom in self.get_atoms_as_list():
            atom.deactivate(clear=True)

