# https://towardsdatascience.com/how-to-build-your-own-neural-network-from-scratch-in-python-68998a08e4f6

from dna import BrainDNA
import numpy as np
import math
import auxiliary
import random


def sigmoid_derivative(x):
    return 1


class Brain:
    # 0, 1 for target directions, 2 for target type, 3 for self.fertile, 4 for target.fertile
    # 5 for size (- target bigger, + self bigger), 6 for self.health, 7 for multiply_cd
    input_neurons = 3
    hidden_neurons = 4
    output_neurons = 4
    min_weight = -1
    max_weight = 1

    def __init__(self, dna: BrainDNA = BrainDNA()):
        self.dna = dna
        weights = np.array([auxiliary.map(gene, 0, 1, self.min_weight, self.max_weight) for gene in dna.genes])
        level1_neurons = self.input_neurons * self.hidden_neurons
        self.input_weights = np.array(weights[0:level1_neurons]).reshape(self.input_neurons, self.hidden_neurons)
        self.hidden_weights = np.array(weights[level1_neurons:-self.output_neurons])\
            .reshape(self.hidden_neurons, self.output_neurons)
        self.output_weights = np.array(weights[-self.output_neurons:]).reshape(self.output_neurons, 1)

        self.input_layer = np.zeros((1, self.hidden_neurons))
        self.hidden_layer = np.zeros((1, self.hidden_neurons))

    def back_propagate(self, values, y):
        output = self.feedforward(values)

        loss = 2 * (y - output) * self.sigmoid_derivative(output)
        d_output_weights = np.dot(self.hidden_layer.T, loss)
        loss2 = np.dot(loss, self.output_weights.T) * self.sigmoid_derivative(self.hidden_layer)
        d_hidden_weights = np.dot(self.input_layer.T, loss2)
        loss3 = np.dot(loss2, self.hidden_weights.T) * self.sigmoid_derivative(self.input_layer)
        d_input_weights = np.dot(values.T, loss3)

        # print(d_input_weights)
        # print(d_hidden_weights)
        # print(d_output_weights)

        self.input_weights += d_input_weights
        self.hidden_weights += d_hidden_weights
        self.output_weights += d_output_weights
        return output

    def feedforward(self, values):
        self.input_layer = self.sigmoid(np.dot(values, self.input_weights))
        self.hidden_layer = self.sigmoid(np.dot(self.input_layer, self.hidden_weights))
        return self.sigmoid(np.dot(self.hidden_layer, self.output_weights))

    def get_direction(self, values):
        return self.feedforward(values) * 2 * math.pi

    def train(self, n, radius=150):
        size = radius / 2
        for i in range(n):
            x = int((random.random() - 0.5) * size)
            y = int((random.random() - 0.5) * size)

            # values = np.zeros((1, 8))
            # values[0, 0] = x
            # values[0, 1] = y
            # values[0, 2] = 1
            values = np.array([[x, y, 1]])
            result = np.array([(math.atan2(y, x) + math.pi) / (math.pi * 2)])

            real_result = self.back_propagate(values, result)

        weights = np.concatenate((self.input_weights.flatten(), self.hidden_weights.flatten(), self.output_weights.flatten()))
        max_weight = max(weights)
        min_weight = min(weights)
        self.dna.genes = np.array([auxiliary.map(weight, min_weight, max_weight, 0, 1) for weight in weights])

    @classmethod
    def get_number_of_neurons(cls):
        return cls.input_neurons * cls.hidden_neurons + cls.hidden_neurons * cls.output_neurons + cls.output_neurons

    @classmethod
    def sigmoid(cls, x):
        if np.isscalar(x):
            return 1 / (1 + np.exp(-x))

        mask = np.full(x.shape, True)
        mask[x <= -6] = False
        mask[x >= 6] = False
        x[x <= -6] = 0.0
        x[x >= 6] = 1.0
        x = x.copy()
        np.exp(-x, out=x, where=mask)

        return 1 / (1 + x)

    @classmethod
    def sigmoid_derivative(cls, x):
        s = cls.sigmoid(x)
        ds = s * (1 - s)
        return ds
