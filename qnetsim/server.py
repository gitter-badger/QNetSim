from __future__ import division
from random import random, seed, expovariate, uniform, triangular, gammavariate, gauss, lognormvariate, weibullvariate
from datetime import datetime
import os
from csv import writer
import yaml
import shutil
import networkx as nx

class Server:
    """
    A class to contain server information
    """
    def __init__(self, node, id_number):
        """
        Initialise the server object
            >>> from simulation import Simulation
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = Q.transitive_nodes[0] 
            >>> S = Server(N, 1)
            >>> S.node.id_number
            1
            >>> S.id_number
            1
        """
        self.node = node
        self.id_number = id_number
        self.cust = False
        self.busy = False

    def __repr__(self):
        """
        Represents the Server instance as a string

            >>> from simulation import Simulation
            >>> Q = Simulation('datafortesting/logs_test_for_simulation/')
            >>> N = Q.transitive_nodes[0] 
            >>> S = Server(N, 1)
            >>> S
            Server 1 at Node 1

        """
        return 'Server %s at Node %s' % (self.id_number, self.node.id_number)