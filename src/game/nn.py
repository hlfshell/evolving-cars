import numpy as np
from random import uniform

HIDDEN_LAYER_SIZE = 20

class NN():

    def __init__(self, weights=None):
        
        # The input and output size of our neural network
        # is locked. We are going to have 7 inputs:
        # 1. speed
        # 2.current rotation
        # 3-7: the 5 measured distances
        # and we'll have a total of 4 outputs:
        # 1. acceleration
        # 2. deacceleration
        # 3+4. turn left (soft and hard)
        # 5+6. turn right (soft and hard)

        # hidden layer size
        input_size = 7
        output_size = 6

        # The amount of layers inbetween can vary, but for
        # now we'll do just one.
        if weights is None:
            self.weights = [
                np.random.uniform(low=-1, high=1, size=(input_size, HIDDEN_LAYER_SIZE)),
                np.random.uniform(low=-1, high=1, size=(HIDDEN_LAYER_SIZE, output_size)),
            ]
        else:
            self.weights = weights

    def infer(self, speed, rotation, distances):
        # Create an input layer from the data
        input = np.array([speed, rotation, distances[-60], distances[-30], distances[0], distances[30], distances[60]])

        hidden = relu(np.dot(input, self.weights[0]))

        output = sigmoid(np.dot(hidden, self.weights[1]))

        return output

# standard sigmoid activation function
def sigmoid(input):
    return 1/(1+np.exp(-input))

# Standard relu
def relu(x):
    return (x > 0) * x

def mate(a : NN, b : NN, a_parentage : float =0.5, mutation : float = 0.05) -> NN:
    weights = []
    for index_weight, weight in enumerate(a.weights):
        new_weight = np.copy(weight)

        # weight layers are size (input, output), so we have
        # to go through two loops on it
        for index_outer, new_weights in enumerate(weight):
            for index_inner, value in enumerate(new_weights):
                # determine - parent a, parent b, or mutation?
                if uniform(0, 1) < mutation:
                    new_weight[index_outer][index_inner] = uniform(-1, 1)
                elif uniform(0, 1) < a_parentage: #parent A?
                    new_weight[index_outer][index_inner] = value
                else: # or parent B?
                    new_weight[index_outer][index_inner] = b.weights[index_weight][index_outer][index_inner]

        weights.append(new_weight)

    return NN(weights=weights)