import os,sys,time,random,numpy
from naoqi import *
from robots.nao_functions import *
from core.molecule import *
from molecules.nao_molecules import *
from core.memory import Messages
import networkx as nx
import pygraphviz as pgv
from networkx.readwrite import json_graph
import config
from experiments_and_search.utilities import WeightedRandomizer, save_population, save_archive, plot_fitness, drawMol, load_json_atom
from experiments_and_search.ga import IslandGA
# makes sure we save all array data
numpy.set_printoptions(threshold=numpy.nan)

class NaoIslandGA(IslandGA):
    def __init__(self,games_array,memory,nao_mem,nao_motion,init_molecules):
        super(NaoIslandGA,self).__init__(games_array,memory)
        self.nao_mem = nao_mem
        self.nao_motion = nao_motion
        self.setup_islands(init_molecules)

    def setup_islands(self,molecules):
        self.islands = []
        for island in self.games:
            population = []
            for molecule in molecules:
                self.memory.add_molecule(molecule)
                population.append(molecule)
            self.islands.append(population)
    def assess_fitness(self,individual,game):
        """
        This is the fitness function used to evaluate actors
        on a specific game
        """
        if config.use_distance:
            self.nao_mem.reset_gps_position()
        individual.activate()
        game.activate()
        sleep(0.5)
        self.nao_motion.rest()
        sleep(0.5)
        for t in range(0,config.time_steps_per_evaluation):
            if config.use_sensory_conditions:
                individual.activate()
            individual.act()
            individual.conditional_activate()
            game.act()
            game.conditional_activate()
            sleep(config.time_step_length)
            if config.draw_molecules:
                drawMol(individual.molecular_graph,self.memory,node_labels="values")
        individual.fitness = game.get_fitness()
        print "fitness:",individual.fitness
        game.deactivate()
        individual.deactivate()

class NaoGAUtil():
    def __init__(self,memory,nao_mem,nao_motion):
        self.memory = memory
        self.nao_mem = nao_mem
        self.nao_motion = nao_motion

    def load_brain_archive(self):
        largest_atom_id = 0
        last_atom_id = 0
        base = "brain_archive/{0}/".format(config.robot_system)
        if not os.path.exists(base): os.makedirs(base)
        files = [o for o in os.listdir(base) if re.match('.*\.json',o)]
        for f in files:
            print f
            json_file = open("{0}{1}".format(base,f),"r")
            json_dict = eval(json_file.read())
            json_file.close()
            id_map = {}
            molecule = NAOActorMolecule(self.memory,self.memory.atoms,self.nao_mem,self.nao_motion,duplication=True)
            atoms = json_dict["atoms"]
            molecular_graph = json_dict["molecular_graph"]
            for json_atom in atoms:
                new_atom = load_json_atom(json_atom,memory,nao_memory=self.nao_mem,nao_motion=self.nao_motion)
                atom_id_number = int(re.match('a-([0-9]+)',new_atom.id).group(1))
                # print atom_id_number
                # print molecular_graph
                new_id = new_atom.create_id(atom_id_number + last_atom_id)
                molecular_graph = molecular_graph.replace(
                    new_atom.id,
                    new_id)
                # print molecular_graph
                atom_id_number += last_atom_id
                if atom_id_number > largest_atom_id:
                    largest_atom_id = atom_id_number
                self.memory.add_atom(new_atom,new_id)
            print molecular_graph
            molecule.molecular_graph=json_graph.loads(molecular_graph)
            print molecule.molecular_graph
            molecule.set_connections()
            memory.add_molecule(molecule)
            memory.add_to_brain_archive(molecule)
            last_atom_id = largest_atom_id
        for molecule in self.memory.brain_archive:
            print molecule
            for a in molecule.get_atoms_as_list():
                print a.print_atom()
        print "brain_archive:",self.memory.brain_archive

    def load_specific_molecule(self,full_path):
            if re.match('.*\.json',full_path) is None:
                return "Path must contain a json file"
            else:
                json_file = open(full_path,"r")
                json_dict = eval(json_file.read())
                json_file.close()
                id_map = {}
                molecule = NAOActorMolecule(self.memory,self.memory.atoms,self.nao_mem,self.nao_motion,duplication=True)
                atoms = json_dict["atoms"]
                molecular_graph = json_dict["molecular_graph"]
                for json_atom in atoms:
                    new_atom = load_json_atom(json_atom,memory,nao_memory=self.nao_mem,nao_motion=self.nao_motion)
                    self.memory.add_atom(new_atom,new_atom.get_id())
                molecule.molecular_graph=json_graph.loads(molecular_graph)
                molecule.set_connections()
                memory.add_molecule(molecule)
                return molecule

if __name__ == '__main__':
    #######################
    # Arguments
    #######################

    args = sys.argv
    if len(args) == 1:
        task = "run_ga"
    elif len(args) > 1:
        task = args[1]
        if len(args) > 2:
            molecule_path = args[2]

    #######################
    # Nao Variables
    #######################

    broker=ALBroker("localbroker","0.0.0.0",   # listen to anyone
           0,           # find a free port and use it
           "127.0.0.1",         # parent broker IP
           config.robot_port)

    global nao_mem_global
    nao_mem_global = NaoMemory("memoryManager")
    global bmf_global
    bmf_global = NaoMotorFunction("bmf","127.0.0.1")
    bmf_global.rest()

    ################################
    # Inititialise search parameters
    ################################
    memory = Messages()
    atoms = memory.atoms
    games = []
    best_game_scores = []
    all_games_history = []

    # set up games here
    max_143 = NaoMaxSensorGameMolecule(memory,atoms,nao_mem_global,sensors=[143])
    distance = NaoMaxDistanceGameMolecule(memory,atoms,nao_mem_global,sensors=[200,202])

    #add games to this array
    games_array = [max_143]

    #brain archive
    util = NaoGAUtil(memory,nao_mem_global,bmf_global)
    util.load_brain_archive()

    # set up actor molecules here
    molecules_array = []
    for i in range(0,config.pop_size):
        molecules_array.append(SMMActorMolecule(memory,atoms,nao_mem_global,bmf_global))
    ga = NaoIslandGA(games_array,memory,nao_mem_global,bmf_global,molecules_array)
    if task == "run_ga":
        ga.run_ga()
    elif task == "play_molecule":
        molecule = util.load_specific_molecule(molecule_path)
        if type(molecule) == str:
            print molecule
        else:
            ga.assess_fitness(molecule,games_array[0])
    else:
        print "no task specified: must either be run_ga or \"play_molecule <path to molecule>\""

