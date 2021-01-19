# https://towardsdatascience.com/how-to-build-your-own-neural-network-from-scratch-in-python-68998a08e4f6

from dna import BrainDNA
import numpy as np
import math


class Brain:
    # 0, 1 for target directions, 2 for target type, 3 for self.fertile, 4 for target.fertile
    # 5 for size (- target bigger, + self bigger), 6 for self.health, 7 for multiply_cd
    input_neurons = 8
    hidden_neurons = 4

    def __init__(self, dna: BrainDNA = BrainDNA()):
        self.dna = dna
        self.input_weights = np.array(dna.genes[0:self.input_neurons * self.hidden_neurons]).reshape(self.input_neurons, self.hidden_neurons)
        self.hidden_weights = np.array(dna.genes[-self.hidden_neurons:])

    def feedforward(self, values):
        layer1 = self.sigmoid(np.dot(values, self.input_weights))
        return self.sigmoid(np.dot(layer1, self.hidden_weights))

    def get_direction(self, values):
        return self.feedforward(values) * 2 * math.pi

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
