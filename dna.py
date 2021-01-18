# reading https://natureofcode.com/book/chapter-9-the-evolution-of-code/

import numpy as np


# I. CREATE A POPULATION

# DNA (genes) - a set of properties that describe creature's behaviour

# important distinction
# genotype - data structure to store object's properties
#            that is passed from generation to generation
# phenotype - what behaviour/ features depend on genotype
#             (expression of genotype)


# TO DO:

# a class to store genetic information of a member of population
# genotype
class DNA:
    mutation_rate = 0.05  # probability of gene mutation
    # gene_length = 6  # first 3 genes: r, g, b (color), gene[4] - speed, gene[5] - size
    gene_length = 7
    def __init__(self, genes=np.zeros(gene_length)):
        self.genes = genes

    def copy(self):
        genes_copy = self.genes.copy()
        return DNA(genes_copy)

    # II. SELECTION
    # in our case two creatures will reproduce with certain probability
    # if the bump into each other

    # III. REPRODUCTION
    # 1. crossover
    # single point crossover
    def crossover(self, partner):
        child = DNA()
        midpoint = np.random.randint(child.gene_length)
        child.genes[midpoint:] = self.genes[midpoint:]
        child.genes[:midpoint] = partner.genes[:midpoint]
        return child

    # 2. mutation

    def mutation(self):
        for i, _ in enumerate(self.genes):
            if np.random.uniform() < self.mutation_rate:
                self.genes[i] = np.random.uniform()
