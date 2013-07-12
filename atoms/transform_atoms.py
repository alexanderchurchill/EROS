from __future__ import division
from core.atom import *
from core.atom import _check_active_timer
import random,copy,string,math
import config
if config.LWPR:
    from lwpr import *

class LinearTransformAtom(TransformAtom):
    """
    Atom used to transform sensor input to output
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                        parameters=None,id=None,n=5,m=None):
        super(LinearTransformAtom, self).__init__(memory,messages,
                                                message_delays,id=id)
        # n columns (outputs), m rows (inputs)
        self.n  = n #size of matrix
        if m is None:
            self.m = n
        else:
            self.m = m
        self.t_matrix = [] #creates nxm matrix (with an extra bias)
        for i in range(0,self.m+1):
            self.t_matrix.append([])
            for j in range(0,self.n):
                self.t_matrix[i] += [0]
        self.init_t_matrix()
        self.parameters = parameters

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        output = self.get_output(inp,5)
        self.send_message("output",output)
        print "t_matrix_output:",output


    def init_t_matrix(self):
        for m,row in enumerate(self.t_matrix):
            for n,cell in enumerate(row):
                self.t_matrix[m][n]=random.gauss(0,0.3)
                if self.t_matrix[m][n] > 1.5:
                    self.t_matrix[m][n] = 1.5
                elif self.t_matrix[m][n] < -1.5:
                    self.t_matrix[m][n] = -1.5

    def init_test_matrix(self):
        for i,row in enumerate(self.t_matrix):
            for j,column in enumerate(row):
                self.t_matrix[i][j] = i

    def get_t_matrix(self):
        return self.t_matrix

    def set_t_matrix(self,t_matrix):
        self.t_matrix = t_matrix

    def mutate_t_matrix(self,mutation_rate):
        for m,row in enumerate(self.t_matrix):
            for n,cell in enumerate(row):
                if random.random() < mutation_rate:
                    self.t_matrix[m][n]+=random.gauss(0,0.2)
                    if self.t_matrix[m][n] > 1.5:
                        self.t_matrix[m][n] = 1.5
                    elif self.t_matrix[m][n] < -1.5:
                        self.t_matrix[m][n] = -1.5

    def large_mutate_t_matrix(self,mutation_rate):
        for m,row in enumerate(self.t_matrix):
            for n,cell in enumerate(row):
                if random.random() < mutation_rate:
                    self.t_matrix[m][n]=random.gauss(0,0.3)
                else:
                    self.t_matrix[m][n]+=random.gauss(0,0.1)
                if self.t_matrix[m][n] > 1:
                    self.t_matrix[m][n] = 1
                elif self.t_matrix[m][n] < -1:
                    self.t_matrix[m][n] = -1

    def mutate(self,large=False):
        self.mutate_delays(config.mutation_rate)
        if large is False:
            # print "mutating t_matrix"
            self.mutate_t_matrix(config.mutation_rate)
        else:
            self.large_mutate_t_matrix(config.mutation_rate)

    def get_output(self,input,len_output):
        """
        takes an input vector (of max length n)
        and produces an output vector (of max length n)
        """
        # print "get_output: input: ",input
        input_bias = input[0:self.m] + [1]
        # print "get_output: input_bias: ",input_bias
        if len_output > self.n:
            len_output = self.n
        output = [0]*len_output
        for column in range(0,len_output):
            for i,inp in enumerate(input_bias):
                # print "output[{0}] += {1}*{2}".format(column,self.t_matrix[i][column],inp)
                output[column] += self.t_matrix[i][column]*inp
        # print "input:",input
        # print "transformed output:",output
        return output

    def duplicate(self):
        new_atom = LinearTransformAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            n=self.n,
                            m=self.m
                            )
        new_atom.set_t_matrix(copy.deepcopy(self.get_t_matrix()))
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["t_matrix","m","n"]:
            self.json[variable] = self.__getattribute__(variable)
    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "parameters: {0}\n".format(self.parameters)
        output += "n: {0}\n".format(self.n)
        output += "t_matrix: {0}\n".format(self.t_matrix)
        return output

class SHCLTransAtom(LinearTransformAtom):
    """
    Atom used to transform sensor input to output
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                parameters=None,id=None,n=5,m=None,function="max"):
        super(SHCLTransAtom, self).__init__(memory=memory,messages=messages,
                                    message_delays=message_delays,id=id,
                                    parameters=parameters,n=n,m=m)
        self.function = function
        self.curr_fitness = -99999
        self.prev_fitness = -99999
        self.prev_t_matrix = copy.deepcopy(self.t_matrix)
        self.state = []
        self.timer_count = 0
    @_check_active_timer
    def act(self):
        # print "previously_tested_params:",self.motor_params
        # print "curr_params:",self.motor_params
        # print "prev_params:",self.prev_motor_params
        if self.time_active > 2 and self.timer_count>1:
            self.timer_count = 0
            # print "self.time_active > 1"
            inp = self.get_input()
            # print "input:",inp
            # print "input produced by:",self.motor_params
            if len(inp) > 0:
                self.get_fitness(inp)
                if self.curr_fitness > self.prev_fitness:
                    # print "new params better"
                    # print "prev_fitness:",self.prev_fitness
                    # print "curr_fitness:",self.curr_fitness
                    # save curr_params
                    self.prev_t_matrix = copy.deepcopy(self.t_matrix)
                    self.shc_mutate_t_matrix()
                else:
                    # print "new params worse"
                    # print "prev_fitness:",self.prev_fitness
                    # print "curr_fitness:",self.curr_fitness
                    # if self.prev_motor_params == self.motor_params:
                    #     self.prev_fitness = self.curr_fitness
                    self.t_matrix = copy.deepcopy(self.prev_t_matrix)
                    # self.shc_mutate_t_matrix()
                    if random.random() < 0.7:
                        self.shc_mutate_t_matrix()
                    else:
                        self.prev_fitness = self.curr_fitness
                    self.curr_fitness = self.prev_fitness
        else:
            self.timer_count += 1
        # print "prev_fitness:",self.prev_fitness
        # print "curr_fitness:",self.curr_fitness
        # print "prev_params:",self.prev_motor_params
        # print "curr_params:",self.motor_params
        output = self.get_output(inp,5)
        self.send_message("output",output)


    def get_fitness(self,inp_vector):
        self.prev_fitness = self.curr_fitness
        if self.function == "max":
            self.curr_fitness = self.max_input(inp_vector)
        elif self.function == "min":
            self.curr_fitness = self.min_input(inp_vector)
        elif self.function == "distance":
            self.curr_fitness = self.distance_input(inp_vector)

    def max_input(self,inp_vector):
        inp = inp_vector
        # print "input:",inp
        fitness = inp[0]
        # print "fitness:",fitness
        for i in inp[1:]:
            fitness += i
        return fitness
    def min_input(self,inp_vector):
        inp = inp_vector
        fitness = inp[0]*-1
        for i in inp[1:]:
            fitness += (i*-1)
        return fitness
    def distance_input(self,inp_vector):
        inp = inp_vector
        if len(self.state) > 0:
            if len(inp) != self.state[-1]:
                self.state = [inp]
            else:
                self.state.append(inp)
        start = self.state[0]
        end = self.state[-1]
        distances = []
        for i in range(0,self.state[0]):
            distances.append((start - end)**2)
        return math.sqrt(sum(distances))

    def shc_mutate_t_matrix(self):
        for m,row in enumerate(self.t_matrix):
            for n,cell in enumerate(row):
                    self.t_matrix[m][n]+=random.gauss(0,0.3)

    def mutate(self,large=False):
        self.mutate_delays(config.mutation_rate)
        if large is False:
            # print "mutating t_matrix"
            self.mutate_t_matrix(config.mutation_rate)
        else:
            self.large_mutate_t_matrix(config.mutation_rate)

    def get_output(self,input,len_output):
        """
        takes an input vector (of max length n)
        and produces an output vector (of max length n)
        """
        # print "get_output: input: ",input
        input_bias = input[0:self.m] + [1]
        # print "get_output: input_bias: ",input_bias
        if len_output > self.n:
            len_output = self.n
        output = [0]*len_output
        for column in range(0,len_output):
            for i,inp in enumerate(input_bias):
                # print "output[{0}] += {1}*{2}".format(column,self.t_matrix[i][column],inp)
                output[column] += self.t_matrix[i][column]*inp
        # print "input:",input
        # print "transformed output:",output
        return output

    def duplicate(self):
        new_atom = SHCLTransAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            n=n,
                            m=m,
                            function=copy.deepcopy(function)
                            )
        new_atom.set_t_matrix(copy.deepcopy(self.get_t_matrix()))
        return new_atom

    def to_json(self):
        LinearTransformAtom.to_json(self)
        for variable in ["function"]:
            self.json[variable] = self.__getattribute__(variable)
    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "parameters: {0}\n".format(self.parameters)
        output += "n: {0}\n".format(self.n)
        output += "t_matrix: {0}\n".format(self.t_matrix)
        output += "function: {0}\n".format(self.function)
        return output

class SHCMotorOutput(SHCLTransAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                parameters=None,id=None,n=5,m=None,function="max",
                use_input=False):
        super(SHCMotorOutput, self).__init__(memory=memory,messages=messages,
                                    message_delays=message_delays,id=id,
                                    parameters=parameters,n=n,m=m)
        self.motor_params = [2*(random.random()-0.5)]*1
        self.prev_motor_params = copy.deepcopy(self.motor_params)
        self.timer_count = 0
    @_check_active_timer
    def act(self):
        print "previously_tested_params:",self.motor_params
        # print "curr_params:",self.motor_params
        # print "prev_params:",self.prev_motor_params
        if self.time_active > 5 and self.timer_count>1:
            self.timer_count = 0
            # print "self.time_active > 1"
            inp = self.get_input()
            # print "input:",inp
            # print "input produced by:",self.motor_params
            if len(inp) > 0:
                self.get_fitness()
                if self.curr_fitness > self.prev_fitness:
                    # print "new params better"
                    # print "prev_fitness:",self.prev_fitness
                    # print "curr_fitness:",self.curr_fitness
                    # save curr_params
                    self.prev_motor_params = copy.deepcopy(self.motor_params)
                    for i,m in enumerate(self.motor_params):
                        number = 1.0*(random.random()-0.5)
                        print "adding:",number
                        self.motor_params[i] += number
                else:
                    # print "new params worse"
                    # print "prev_fitness:",self.prev_fitness
                    # print "curr_fitness:",self.curr_fitness
                    # if self.prev_motor_params == self.motor_params:
                    #     self.prev_fitness = self.curr_fitness
                    self.motor_params = copy.deepcopy(self.prev_motor_params)
                    # self.shc_mutate_t_matrix()
                    if random.random() < 0.9:
                        for i,m in enumerate(self.motor_params):
                            number = 1.0*(random.random()-0.5)
                            print "adding:",number
                            self.motor_params[i] += number
                    # else:
                    #     self.prev_fitness = self.curr_fitness
                    self.curr_fitness = self.prev_fitness
        else:
            print "self.time_active NOT > 1"
            self.timer_count += 1
            # self.prev_motor_params = self.motor_params
        print "prev_fitness:",self.prev_fitness
        print "curr_fitness:",self.curr_fitness
        print "prev_params:",self.prev_motor_params
        print "curr_params:",self.motor_params
        self.send_message("output",self.motor_params)
        # print "t_matrix_output:",output


class PCATranformAtom(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,N=1):
        super(PCATranformAtom, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.output_history = []
        self.u = None
        self.N = N
        self.current_max_input = 0
    def princomp(self,A):
     """ performs principal components analysis 
         (PCA) on the n-by-p data matrix A
         Rows of A correspond to observations, columns to variables. 

     Returns :  
      coeff :
        is a p-by-p matrix, each column containing coefficients 
        for one principal component.
      score : 
        the principal component scores; that is, the representation 
        of A in the principal component space. Rows of SCORE 
        correspond to observations, columns to components.
      latent : 
        a vector containing the eigenvalues 
        of the covariance matrix of A.
     """
     # computing eigenvalues and eigenvectors of covariance matrix
     M = (A-mean(A.T,axis=1)).T # subtract the mean (along columns)
     [u,s,v] = linalg.svd(cov(M)) # attention:not always sorted
     score = dot(u.T,M) # projection of the data in the new space
     return u,score,s,M

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        if len(inp) > 0:
            if len(inp) != self.current_max_input:
                self.current_max_input = len(inp)
                self.output_history = []
            self.output_history.append(inp)
            if len(self.output_history) >= 2:
                if len(self.output_history[0]) > 1:
                    self.u,score,s,M = self.princomp(array(self.output_history))
                    self.send_message("output",list(score.T[-1][0:self.N]))
                    # print "output:",list(score.T[-1][0:self.N])
                else:
                    # Because no 1 dimensional arrays allowed
                    output_array = array(self.output_history)-mean(self.output_history)
                    self.send_message("output",list(output_array[-1]))
        # print "output_history: ",self.output_history

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def mutate(self):
        self.mutate_delays(config.mutation_rate)
        self.mutate_pca_params(config.mutation_rate)
        
    def deactivate(self,clear=False):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        if clear:
            self.memory.clear_all_from_memory(self.id)
            self.output_history = []
        self.send_deactivate_message()

    def mutate_pca_params(self,mutation_rate):
        if random.random() > mutation_rate:
            self.N += random.choice([-1,1])
        if self.N > 5:
            self.N = 5
        elif self.N < 1:
            self.N = 1
    def duplicate(self):
        new_atom = PCATranformAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            N=copy.deepcopy(self.N)
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["N"]:
            self.json[variable] = self.__getattribute__(variable)
    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "parameters: {0}\n".format(self.parameters)
        output += "N: {0}\n".format(self.N)
        output += "output_history: {0}\n".format(self.output_history)
        return output

class KMeansClassifyAtom(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,K=2):
        super(KMeansClassifyAtom, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.K = K
        self.clear_input_history()
        self.centroids = None
        self.current_max_input = 0

    def add_input(self,d_input):
        if len(self.input_history) == 0:
            self.input_history = array([d_input])
        else:
            self.input_history = vstack((self.input_history,array(d_input)))

    def clear_input_history(self):
        self.input_history = array([])

    def clear_centroids(self):
        self.centroids = None

    def train_and_classify(self):
        # train and compute centroids
        if self.centroids is not None and len(self.centroids) == self.K:
            self.centroids,_ = kmeans(self.input_history,k_or_guess=self.centroids)
        else:
            self.centroids,_ = kmeans(self.input_history,k_or_guess=self.K)
        # assign last input to a cluster
        idx,_ = vq(self.input_history[-2:-1],self.centroids)
        # return output as e.g. [0,1,0] where we've assigned
        # output to cluster 1 (0 indexing)
        classification = [0]*self.K
        classification[idx] = 1
        return classification

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        if len(inp) > 0:
            if len(inp) != self.current_max_input:
                self.current_max_input = len(inp)
                self.clear_input_history()
                self.clear_centroids()
            self.add_input(inp)
            if len(self.input_history) >= 2:
                    classification = self.train_and_classify()
                    self.send_message("output",list(classification))
                    # print "output:",list(score.T[-1][0:self.N])
                    # print "kmeans [input_history]:",list(self.input_history)
                    # print "classification [input_history]:",classification

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def mutate(self):
        self.mutate_delays(config.mutation_rate)
        self.mutate_k_means(config.mutation_rate)
        
    def deactivate(self,clear=False):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        if clear:
            self.memory.clear_all_from_memory(self.id)
            self.clear_input_history()
            self.clear_centroids()
        self.send_deactivate_message()

    def mutate_k_means(self,mutation_rate):
        if random.random() > mutation_rate:
            self.K += random.choice([-1,1])
        if self.K > 5:
            self.K = 5
        elif self.K < 1:
            self.K = 1

    def duplicate(self):
        new_atom = KMeansClassifyAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            K=copy.deepcopy(self.K)
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["K"]:
            self.json[variable] = self.__getattribute__(variable)
    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "parameters: {0}\n".format(self.parameters)
        output += "K: {0}\n".format(self.K)
        return output

class EuclidianDistanceAtom(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,goal_output=None,id=None):
        super(EuclidianDistanceAtom, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        if goal_output == None:
            self.goal_output = []
        else:
            self.goal_output = goal_output

    def euclidian_distance(self,inp):
        sum_sqrd_distance = 0
        for i,goal in enumerate(self.goal_output[0:len(inp)]):
            sum_sqrd_distance += (goal-inp[i])**2
        return math.sqrt(sum_sqrd_distance)

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        output = self.euclidian_distance(inp)
        self.send_message("output",[output])

    def set_goal(self,goal):
        self.goal_output = goal

    def mutate(self):
        self.mutate_delays(config.mutation_rate)
        self.mutate_goals(config.mutation_rate)

    def mutate_goals(self,mutation_rate):
        for i,goal in enumerate(self.goal_output):
            if random.random() < mutation_rate:
                self.goal_output[i] = self.goal_output[i] + random.gauss(0,1)
                if self.goal_output[i] > 5.0:
                    self.goal_output[i] = 5.0
                elif self.goal_output[i] < -5.0:
                    self.goal_output[i] = -5.0

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def duplicate(self):
        new_atom = EuclidianDistanceAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            goal_output=copy.deepcopy(self.goal_output)
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["goal_output"]:
            self.json[variable] = self.__getattribute__(variable)

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "parameters: {0}\n".format(self.parameters)
        output += "goal_output: {0}\n".format(self.goal_output)
        return output

class IzhikevichTransformAtom(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,no_outputs=1,
                    assign_inputs_to_neurons=None,weight_spikes=None,
                            re=None,
                            ri=None,
                            a=None,
                            b=None,
                            c=None,
                            d=None,
                            S=None,
                            gain=None):
        super(IzhikevichTransformAtom, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.I = 0
        self.Ne = 80
        self.Ni = 20
        if re == None:
            self.re = rand(self.Ne)
        else:
            self.re = re
        if ri is None:
            self.ri = rand(self.Ni)
        else:
            self.ri = ri
        if a is None:
            self.a = r_[0.02 * ones(self.Ne), 0.02 + 0.08 * self.ri]
        else:
            self.a = a
        if b is None:
            self.b = r_[0.2 * ones(self.Ne), 0.25 - 0.05 * self.ri]
        else:
            self.b = b
        if c is None:
            self.c = r_[-65 + 15 * self.re**2, -65 * ones(self.Ni)]
        else:
            self.c = c
        if d is None:
            self.d = r_[8 - 6 * self.re**2, 2 * ones(self.Ni)]
        else:
            self.d = d
        if S is None:
            self.S = c_[0.5 * rand(self.Ne + self.Ni, self.Ne), -rand(self.Ne + self.Ni, self.Ni)]
        else:
            self.S = S
        if gain is None:
            self.gain = 1
        else:
            self.gain = gain
        self.v = -65 * ones(self.Ne + self.Ni)# Initial values of v
        self.u = self.b*self.v                   # Initial values of u
        self.firings = zeros((0,2))
        self.no_outputs = no_outputs
        self.assign_inputs_to_neurons = assign_inputs_to_neurons
        self.weight_spikes = weight_spikes
        self.max_inputs = 5
        self.output = []

    @_check_active_timer
    def act(self):
        self.firings = zeros((0,2))
        for t in xrange(100):# simulation of 1000 ms
            self.I = r_[(0.5*5) * randn(self.Ne), (0.5*2) * randn(self.Ni)] # To be replaced by sensory input
            #Add the inputs here to I from the sensors at neurons specified by the parameter lists.
            v = self.get_input()[0:self.max_inputs]
            if v is None:
              print "Strange!!!??"
            for i, _input in enumerate(v):
                for parameter in self.assign_inputs_to_neurons[i]:
                    self.I[parameter] = self.I[parameter]+(v[i]*self.gain)
            fired = find(self.v >= 30)# indices of spikes
            if any(fired):
                self.firings = vstack((self.firings, c_[t + 0 * fired, fired]))
                self.v[fired] = self.c[fired]
                self.u[fired] = self.u[fired] + self.d[fired]
                self.I = self.I + self.S[:,fired].sum(1)
            self.v = self.v + 0.5 * (0.04 * self.v**2 + 5 * self.v + 140 - self.u + self.I)
            self.v = self.v + 0.5 * (0.04 * self.v**2 + 5 * self.v + 140 - self.u + self.I)
            self.u = self.u + self.a*(self.b*self.v - self.u)
        a = self.firings[:,0].tolist()
        # plot(self.firings[:,0],self.firings[:,1],'.')
        # ion()
        # show()
        sums = dict((i,a.count(i)) for i in a)
        # print sums
        #Now the dict can be used to determine the motor output values.
        output = []
        for index in range(0,self.no_outputs):
            #Get neuronal sums for parameter index multiplied by the perceptron weights (no bias included yet) 
            tot = 0
            for ind3, y in enumerate(self.assign_inputs_to_neurons[len(v)-1+index]):
                for ind4, p in enumerate(y):
                    if p in sums.keys(): 
                        tot = tot + sums[p]*self.weight_spikes[index][ind4]
            output.append(tot)
        # print "output:",output
        # print "len(firings):",len(self.firings)
        self.send_message("output",output)
        self.output.append(output)

    def mutate(self):
        self.mutate_delays(config.mutation_rate)
        self.mutate_izh(config.mutation_rate)

    def mutate_izh(self,mutation_rate):
        for i,groups in enumerate(self.assign_inputs_to_neurons):
            if random.random() < mutation_rate:
                self.assign_inputs_to_neurons[i]=[random.sample(range(100), 5)]
        for i,weights in enumerate(self.weight_spikes):
            for j,weight in enumerate(weights):
                if random.random() < mutation_rate:
                    self.weight_spikes[i][j]=random.random()-0.5
        if random.random() < mutation_rate:
            self.no_outputs += random.choice([-1,1])
            if self.no_outputs > 5:
                self.no_outputs = 5
            elif self.no_outputs < 1:
                self.no_outputs = 1

        if random.random() < mutation_rate:
            self.gain += random.random()-0.5
        if self.gain < -20:
            self.gain = -20
        elif self.gain > 20:
            self.gain = 20

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def duplicate(self):
        new_atom = IzhikevichTransformAtom(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            re=copy.deepcopy(self.re),
                            ri=copy.deepcopy(self.ri),
                            a=copy.deepcopy(self.a),
                            b=copy.deepcopy(self.b),
                            c=copy.deepcopy(self.c),
                            d=copy.deepcopy(self.d),
                            S=copy.deepcopy(self.S),
                            no_outputs=copy.deepcopy(self.no_outputs),
                            assign_inputs_to_neurons=copy.deepcopy(self.assign_inputs_to_neurons),
                            weight_spikes=copy.deepcopy(self.weight_spikes),
                            gain = copy.deepcopy(self.gain)
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["re","ri","a","b","c","d","S","no_outputs",
                        "assign_inputs_to_neurons","weight_spikes",
                        "gain"]:
            self.json[variable] = self.__getattribute__(variable)

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        output += "parameters: {0}\n".format(self.parameters)
        return output
    def deactivate(self,clear=False):
        TransformAtom.deactivate(self,clear=clear)
        # plot(self.output)
        # show()
        # ion()
        self.output = []

if config.LWPR:
    class LWPRTransformAtom(TransformAtom):
        def __init__(self,memory=None,messages=None,message_delays=None,
                        parameters=None,inputs=1,id=None,N=1):
            super(LWPRTransformAtom, self).__init__(memory,messages,
                                            message_delays,id=id)
            self.type = "transform"
            if parameters == None:
                self.parameters = {}
            else:
                self.parameters = parameters
            # LWPR variables
            self.N = N
            self.sending_output = False
            self.inputs = inputs
            self.outputs = inputs
            self.current_max_input = 0
            self.buffer = zeros((self.N, self.inputs))
            self.buffer_flag = 0    # 0 is empty, flag = N is full, can be retrieved
            self.global_model = LWPR(self.inputs, self.outputs)
            self.output_history = []
            # ------- Parameter list-------------
            # -------   The parameter for the LWPR -------
            # 0 penalty 
            # 1 meta learning enable (0,1)
            # 2 init_D  
            # 3 update_D (0,1) Determine whether distance metrics of RF are updated or kept fixed.
            # 4 init_alpha
            # 5 kernel  'Gaussian'(0) or 'BiSquare'(1)
            # 6 meta_rate   default 250
            # ---------   Parameter controlling the local regress ----
            # 7 w_gen  Weight activation threshold default=0.1
            # 8 w_prune Prune the training example with elicit reponse greater than w_prune.
            # 9 init_S2 initial value for the covariance computation. Default = 10^-10
            # 10 add_threshold  The mean square default 0.5 
            # 11 init_lambda   Initial forgetting factor default 0.999
            # 12 final_lambda  Final forget factor default 0.99999
            # 13 tau_lambda   Annealing constant for the forget factor        
            self.paramlist = [1e-06, False, 50, True, 250, 0, 250, 0.1, 1, 1e-10, 0.5, 0.999, 0.99999, 0.9999]
            self.updateParameter(self.paramlist)
            self.reinitialised = True

        # Updata the Atom's parameters by assigning a list 'parameters', which must be a 13x1 array
        def updateParameter(self, parameters):
            self.global_model.init_D = parameters[2]*eye(self.inputs);
            self.global_model.init_alpha = parameters[4]*ones([self.inputs,self.inputs])
            self.global_model.penalty = parameters[0]
            self.global_model.meta = parameters[1]
            self.global_model.update_D = parameters[3]
            if (parameters[5] == 0):
              self.global_model.kernel = 'Gaussian'
            else:
              self.global_model.kernel = 'BiSquare'
            self.global_model.meta_rate = parameters[6]
            
            self.global_model.w_gen = parameters[7]
            self.global_model.w_prune = parameters[8]
            self.global_model.init_S2 = parameters[9]
            self.global_model.add_threshold = parameters[10]
            self.global_model.init_lambda = parameters[11]
            self.global_model.final_lambda = parameters[12]
            self.global_model.tau_lambda = parameters[13]

        # push the data into the buffer (time = t)
        #  push the old data(time = t) to new buffer(time = t+1)
        def updateInputBuffer(self, input_list):

            self.pushdata(array(input_list))
            if self.isBufferFull():
                self.global_model.update(self.buffer[0], self.buffer[self.N-1])
                
        def predict(self, current_state):
            # Tranform the data into numpy.ndarray
            states = array(current_state)
            # print states
            nextstates = self.global_model.predict(states)

            return nextstates

        #  ------------- BUFFER ----------------------
        #  The following function is for operating the 
        #   buffer: push the data in, check if it is full
        #            return the data in the last queue
        def pushdata(self, datalist):
            # print "lwpr [pushdata N]:",self.N
            # print "lwpr [pushdata buffer]:",self.buffer
            for i in arange(self.N-1, 0, -1):
                self.buffer[i] = self.buffer[i-1]

            self.buffer[0] = datalist
            if self.buffer_flag < self.N:
                self.buffer_flag = self.buffer_flag + 1
            
        def isBufferFull(self):
            if self.buffer_flag == self.N:
                
                return True
            else:
                return False
        @_check_active_timer
        def act(self):
            inp = self.get_input()
            # print "lwpr [len inputs]:",len(inp)
            # print "lwpr [inputs]:",inp
            if len(inp) >= self.inputs:
                self.updateInputBuffer(inp[0:self.inputs])
                # print "lwpr [input]:",inp[0:self.inputs]
                # print "lwpr [self.inputs]:",self.inputs
                # print "lwpr [self.outputs]:",self.outputs
                out = list(self.predict(inp[0:self.inputs]))
                # print "lwpr [output]:",out
                if self.sending_output == False:
                    self.output_history.append(out)
                    if array(self.output_history).sum() > 0:
                        self.sending_output = True
                if self.sending_output:
                    # print "sending lwpr message"
                    self.send_message("output",out)
                else:
                    # print "sending initial lwpr message"
                    self.send_message("output",inp[0:self.outputs])

        def get_input(self):
            """
            Reads the output messages sent by the atoms
            connected to this one
            """
            inp = []
            for m in sorted(self.messages):
                in_message = self.memory.get_message(m,'output')
                if in_message is not None:
                    inp += in_message
            return inp

        def mutate(self):
            self.mutate_delays(config.mutation_rate)
            self.mutate_lwpr_params(config.mutation_rate)

        def mutate_lwpr_params(self,mutation_rate):
            if random.random() > mutation_rate:
                self.inputs += random.choice([-1,1])
            if self.inputs > 5:
                self.inputs = 5
            elif self.inputs < 1:
                self.inputs = 1
            self.outputs = self.inputs
            if random.random() > mutation_rate:
                self.N += random.choice([-1,1])
            if self.N > 15:
                self.N = 15
            elif self.N < 1:
                self.N = 1

        def activate(self):
            self.active = True
            if self.reinitialised == False:
                # if there was a mutation we need to reinitialise
                self.sending_output = False
                self.outputs = self.inputs
                self.current_max_input = 0
                self.buffer = zeros((self.N, self.inputs))
                self.buffer_flag = 0    # 0 is empty, flag = N is full, can be retrieved
                self.global_model = LWPR(self.inputs, self.outputs)
                self.output_history = []
                # ------- Parameter list-------------
                # -------   The parameter for the LWPR -------
                # 0 penalty 
                # 1 meta learning enable (0,1)
                # 2 init_D  
                # 3 update_D (0,1) Determine whether distance metrics of RF are updated or kept fixed.
                # 4 init_alpha
                # 5 kernel  'Gaussian'(0) or 'BiSquare'(1)
                # 6 meta_rate   default 250
                # ---------   Parameter controlling the local regress ----
                # 7 w_gen  Weight activation threshold default=0.1
                # 8 w_prune Prune the training example with elicit reponse greater than w_prune.
                # 9 init_S2 initial value for the covariance computation. Default = 10^-10
                # 10 add_threshold  The mean square default 0.5 
                # 11 init_lambda   Initial forgetting factor default 0.999
                # 12 final_lambda  Final forget factor default 0.99999
                # 13 tau_lambda   Annealing constant for the forget factor        
                self.paramlist = [1e-06, False, 50, True, 250, 0, 250, 0.1, 1, 1e-10, 0.5, 0.999, 0.99999, 0.9999]
                self.updateParameter(self.paramlist)
                self.reinitialised = True
            self.send_active_message()

        def deactivate(self,clear=False):
            self.active = False
            self.time_delayed = 0
            self.time_active = 0
            if clear:
                self.memory.clear_all_from_memory(self.id)
                # LWPR parameter clear
                self.sending_output = False
                self.current_max_input = 0
                self.buffer = zeros((self.N, self.inputs))
                self.buffer_flag = 0    # 0 is empty, flag = N is full, can be retrieved
                self.global_model = LWPR(self.inputs, self.outputs)
                self.output_history = []
                self.updateParameter(self.paramlist)
                self.reinitialised = False
            self.send_deactivate_message()

        def duplicate(self):
            new_atom = LWPRTransformAtom(memory=self.memory,
                                messages=[],
                                message_delays=copy.deepcopy(self.message_delays),
                                parameters=copy.deepcopy(self.parameters),
                                N=copy.deepcopy(self.N),
                                inputs = copy.deepcopy(self.inputs)
                                )
            return new_atom

        def to_json(self):
            TransformAtom.to_json(self)
            for variable in ["N","inputs"]:
                self.json[variable] = self.__getattribute__(variable)
        def print_atom(self):
            output=""
            output += "id: {0}\n".format(self.get_id())
            output += "type: {0}\n".format(self.type)
            output += "class: {0}\n".format(self.__class__.__name__)
            output += "messages: {0}\n".format(self.messages)
            output += "message_delays: {0}\n".format(self.message_delays)
            output += "parameters: {0}\n".format(self.parameters)
            output += "N: {0}\n".format(self.N)
            output += "inputs: {0}\n".format(self.inputs)
            return output
class AveragePixelAtom(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None):
        super(AveragePixelAtom, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters

    def avg_rgb(self,image):
        x,y = image.size
        total = float(x*y)
        sum_r, sum_g, sum_b = 0.0, 0.0, 0.0
        for i in range(x):
            for j in range(y):
                r,g,b = image.getpixel((i,j))
                sum_r, sum_g, sum_b = sum_r + r, sum_g + g, sum_b + b
        return [sum_r/total, sum_g/total, sum_b/total]

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        if len(inp) > 0:
            output = self.avg_rgb(inp[0])
            self.send_message("output",output)

    def mutate(self):
        self.mutate_delays(config.mutation_rate)

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def duplicate(self):
        new_atom = AveragePixelAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            )
        return new_atom

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        return output

class SumInputAtom(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,normalise = 1.0):
        super(SumInputAtom, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.normalise = normalise

    def sum_input(self,inp):
        total = 0
        for i in inp:
            total += i
        return total/self.normalise

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        # print "[sum]",inp
        if len(inp) > 0:
            output = self.sum_input(inp)
            self.send_message("output",[output])

    def mutate(self):
        self.mutate_delays(config.mutation_rate)

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def duplicate(self):
        new_atom = SumInputAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            normalise=self.normalise
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["normalise"]:
            self.json[variable] = self.__getattribute__(variable)

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        return output

class OneOverSumInputAtom(SumInputAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,normalise = 1.0):
        super(OneOverSumInputAtom, self).__init__(memory,messages,
                                        message_delays,parameters,id,normalise)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.normalise = normalise

    def one_over_sum_input(self,inp):
        total = 0
        for i in inp:
            total += i
        total = total / self.normalise
        if total == 0:
            total = 0.001
        return total

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        # print "[sum]",inp
        if len(inp) > 0:
            output = self.one_over_sum_input(inp)
            self.send_message("output",[output])

    def mutate(self):
        self.mutate_delays(config.mutation_rate)

    def duplicate(self):
        new_atom = OneOverSumInputAtom(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            normalise=self.normalise
                            )
        return new_atom

class OccurenceCounter(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,threshold = 1.0, function = "max"):
        super(OccurenceCounter, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.threshold = threshold
        self.count = 0
        self.function = function

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        if len(inp) > 0:
            if self.function == "min":
                if inp[0] < self.threshold:
                    self.count += 1
            elif inp[0] > self.threshold:
                self.count += 1
            self.send_message("output",[self.count])


    def mutate(self):
        self.mutate_delays(config.mutation_rate)

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def deactivate(self,clear=False):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        if clear:
            self.memory.clear_all_from_memory(self.id)
            self.count = 0
        self.send_deactivate_message()

    def duplicate(self):
        new_atom = OccurenceCounter(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            threshold=self.threshold,
                            function=copy.deepcopy(self.function)
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["threshold","function"]:
            self.json[variable] = self.__getattribute__(variable)

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        return output

class EventDetection(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,threshold = 1.0, function = "max"):
        super(OccurenceCounter, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.threshold = threshold
        self.event = 0
        self.function = function

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        if len(inp) > 0:
            if self.function == "min":
                if inp[0] < self.threshold:
                    self.event = 1
            elif inp[0] > self.threshold:
                self.event = 1
            self.send_message("output",[self.event])


    def mutate(self):
        self.mutate_delays(config.mutation_rate)

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def deactivate(self,clear=False):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        if clear:
            self.memory.clear_all_from_memory(self.id)
            self.event = 0
        self.send_deactivate_message()

    def duplicate(self):
        new_atom = OccurenceCounter(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            threshold=self.threshold,
                            function=copy.deepcopy(self.function)
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["threshold","function"]:
            self.json[variable] = self.__getattribute__(variable)

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        return output

class MaxOrMinValue(TransformAtom):
    def __init__(self,memory=None,messages=None,message_delays=None,
                    parameters=None,id=None,function = "max"):
        super(MaxOrMinValue, self).__init__(memory,messages,
                                        message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters
        self.value = None
        self.function = function

    @_check_active_timer
    def act(self):
        inp = self.get_input()
        if len(inp) > 0:
            if self.function == "min":
                if inp[0] < self.value:
                    self.value = inp[0]
            elif inp[0] > self.threshold:
                self.value = inp[0]
            self.send_message("output",[self.value])


    def mutate(self):
        self.mutate_delays(config.mutation_rate)

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in sorted(self.messages):
            in_message = self.memory.get_message(m,'output')
            if in_message is not None:
                inp += in_message
        return inp

    def deactivate(self,clear=False):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        if clear:
            self.memory.clear_all_from_memory(self.id)
            self.value = None
        self.send_deactivate_message()

    def duplicate(self):
        new_atom = MaxOrMinValue(memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays),
                            parameters=copy.deepcopy(self.parameters),
                            function=copy.deepcopy(self.function)
                            )
        return new_atom

    def to_json(self):
        TransformAtom.to_json(self)
        for variable in ["threshold","function"]:
            self.json[variable] = self.__getattribute__(variable)

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "class: {0}\n".format(self.__class__.__name__)
        return output

