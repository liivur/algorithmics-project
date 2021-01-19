# https://towardsdatascience.com/how-to-build-your-own-neural-network-from-scratch-in-python-68998a08e4f6

from dna import BrainDNA
import numpy as np
import math
import auxiliary


class Brain:
    # 0, 1 for target directions, 2 for target type, 3 for self.fertile, 4 for target.fertile
    # 5 for size (- target bigger, + self bigger), 6 for self.health, 7 for multiply_cd
    input_neurons = 3
    hidden1_neurons = 4
    hidden2_neurons = 4
    min_weight = -1
    max_weight = 1

    def __init__(self, dna: BrainDNA = BrainDNA()):
        self.dna = dna
        weights = np.array([auxiliary.map(gene, 0, 1, self.min_weight, self.max_weight) for gene in dna.genes])
        level1_neurons = self.input_neurons * self.hidden1_neurons
        self.input_weights = np.array(weights[0:level1_neurons]).reshape(self.input_neurons, self.hidden1_neurons)
        self.hidden1_weights = np.array(weights[level1_neurons:-self.hidden2_neurons])\
            .reshape(self.hidden1_neurons, self.hidden2_neurons)
        self.hidden2_weights = np.array(weights[-self.hidden2_neurons:])

    def feedforward(self, values):
        layer1 = self.sigmoid(np.dot(values, self.input_weights))
        layer2 = self.sigmoid(np.dot(layer1, self.hidden1_weights))
        return self.sigmoid(np.dot(layer2, self.hidden2_weights))

    def get_direction(self, values):
        return self.feedforward(values) * 2 * math.pi

    @classmethod
    def get_number_of_neurons(cls):
        return cls.input_neurons * cls.hidden1_neurons + cls.hidden1_neurons * cls.hidden2_neurons + cls.hidden2_neurons

    @staticmethod
    def sigmoid(x):
        if np.isscalar(x):
            return 1 / (1 + np.exp(-x))

        mask = np.full(x.shape, True)
        mask[x <= -6] = False
        mask[x >= 6] = False
        # print(x, mask)
        x[x <= -6] = 0.0
        x[x >= 6] = 1.0
        np.exp(-x, out=x, where=mask)
        # print(x)
        # res = 1 / (1 + out)

        return 1 / (1 + x)
