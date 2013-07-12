import random, copy, os, sys
import config
from .utilities import WeightedRandomizer, save_population, save_archive, plot_fitness

class BaseGA(object):
    """
    Basic methods and data structures used in all GAs
    """
    def assess_fitness(self,individual,game):
        pass

    def load_brain_archive(self):
        """
        adds brain archive molecules to memory
        """
        pass

class IslandGA(BaseGA):
    """
    Basic methods and data structures used in all GAs
    """
    def __init__(self,games_array,memory):
        self.games_array = games_array
        self.memory = memory
        self.atoms = memory.atoms
        self.games = []
        self.best_game_scores = []
        self.all_games_history = []
        self.islands = []
        self.population = []

        #add games to this array
        for g in self.games_array:
            self.games.append(g)
            self.memory.add_molecule(g)
            self.all_games_history.append([])
            self.best_game_scores.append(-99999.0)

    def setup_island(self):
        """
        To be replaced by whatever molecule needs to be produced
        """
        pass

    def assess_fitness(self,individual,game):
        pass

    def run_ga(self):
        for game_no,island in enumerate(self.islands):
            for indiv in island:
                self.assess_fitness(indiv,self.games[game_no])
        for game_no,island in enumerate(self.islands):
            best = 0
            print "fitnesses game {0}:".format(game_no)
            for i,bm in enumerate(island):
                print "{0}: {1}".format(i,bm.fitness)
                if bm.fitness > island[best].fitness:
                    best = i
            print "best = ",best
            print "fitness = ",island[best].fitness

        for g in range(0,config.pop_size*config.max_generations):
            print "iteration:",g
            for game_no,island in enumerate(self.islands):
                population = island
                game = self.games[game_no]
                print "===looking at game {0}===".format(game_no)
                ind_1_i = random.randint(0,len(population)-1)
                ind_2_i = random.randint(0,len(population)-1)
                while ind_1_i == ind_2_i:
                    ind_2_i = random.randint(0,len(population)-1)
                ind_1 = population[ind_1_i]
                ind_2 = population[ind_2_i]
                for ind in [ind_1,ind_2]:
                    self.assess_fitness(ind,game)
                if ind_1.fitness > ind_2.fitness:
                    print "ind_1 better"
                    ind_2 = ind_1.duplicate()

                    self.memory.add_molecule(ind_2)
                    population[ind_2_i] = ind_2
                    new_ind = ind_2
                    ind_2.fitness = copy.deepcopy(ind_1.fitness)
                else:
                    print "ind_2 better"
                    ind_1 = ind_2.duplicate()
                    self.memory.add_molecule(ind_1)
                    population[ind_1_i] = ind_1
                    new_ind = ind_1
                    ind_1.fitness = copy.deepcopy(ind_2.fitness)
                if config.use_brain_archive and len(self.memory.brain_archive) > 0 and random.random() < config.crossover_rate:
                    new_ind.single_point_crossover(random.choice(self.memory.brain_archive))
                if config.use_run_archive and len(self.memory.archive) > 0 and random.random() < config.crossover_rate:
                    crossover_ind_index = crossover_get_weights.random()
                    print "choosing {0} to crossover".format(crossover_ind_index)
                    ind_from_archive = self.memory.archive[crossover_ind_index].actor
                    new_ind.crossover(ind_from_archive)
                new_ind.mutate()
                if g%config.pop_size == 0:
                    plot_fitness(population,game_no,self.all_games_history[game_no],g)
                    save_population(g,population,game_no,self.memory)
                    print "fitnesses:"
                    for p in population:
                        print p.fitness
            if g > 0 and g%(config.pop_size*10) == 0:
                """
                After a certain number of iterations, store the best (actor,game) from
                each island
                """
                for game_no,island in enumerate(self.islands):
                    for indiv in island:
                        self.assess_fitness(indiv,self.games[game_no])
                for game_no,island in enumerate(self.islands):
                    best = 0
                    print "fitnesses game {0}:".format(game_no)
                    for i,bm in enumerate(island):
                        print "{0}: {1}".format(i,bm.fitness)
                        if bm.fitness > island[best].fitness:
                            best = i
                    print "best = ",best
                    print "fitness = ",island[best].fitness
                    self.memory.add_best_game_act_pair(self.games[game_no],island[best],
                                                            fitness=island[best].fitness)
                    if island[best].fitness > self.best_game_scores[game_no]:
                        self.best_game_scores[game_no] = island[best].fitness
                crossover_weights_table = {}
                for i,b in enumerate(self.memory.archive):
                    normaliser = self.best_game_scores[i%len(self.games)]
                    if normaliser == 0 : normaliser = 0.01
                    crossover_weights_table[i]=b.actor.fitness/normaliser
                    crossover_get_weights = WeightedRandomizer(crossover_weights_table)
                save_archive(self.memory.archive,self.memory)

        ############################
        # Sort out final population
        ############################
        save_archive(self.memory.archive,self.memory)

        for game_no,island in enumerate(self.islands):
            for indiv in island:
                assess_fitness(indiv,self.games[game_no])
        for game_no,island in enumerate(self.islands):
            best = 0
            print "fitnesses game {0}:".format(game_no)
            for i,bm in enumerate(island):
                print "{0}: {1}".format(i,bm.fitness)
                if bm.fitness > island[best].fitness:
                    best = i
            print "best = ",best
            print "fitness = ",island[best].fitness
