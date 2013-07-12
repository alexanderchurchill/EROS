import random
import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz as pgv
import os, sys
from core.atom import *
from atoms.input_atoms import *
from atoms.game_atoms import *
from atoms.transform_atoms import *
from atoms.epuck_atoms import *
from atoms.nao_atoms import *

"""
Utility classes and functions to aid search algorithms
and plot results
"""
graph_colours = {
        "motor":"red",
        "sensory":"blue",
        "transform":"green",
        "game":"purple"
        }

class WeightedRandomizer:
    """
    This is used to create probabilities weighted by
    value (i.e. fitness proportionate weightings)
    """
    def __init__ (self, weights):
        self.__max = .0
        self.__weights = []
        for value, weight in weights.items ():
            self.__max += weight
            self.__weights.append ( (self.__max, value) )

    def random (self):
        r = random.random () * self.__max
        for ceil, value in self.__weights:
            if ceil > r: return value

    def get_weights(self):
        return self.__weights

    def get_max(self):
        return self.__max

##################
# Plotting graphs
##################
def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def plot_fitness(population,game,games_history,generation):
    if not os.path.exists('results'.format(game)): os.makedirs('results'.format(game))
    if not os.path.exists('results/graphs/game_{0}'.format(game)): os.makedirs('results/graphs/game_{0}'.format(game))
    plt.figure(1)
    plt.clf()
    popFit = []
    for index, i in enumerate(population):
        popFit.append(i.fitness)
        merged = flatten(popFit)

    games_history.append(merged)

    trans = [list(i) for i in zip(*games_history)]
    for index, i in enumerate(trans):
        plt.plot(trans[index], marker='o', linestyle='None')
    plt.draw()
    plt.ion()
    plt.show()
    plt.savefig('results/graphs/game_{0}/{1}.png'.format(game,generation))
    plt.close()

def save_population(g,population,game="game_1",memory=None):
    if not os.path.exists('results'): os.makedirs('results')
    if not os.path.exists('results/populations'): os.makedirs('results/populations')
    if not os.path.exists('results/populations/game_{0}'.format(game)): os.makedirs('results/populations/game_{0}'.format(game))
    if not os.path.exists('results/populations/game_{0}/{1}'.format(game,g)): os.makedirs('results/populations/game_{0}/{1}'.format(game,g))
    for i,p in enumerate(population):
        file = open('results/populations/game_{0}/{1}/{2}.dat'.format(game,g,i),'w')
        file.write("member: {0}\n".format(i))
        file.write("fitness: {0}\n".format(p.fitness))
        file.write("----ATOMS----\n")
        for a in p.get_atoms_as_list():
            file.write(a.print_atom())
        file.close()
        graph = nx.to_agraph(p.molecular_graph)
        for n in graph.nodes():
            graph.get_node(n).attr['color'] = graph_colours[memory.get_atom(n).type]
            if memory.get_atom(n).__class__.__name__ == "EuclidianDistanceAtom":
                graph.get_node(n).attr['color'] = "yellow"
                graph.get_node(n).attr['label'] = memory.get_atom(n).goal_output
            if memory.get_atom(n).__class__.__name__ == "PCATranformAtom":
                graph.get_node(n).attr['color'] = "orange"
                graph.get_node(n).attr['label'] = memory.get_atom(n).N
            if memory.get_atom(n).__class__.__name__ == "LWPRTransformAtom":
                graph.get_node(n).attr['color'] = "black"
                graph.get_node(n).attr['label'] = "[{0},{1}]".format(
                                                    memory.get_atom(n).N,
                                                    memory.get_atom(n).inputs)
            if memory.get_atom(n).__class__.__name__ == "KMeansClassifyAtom":
                graph.get_node(n).attr['color'] = "pink"
                graph.get_node(n).attr['label'] = memory.get_atom(n).K
            if memory.get_atom(n).__class__.__name__ == "IzhikevichTransformAtom":
                graph.get_node(n).attr['color'] = "black"
                graph.get_node(n).attr['label'] = memory.get_atom(n).no_outputs
            if memory.get_atom(n).type == 'motor':
                graph.get_node(n).attr['label'] = memory.get_atom(n).motors
            if memory.get_atom(n).type == 'sensory':
                graph.get_node(n).attr['label'] = memory.get_atom(n).sensors
        graph.layout()
        graph.draw('results/populations/game_{0}/{1}/{2}.png'.format(game,g,i))
        json_output = p.get_json()
        file = open('results/populations/game_{0}/{1}/{2}.json'.format(game,g,i),'w')
        file.write(str(json_output))
        file.close()

def save_archive(archive,memory):
    if not os.path.exists('results'): os.makedirs('results')
    if not os.path.exists('results/archive'): os.makedirs('results/archive')
    for i,m in enumerate(archive):
        p = m.actor
        file = open('results/archive/{0}.dat'.format(i),'w')
        file.write("member: {0}\n".format(i))
        file.write("fitness: {0}\n".format(m.fitness))
        file.write("----ATOMS----\n")
        for a in p.get_atoms_as_list():
            file.write(a.print_atom())
        file.close()
        graph = nx.to_agraph(p.molecular_graph)
        for n in graph.nodes():
            graph.get_node(n).attr['color'] = graph_colours[memory.get_atom(n).type]
            if memory.get_atom(n).__class__.__name__ == "EuclidianDistanceAtom":
                graph.get_node(n).attr['color'] = "yellow"
                graph.get_node(n).attr['label'] = memory.get_atom(n).goal_output
            if memory.get_atom(n).__class__.__name__ == "PCATranformAtom":
                graph.get_node(n).attr['color'] = "orange"
                graph.get_node(n).attr['label'] = memory.get_atom(n).N
            if memory.get_atom(n).__class__.__name__ == "LWPRTransformAtom":
                graph.get_node(n).attr['color'] = "black"
                graph.get_node(n).attr['label'] = "[{0},{1}]".format(
                                                    memory.get_atom(n).N,
                                                    memory.get_atom(n).inputs)
            if memory.get_atom(n).__class__.__name__ == "KMeansClassifyAtom":
                graph.get_node(n).attr['color'] = "pink"
                graph.get_node(n).attr['label'] = memory.get_atom(n).K
            if memory.get_atom(n).__class__.__name__ == "IzhikevichTransformAtom":
                graph.get_node(n).attr['color'] = "black"
                graph.get_node(n).attr['label'] = memory.get_atom(n).no_outputs
            if memory.get_atom(n).type == 'motor':
                graph.get_node(n).attr['label'] = memory.get_atom(n).motors
            if memory.get_atom(n).type == 'sensory':
                graph.get_node(n).attr['label'] = memory.get_atom(n).sensors
        graph.layout()
        graph.draw('results/archive/{0}.png'.format(i))
        json_output = p.get_json()
        file = open('results/archive/{0}.json'.format(i),'w')
        file.write(str(json_output))
        file.close()

def nao_load_molecule(json,memory,atoms,nao_memory,nao_motion):
    molecule = NAOActorMolecule(memory,atoms,nao_memory,nao_motion,duplication=True)
    atoms = json["atoms"]
    for atom in atoms:
        id = atom["id"]
        _class = atom["class"]
        message_delays = atom["message_delays"]
        if _class == 'NaoSensorAtom':
            new_atom = NaoSensorAtom(memory=memory,messages=None,message_delays=message_delays,
                 sensors=atom["sensors"],sensory_conditions=atom["sensory_conditions"],nao_memory=nao_memory,
                 parameters=atom["parameters"],id = id)
            memory.add_atom(new_atom,id)
        elif _class == 'TransformAtom':
            new_atom = TransformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id)
            memory.add_atom(new_atom,id)
        elif _class == 'LinearTransformAtom':
            new_atom = LinearTransformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id)
            new_atom.set_t_matrix(atom["t_matrix"])
            memory.add_atom(new_atom,id)
        elif _class == 'PCATranformAtom':
            new_atom = PCATranformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id,N=atom["N"])
            memory.add_atom(new_atom,id)
        elif _class == 'KMeansClassifyAtom':
            new_atom = KMeansClassifyAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id,K=atom["K"])
            memory.add_atom(new_atom,id)
        elif _class == 'IzhikevichTransformAtom':
            new_atom = IzhikevichTransformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id,no_outputs=atom["no_outputs"],
                    assign_inputs_to_neurons=atom["assign_inputs_to_neurons"],weight_spikes=atom["weight_spikes"],
                            re=atom["re"],
                            ri=atom["ri"],
                            a=atom["a"],
                            b=atom["b"],
                            c=atom["c"],
                            d=atom["d"],
                            S=atom["S"],
                            gain = atom["gain"])
            memory.add_atom(new_atom,id)
        elif _class == 'EuclidianDistanceAtom':
            new_atom = EuclidianDistanceAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id,goal_output=atom["goal_output"])
            memory.add_atom(new_atom,id)
        elif _class == 'NaoMotorAtom':
            new_atom = NaoMotorAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],motors=atom["motors"],nao_motion=nao_motion,
                nao_memory=nao_memory, use_input=atom["use_input"],id = id)
            memory.add_atom(new_atom,id)
    molecule.molecular_graph=json_graph.loads(json["molecular_graph"])
    molecule.set_connections()
    return molecule

def load_json_atom(atom,memory,nao_memory=None,nao_motion=None,epuck_controller=None):
    """
    Returns an atom provided in dictionary format
    """
    id = atom["id"]
    _class = atom["class"]
    message_delays = atom["message_delays"]
    if _class == 'TransformAtom':
        new_atom = TransformAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],id = id)
    elif _class == 'LinearTransformAtom':
        new_atom = LinearTransformAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],m=atom["m"],n=atom["n"],id = id)
        new_atom.set_t_matrix(atom["t_matrix"])
    elif _class == 'OscillatorAtom':
        new_atom = OscillatorAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],amplitude=atom["amplitude"],speed=atom["speed"],
            no_outputs=atom["no_outputs"],id = id)
    elif _class == 'PCATranformAtom':
        new_atom = PCATranformAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],id = id,N=atom["N"])
    elif _class == 'KMeansClassifyAtom':
        new_atom = KMeansClassifyAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],id = id,K=atom["K"])
    elif _class == 'IzhikevichTransformAtom':
        new_atom = IzhikevichTransformAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],id = id,no_outputs=atom["no_outputs"],
                assign_inputs_to_neurons=atom["assign_inputs_to_neurons"],weight_spikes=atom["weight_spikes"],
                        re=atom["re"],
                        ri=atom["ri"],
                        a=atom["a"],
                        b=atom["b"],
                        c=atom["c"],
                        d=atom["d"],
                        S=atom["S"],
                        gain = atom["gain"])
    elif _class == 'EuclidianDistanceAtom':
        new_atom = EuclidianDistanceAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],id = id,goal_output=atom["goal_output"])
    elif _class == 'SumInputAtom':
        new_atom = SumInputAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],id = id,normalise=atom["normalise"])
    # Nao
    elif _class == 'NaoSensorAtom':
        new_atom = NaoSensorAtom(memory=memory,messages=None,message_delays=message_delays,
             sensors=atom["sensors"],sensory_conditions=atom["sensory_conditions"],nao_memory=nao_memory,
             parameters=atom["parameters"],id = id,activate_with_sensory_condition=atom["activate_with_sensory_condition"],
            deactivate_with_sensory_condition=atom["deactivate_with_sensory_condition"])
    elif _class == 'NaoMotorAtom':
        new_atom = NaoMotorAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],motors=atom["motors"],nao_motion=nao_motion,
            nao_memory=nao_memory, use_input=atom["use_input"],id = id)
    elif _class == 'SHCLtInternalSensor':
        new_atom = SHCLtInternalSensor(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],m=atom["m"],n=atom["n"],sensors=atom["sensors"],
            function=atom["function"],id = id,nao_memory=nao_memory)
        new_atom.set_t_matrix(atom["t_matrix"])
    # Epuck
    elif _class == 'EpuckMultiSensor':
        new_atom = EpuckMultiSensor(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],sensors=atom["sensors"],sensory_conditions=atom["sensory_conditions"],
            epuck_interface=epuck_controller,id = id,activate_with_sensory_condition=atom["activate_with_sensory_condition"],
            deactivate_with_sensory_condition=atom["deactivate_with_sensory_condition"],
            )
    elif _class == 'EpuckMotorAtom':
        new_atom = EpuckMotorAtom(memory=memory,messages=None,message_delays=message_delays,
            parameters=atom["parameters"],motors=atom["motors"],epuck_interface=epuck_controller,
            use_input=atom["use_input"],id=id)
    return new_atom

def drawMol(graph,memory,node_labels="values"):
    plt.figure(2)
    plt.ion()
    plt.show()
    plt.clf()
    pos1 = nx.circular_layout(graph)
    labels = {}
    for n,d in graph.nodes_iter(data=True):
        if memory.get_atom(n).type == "sensory":
            sensor_node_colour = 'c'
            if memory.get_atom(n).__class__.__name__ == "OscillatorAtom":
                sensor_node_colour = 'g'
            nx.draw_networkx_nodes(graph,pos1, nodelist=[n] ,node_color=sensor_node_colour, label = memory.get_atom(n).sensors)
            if node_labels == "values":
                if memory.get_atom(n).sensor_input:
                    labels[n]=["{0:.2f}".format(v) for v in memory.get_atom(n).sensor_input]
            else:
                labels[n]=memory.get_atom(n).sensors
        if memory.get_atom(n).type == "motor":
            nx.draw_networkx_nodes(graph,pos1, nodelist=[n] ,node_color='r', label = "mot")
            if node_labels == "values":
                if config.robot_system == "nao":
                    labels[n]=["{0:.2f}".format(v) for v in memory.get_atom(n).angles]
                    print "angles:",["{0:.2f}".format(v) for v in memory.get_atom(n).angles]
                else:
                    labels[n]=["{0:.2f}".format(v) for v in memory.get_atom(n).speeds]
                    print "angles:",["{0:.2f}".format(v) for v in memory.get_atom(n).speeds]
            else:
                labels[n]=memory.get_atom(n).motors
        if memory.get_atom(n).type == "transform":
            nx.draw_networkx_nodes(graph,pos1, nodelist=[n] ,node_color='b', label = memory.get_atom(n).__class__.__name__)
            labels[n] = memory.get_atom(n).__class__.__name__
        if memory.get_atom(n).active == True and memory.get_atom(n).type == "motor":
            nx.draw_networkx_nodes(graph,pos1, node_size=2000, nodelist=[n] ,node_color='r', label = memory.get_atom(n).motors)
        if memory.get_atom(n).active == True and memory.get_atom(n).type == "transform":
            nx.draw_networkx_nodes(graph,pos1, node_size=2000, nodelist=[n] ,node_color='b', label = memory.get_atom(n).get_id())
        if memory.get_atom(n).active == True and memory.get_atom(n).type == "sensory":
            nx.draw_networkx_nodes(graph,pos1, node_size=2000, nodelist=[n] ,node_color=sensor_node_colour, label = memory.get_atom(n).sensors)
    edge_colours = []
    edge_labels = {}
    for edge in graph.edges():
        _from = edge[0]
        _to = edge[1]
        if memory.get_atom(_from).active:
            edge_colours.append('r')
        else:
            edge_colours.append('k')
        # if _from not in edge_labels:
        #     edge_labels[_from] = {}
        edge_labels[edge] = str(memory.get_atom(_from).message_delays[0])
    nx.draw_networkx_edges(graph,pos1,alpha = 0.5, width = 6, edge_color=edge_colours)
    nx.draw_networkx_edge_labels(graph,pos1,alpha = 0.5, width = 6, edge_labels=edge_labels)
    nx.draw_networkx_labels(graph,pos1,labels,font_size=10,font_family='sans-serif')
    plt.draw()
