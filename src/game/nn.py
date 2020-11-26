import numpy as np

class NN():

    def __init__(self, layers=1):
        
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
        hidden_size = 20

        # The amount of layers inbetween can vary, but for
        # now we'll do just one.
        self.weights = [
            np.random.uniform(low=-1, high=1, size=(input_size, hidden_size)),
            np.random.uniform(low=-1, high=1, size=(hidden_size, output_size)),
        ]

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