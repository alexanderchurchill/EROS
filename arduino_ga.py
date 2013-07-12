import os,sys,time,random,numpy
from robots.arduino_functions import ArduinoController
from core.molecule import *
from molecules.arduino_molecules import *
from core.memory import Messages
import networkx as nx
import pygraphviz as pgv
from networkx.readwrite import json_graph
import config
from experiments_and_search.utilities import WeightedRandomizer, save_population, save_archive, plot_fitness, drawMol, load_json_atom
from experiments_and_search.ga import IslandGA
# makes sure we save all array data
numpy.set_printoptions(threshold=numpy.nan)

class ArduinoIslandGA(IslandGA):
    def __init__(self,games_array,memory,arduino_interface,init_molecules):
        super(ArduinoIslandGA,self).__init__(games_array,memory)
        self.arduino_interface = arduino_interface
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
        individual.activate()
        game.activate()
        for t in range(0,config.time_steps_per_evaluation):
            if config.use_sensory_conditions:
                individual.activate()
            individual.act()
            individual.conditional_activate()
            game.act()
            game.conditional_activate()
            time.sleep(config.time_step_length)
            if config.draw_molecules:
                drawMol(individual.molecular_graph,self.memory,node_labels="values")
        individual.fitness = game.get_fitness()
        print "fitness:",individual.fitness
        game.deactivate()
        individual.deactivate()


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        task = "run_ga"
    elif len(args) > 1:
        task = args[1]
        if len(args) > 2:
            molecule_path = args[2]

    #######################
    # Arduino Variables
    #######################
    arduino_interface = ArduinoController()
    ################################
    # Inititialise search parameters
    ################################
    memory = Messages()
    atoms = memory.atoms

    # set up games here
    max_sensors = ArduinoGameMolecule(memory,atoms,arduino_interface)

    #add games to this array
    games_array = [max_sensors]

    # set up actor molecules here
    molecules_array = []
    for i in range(0,config.pop_size):
        molecules_array.append(ArduinoActorMolecule(memory,atoms,arduino_interface))
    ga = ArduinoIslandGA(games_array,memory,arduino_interface,molecules_array)
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
