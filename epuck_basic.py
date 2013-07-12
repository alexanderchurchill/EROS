import os,re,time,random,math
from molecules.epuck_molecules import *
from core.memory import Messages
import config
from experiments_and_search.utilities import WeightedRandomizer, save_population, save_archive, plot_fitness, load_json_atom
from experiments_and_search.ga import IslandGA
from robots.epuck_functions import EpuckFunctions
class EpuckGAUtil():
    def __init__(self,memory,controller):
        self.memory = memory
        self.controller = controller

    def load_brain_archive(self):
        largest_atom_id = 0
        last_atom_id = 0
        base = "brain_archive/{0}/".format(config.robot_system)
        files = [o for o in os.listdir(base) if re.match('.*\.json',o)]
        for f in files:
            print f
            json_file = open("{0}{1}".format(base,f),"r")
            json_dict = eval(json_file.read())
            json_file.close()
            id_map = {}
            molecule = EpuckActorMolecule(self.memory,self.memory.atoms,self.controller,duplication=True)
            atoms = json_dict["atoms"]
            molecular_graph = json_dict["molecular_graph"]
            for json_atom in atoms:
                new_atom = load_json_atom(json_atom,memory,epuck_controller=self.controller)
                atom_id_number = int(re.match('a-([0-9]+)',new_atom.id).group(1))
                new_id = new_atom.create_id(atom_id_number + last_atom_id)
                molecular_graph = molecular_graph.replace(
                    new_atom.id,
                    new_id)
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
                molecule = EpuckActorMolecule(self.memory,self.memory.atoms,self.controller,duplication=True)
                atoms = json_dict["atoms"]
                molecular_graph = json_dict["molecular_graph"]
                for json_atom in atoms:
                    new_atom = load_json_atom(json_atom,memory,epuck_controller=self.controller)
                    self.memory.add_atom(new_atom,new_atom.get_id())
                molecule.molecular_graph=json_graph.loads(molecular_graph)
                molecule.set_connections()
                memory.add_molecule(molecule)
                return molecule

class EpuckIslandGA(IslandGA):
    def __init__(self,games_array,memory,controller,init_molecules):
        super(EpuckIslandGA,self).__init__(games_array,memory)
        self.controller = controller
        self.setup_islands(init_molecules)

    def setup_islands(self,molecules):
        self.islands = []
        for island in self.games:
            population = []
            for molecule in molecules:
                self.memory.add_molecule(molecule)
                population.append(molecule)
            self.islands.append(population)

    def assess_fitness(self,actor,game):
        self.controller.emitter.send(str("stop"))
        self.controller.stop_moving()
        self.controller.step(10)
        d = None
        self.controller.update_proximities()
        self.controller.snapshot(show=False,sampled=True)
        self.controller.step(200)
        if self.controller.receiver.getQueueLength() > 0:
            for i in range(0,self.controller.receiver.getQueueLength()):
                d = self.controller.receiver.getData()
                self.controller.receiver.nextPacket()
        if d is not None:
            self.controller.update_current_coordinates(d)
        actor.activate()
        game.activate()

        # Main loop
        count = 0
        while count < config.time_steps_per_evaluation:
            self.controller.update_proximities()
            self.controller.snapshot(show=False,sampled=True)
            if config.use_sensory_conditions:
                actor.activate()
            actor.act()
            actor.conditional_activate()
            game.act()
            game.conditional_activate()
            if self.controller.receiver.getQueueLength() > 0:
                for i in range(0,self.controller.receiver.getQueueLength()):
                    d = self.controller.receiver.getData()
                    self.controller.receiver.nextPacket()
            if d is not None:
                self.controller.update_current_coordinates(d)
            if self.controller.step(200) == -1: break
            count += 1
        actor.fitness = game.get_fitness()
        print "actor.fitness:",actor.fitness
        actor.deactivate()
        game.deactivate()
        self.controller.emitter.send(str("stop"))
        self.controller.stop_moving()
        self.controller.step(200)

################################
# Epuck parameters
################################

controller = EpuckFunctions()
controller.basic_setup()

################################
# Inititialise search parameters
################################
memory = Messages()
atoms = memory.atoms
games = []
best_game_scores = []
all_games_history = []

# set up games here
distance = EpuckDistanceGameMolecule(memory,atoms,controller)
proxim = EpuckGameMolecule(memory,atoms,controller)
#add games to this array
games_array = [proxim]

# set up actor molecules here
molecules_array = []
print "creating molecules"
for i in range(0,config.pop_size):
    molecules_array.append(EpuckTestMolecule(memory,atoms,controller))
print "finished molecules"
util = EpuckGAUtil(memory,controller)
util.load_brain_archive()
ga = EpuckIslandGA(games_array,memory,controller,molecules_array)
ga.run_ga()

