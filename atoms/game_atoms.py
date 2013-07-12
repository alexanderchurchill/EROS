from core.atom import *
from core.atom import _check_active_timer

class OneOverSumGameAtom(GameAtom):
    """Game atom to calculate 1 / sum of input history"""
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(OneOverSumGameAtom, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )

    def act(self):
        inp = self.get_input()
        self.state.append(inp)
        self.send_message("output",[self.get_fitness()])

    def get_fitness(self):
        """
        This is currently performing a sum
        """
        fitness = 0.0
        for time_step in self.state:
            for record in time_step:
                fitness += record
        return 1/fitness

    def duplicate(self):
        new_atom = OneOverSumGameAtom(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

class MaxSensorGame(GameAtom):
    """A simple maximise sensory input game"""
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(MaxSensorGame, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )

    def act(self):
        inp = self.get_input()
        self.state.append(inp)
        # print self.state
        self.send_message("output",[self.get_fitness()])
        # print "output",[self.get_fitness()]

    def get_fitness(self):
        """
        This is currently performing a sum
        """
        fitness = 0
        for time_step in self.state:
            for record in time_step:
                fitness += record
        return fitness

    def duplicate(self):
        new_atom = MaxSensorGame(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

class DistanceGameAtom(GameAtom):
    """
    Records the distance at various way points
    """
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(DistanceGameAtom, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )

    def act(self):
        inp = self.get_input()
        self.state.append(inp)
        self.send_message("output",[self.get_fitness()])

    def get_distance_travelled(self):
        initial_x = self.state[0][0]
        initial_y = self.state[0][1]
        final_x = self.state[-1][0]
        final_y = self.state[-1][1]
        distance = math.sqrt(((final_x - initial_x)**2)
                                + ((final_y - initial_y)**2))
        return distance

    def get_fitness(self):
        """
        This is currently performing a sum
        """
        fitness = self.get_distance_travelled()
        return fitness

    def duplicate(self):
        new_atom = DistanceGameAtom(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom

    def return_trajectory_data(self):
        x = []
        y = []
        for i in range(0,len(self.state)):
            x.append(self.state[i][0])
            y.append(self.state[i][1])
        return [x,y]
    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

class PathIntegrationDistance(GameAtom):
    """
    Records the distance at various way points
    """
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(PathIntegrationDistance, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )

    def act(self):
        inp = self.get_input()
        self.state.append(inp)
        self.send_message("output",[self.get_fitness()])

    def get_distance_travelled(self):
        total_distance = 0
        if len(self.state) > 1:
            for i in range(1,len(self.state)):
                initial_x = self.state[i-1][0]
                initial_y = self.state[i-1][1]
                final_x = self.state[i][0]
                final_y = self.state[i][1]
                distance = math.sqrt(((final_x - initial_x)**2)
                                        + ((final_y - initial_y)**2))
                total_distance += distance
        return total_distance

    def get_fitness(self):
        """
        This is currently performing a sum
        """
        fitness = self.get_distance_travelled()
        return fitness

    def duplicate(self):
        new_atom = PathIntegrationDistance(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom

class TimeNotMovingAtom(GameAtom):
    """
    Records the distance at various way points
    """
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(TimeNotMovingAtom, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )

    def act(self):
        inp = self.get_input()
        self.state.append(inp)
        self.send_message("output",[self.get_fitness()])

    def get_distance_travelled(self):
        time_steps = 1
        if len(self.state) > 1:
            for i in range(1,len(self.state)):
                initial_x = self.state[i-1][0]
                initial_y = self.state[i-1][1]
                final_x = self.state[i][0]
                final_y = self.state[i][1]
                distance = math.sqrt(((final_x - initial_x)**2)
                                        + ((final_y - initial_y)**2))
                if distance < 0.001:
                    time_steps += 1
        return time_steps

    def get_fitness(self):
        """
        This is currently performing a sum
        """
        fitness = self.get_distance_travelled()
        return fitness

    def duplicate(self):
        new_atom = TimeNotMovingAtom(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom

class LastOutputGameAtom(GameAtom):
    """
    Sum of output of other game atoms
    """
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(LastOutputGameAtom, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )

    def act(self):
        inp = self.get_input()
        self.state.append(inp)
        self.send_message("output",[self.get_fitness()])
        # print "self.state [last]",[self.state[-1]]
        # print "output [last]",[self.get_fitness()]

    def get_fitness(self):
        """
        This is currently performing a sum
        """
        fitness = 0.0
        for record in self.state[-1]:
            fitness += record
        return fitness

    def duplicate(self):
        new_atom = LastOutputGameAtom(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

class PCAGame(GameAtom):
    """A simple NAO game"""
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(NaoPCAGame, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )
        self.scores = []
    def act(self):
        inp = self.get_input()
        self.state.append(inp)

    def get_fitness(self):
        """
        This is currently performing a sum
        """
        state_t = array(self.state)
        coeff, score, latent = self.princomp(state_t)
        self.coeff = coeff
        first_dimension = score[0]
        fitness = abs(latent).sum()
        self.scores = score
        return fitness

    def duplicate(self):
        new_atom = PCAGame(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

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
     [latent,coeff] = linalg.eig(cov(M)) # attention:not always sorted
     score = dot(coeff.T,M) # projection of the data in the new space
     return coeff,score,latent

    def duplicate(self):
        new_atom = NaoPCAGame(
                            memory=self.memory,
                            messages=[],
                            message_delays=copy.deepcopy(self.message_delays)
                            )
        return new_atom
