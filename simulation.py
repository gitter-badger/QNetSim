"""
A simulation of a Queueing network
"""

from __future__ import division
from random import random, seed, expovariate
from numpy import mean as np_mean

def mean(lst):
    """
    A function to find the mean of a list, returns false if empty

    Tests with a full list.
        >>> AList = [6, 6, 4, 6, 8]
        >>> mean(AList)
        6.0

     Tests with an empty list.
        >>> AnotherList = []
        >>> mean(AnotherList)
        False
    """

    if len(lst) == 0:
        return False
    return np_mean(lst)

class DataRecord:
    """
    A class for a data record
    """
    def __init__(self, arrival_date, service_time, exit_date, node):
        """
        An example of a data record instance.
            >>> r = DataRecord(2, 3, 5, 3)
            >>> r.arrival_date
            2
            >>> r.wait
            0
            >>> r.service_date
            2
            >>> r.service_time
            3
            >>> r.exit_date
            5
            >>> r.node
            3

        Another example of a data record instance.
            >>> r = DataRecord(5.7, 2.1, 8.2, 1)
            >>> r.arrival_date
            5.7
            >>> round(r.wait, 5)
            0.4
            >>> r.service_date
            6.1
            >>> r.service_time
            2.1
            >>> r.exit_date
            8.2
            >>> r.node
            1

        If parameters don't make sense, errors occur.
            >>> r = DataRecord(4, 2.5, 3, 3)
            Traceback (most recent call last):
            ...
            ValueError: Arrival date should preceed exit date

            >>> r = DataRecord(4, -2, 7, 1)
            Traceback (most recent call last):
            ...
            ValueError: Service time should be positive

        """
        if exit_date < arrival_date:
            raise ValueError('Arrival date should preceed exit date')

        if service_time < 0:
            raise ValueError('Service time should be positive')

        self.arrival_date = arrival_date
        self.service_time = service_time
        self.exit_date = exit_date
        self.service_date = exit_date - service_time
        self.wait = self.service_date - arrival_date
        self.node = node

class Individual:
    """
    Class for an individual
    """
    def __init__(self, id_number, number_of_nodes, customer_class=0):
        """
        Initialise an individual

        An example of an Individual instance.
            >>> i = Individual(22, 3)
            >>> i.in_service
            False
            >>> i.end_service_date
            False
            >>> i.id_number
            22
            >>> i.data_records
            {}
            >>> i.customer_class
            0

        Another example of an individual instance.
            >>> i = Individual(5, 1, 2)
            >>> i.in_service
            False
            >>> i.end_service_date
            False
            >>> i.id_number
            5
            >>> i.data_records
            {}
        """
        self.in_service = False
        self.end_service_date = False
        self.id_number = id_number
        self.data_records = {}
        self.number_of_visits = {i+1:0 for i in range(number_of_nodes)}
        self.customer_class = customer_class

    def __repr__(self):
        """
        Represents an Individual instance as a string

        An example of how an intance in represented.
            >>> i = Individual(3, 6)
            >>> i
            Individual 3

        Another example of how an individual is represented.
            >>> i = Individual(93, 2)
            >>> i
            Individual 93

        Although individuals should be represented by unique integers, they can be called anything.
            >>> i = Individual('twelve', 2)
            >>> i
            Individual twelve
        """
        return 'Individual %s' % self.id_number

class Node:
    """
    Class for a node on our network
    """
    def __init__(self, id_number, simulation):
        """
        Initialise a node.

        An example of initialising a node.
            >>> Q = Q = Simulation([[5, 3]], [[10, 10]], [4, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> N = Node(1, Q)
            >>> N.mu
            [10]
            >>> N.c
            4
            >>> N.transition_row
            [[0.2, 0.5]]
            >>> N.next_event_time
            50
            >>> N.individuals
            []
            >>> N.id_number
            1
            >>> N.cum_transition_row
            [[0.2, 0.7]]

        Another example.
            >>> Q = Simulation([[5, 3]], [[10, 10]], [4, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> N = Q.transitive_nodes[1]
            >>> N.mu
            [10]
            >>> N.c
            1
            >>> N.transition_row
            [[0.4, 0.4]]
            >>> N.individuals
            []
            >>> N.id_number
            2
            >>> N.next_event_time
            50
            >>> N.cum_transition_row
            [[0.4, 0.8]]
            >>> N.simulation.max_simulation_time
            50

        A node's id number must conform with how many nodes are in the simulation.
            >>> Q = Simulation([[5, 3]], [[10, 10]], [4, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> N = Node(3, Q)
            Traceback (most recent call last):
            ...
            IndexError: list index out of range
        """

        self.simulation = simulation
        self.mu = [self.simulation.mu[cls][id_number-1] for cls in range(len(self.simulation.mu))]
        self.c = self.simulation.c[id_number-1]
        self.transition_row = [self.simulation.transition_matrix[j][id_number-1] for j in range(len(self.simulation.transition_matrix))]
        self.individuals = []
        self.id_number = id_number
        self.cum_transition_row = self.find_cum_transition_row()
        self.next_event_time = self.simulation.max_simulation_time
        self.numbers_in_node = [[0.0,0]]

    def find_cum_transition_row(self):
        """
        Finds the cumulative transition row for the node

        An exmaple of finding the cumulative transition row of a node.
            >>> Q = Simulation([[2, 1, 2, 2, 1, 2]], [[6, 3, 6, 6, 6, 2]], [1, 2, 2, 2, 2, 2], [[[0.125, 0.200, 0.250, 0.150, 0.170, 0.1], [0.125, 0.200, 0.250, 0.150, 0.170, 0.1], [0.125, 0.200, 0.250, 0.150, 0.170, 0.1], [0.125, 0.200, 0.250, 0.150, 0.170, 0.1], [0.125, 0.200, 0.250, 0.150, 0.170, 0.1], [0.125, 0.200, 0.250, 0.150, 0.170, 0.1]]], 70)
            >>> N = Node(1, Q)
            >>> N.cum_transition_row
            [[0.125, 0.325, 0.575, 0.725, 0.895, 0.995]]

        Another example.
            >>> Q = Simulation([[4, 5]], [[7, 8]], [2, 1], [[[0.2, 0.5], [0.1, 0.7]]], 100)
            >>> N = Q.nodes[1]
            >>> N.cum_transition_row
            [[0.2, 0.7]]
        """

        cum_transition_row = []
        for cls in range(len(self.transition_row)):
            sum_p = 0
            cum_transition_row.append([])
            for p in self.transition_row[cls]:
                sum_p += p
                cum_transition_row[cls].append(sum_p)
        return cum_transition_row

    def __repr__(self):
        """
        Representation of a node::

        An example of how a node is represented.
            >>> Q = Simulation([[5, 4]], [[8, 9]], [2, 2], [[[0.2, 0.5], [0.1, 0.7]]], 100)
            >>> N = Node(1, Q)
            >>> N
            Node 1

        Another example.
            >>> Q = Simulation([[5, 2, 1]], [[8, 8, 3]], [1, 2, 1], [[[0.2, 0.1, 0.1], [0.1, 0.4, 0.3], [0.3, 0.1, 0.1]]], 300)
            >>> N = Q.transitive_nodes[2]
            >>> N
            Node 3

        A node cannot exist without a simulation.
            >>> N = Node(2, False)
            Traceback (most recent call last):
            ...
            AttributeError: 'bool' object has no attribute 'mu'
        """
        return 'Node %s' % self.id_number

    def release(self):
        """
        Update node when a service happens.

        Once an individual is released, his exit date will be updated.
            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> N = Q.transitive_nodes[0]
            >>> i = Individual(2, 1)
            >>> i.arrival_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'arrival_date'
            >>> i.service_time
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'service_time'
            >>> N.accept(i, 1)
            >>> i.arrival_date
            1
            >>> round(i.service_time, 5)
            0.01443
            >>> i.data_records[N.id_number]
            Traceback (most recent call last):
            ...
            KeyError: 1
            >>> i.exit_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> N.release()
            >>> round(i.exit_date, 5)
            1.01443
            >>> i.data_records[N.id_number][0].wait
            0.0

        Another example of an individual being released.
            >>> seed(6)
            >>> Q = Simulation([[7, 4]], [[9, 11]], [2, 1], [[[.3, .2], [.1, .4]]], 60)
            >>> N = Q.transitive_nodes[0]
            >>> i = Individual(4, 1)
            >>> i.arrival_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'arrival_date'
            >>> i.service_time
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'service_time'
            >>> N.accept(i, 3)
            >>> i.arrival_date
            3
            >>> round(i.service_time, 5)
            0.17519
            >>> i.data_records[N.id_number]
            Traceback (most recent call last):
            ...
            KeyError: 1
            >>> i.exit_date
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> N.release()
            >>> round(i.exit_date, 5)
            3.17519
            >>> i.data_records[N.id_number][0].wait
            0.0

        A node can only release if it has an individual to release.
            >>> seed(2)
            >>> Q = Simulation([[2]], [[3]], [1], [[[0]]], 20)
            >>> N = Q.transitive_nodes[0]
            >>> N.release()
            Traceback (most recent call last):
            ...
            IndexError: pop from empty list
        """
        next_individual = self.individuals.pop(0)
        self.count_down(self.next_event_time)

        next_individual.exit_date = self.next_event_time
        self.write_individual_record(next_individual)

        next_node = self.next_node(next_individual.customer_class)
        next_node.accept(next_individual, self.next_event_time)
        self.update_next_event_date()

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

        Accepting an individual updates a nodes next event date and appends that individual to its list of customers.
            >>> seed(1)
            >>> Q = Simulation([[7, 4]], [[9, 11]], [2, 1], [[[.3, .2], [.1, .4]]], 60)
            >>> N = Node(1, Q)
            >>> next_individual = Individual(5, 3)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> next_individual.arrival_date
            1
            >>> round(next_individual.service_time, 5)
            0.01603
            >>> round(N.next_event_time, 5)
            1.01603
            >>> N.accept(Individual(10, 3), 1)
            >>> round(N.next_event_time, 5)
            1.01603

        Another example of accepting an individual.
            >>> seed(4)
            >>> Q = Simulation([[5, 3, 2]], [[9, 6, 8]], [2, 2, 1], [[[.3, .2, .1], [.1, .4, .3], [.7, .1, .1]]], 60)
            >>> N = Node(3, Q)
            >>> next_individual = Individual(6, 1)
            >>> N.accept(next_individual, 8.2)
            >>> N.individuals
            [Individual 6]
            >>> next_individual.arrival_date
            8.2
            >>> round(next_individual.service_time, 5)
            0.03366
            >>> round(N.next_event_time, 5)
            8.23366
            >>> N.accept(Individual(10, 1), 1)
            >>> round(N.next_event_time, 5)
            8.23366

        """
        next_individual.arrival_date = current_time
        next_individual.service_time = expovariate(self.mu[next_individual.customer_class])

        if len(self.individuals) < self.c:
            next_individual.end_service_date = current_time + next_individual.service_time
        else:
            next_individual.end_service_date = self.individuals[-self.c].end_service_date + next_individual.service_time

        self.include_individual(next_individual)
        self.count_up(current_time)
        self.update_next_event_date()

    def find_index_for_individual(self, individual):
        """
        Returns the index of the position that the new individual will take


            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [4, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(10)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            >>> ind = Individual(10, 2)
            >>> ind.end_service_date = 17
            >>> node.find_index_for_individual(ind)
            -2
            >>> ind = Individual(11, 2)
            >>> ind.end_service_date = 67
            >>> node.find_index_for_individual(ind)
            False

            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [5, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(2)]
            >>> end_date = 1
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 4
            >>> [ind.end_service_date for ind in node.individuals]
            [1, 5]
            >>> ind = Individual(3, 2)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            -1

            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [4, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(3)]
            >>> end_date = 1
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 4
            >>> [ind.end_service_date for ind in node.individuals]
            [1, 5, 9]
            >>> ind = Individual(3, 2)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            -2

            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [400, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(3)]
            >>> end_date = 1
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 4
            >>> [ind.end_service_date for ind in node.individuals]
            [1, 5, 9]
            >>> ind = Individual(3, 2)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            -2

            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [400, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = []
            >>> end_date = 1
            >>> [ind.end_service_date for ind in node.individuals]
            []
            >>> ind = Individual(3, 2)
            >>> ind.end_service_date = 3
            >>> node.find_index_for_individual(ind)
            False
        """
        for i, ind in enumerate(self.individuals[-self.c:]):
                if individual.end_service_date < ind.end_service_date:
                    return -min(self.c,len(self.individuals)) + i
        return False

    def include_individual(self, individual):
        """
        Inserts that individual into the correct position in the list of individuals.

            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [4, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(10)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4, Individual 5, Individual 6, Individual 7, Individual 8, Individual 9]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            >>> ind = Individual(10, 2)
            >>> ind.end_service_date = 17
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4, Individual 5, Individual 6, Individual 7, Individual 10, Individual 8, Individual 9]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12, 14, 16, 17, 18, 20]

            TESTS 2
            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [7, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(3)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6]
            >>> ind = Individual(10, 2)
            >>> ind.end_service_date = 17
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 10]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 17]

            TESTS 3
            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [8, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals = [Individual(i, 2) for i in range(6)]
            >>> end_date = 2
            >>> for ind in node.individuals:
            ...     ind.end_service_date = end_date
            ...     end_date += 2
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 3, Individual 4, Individual 5]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 8, 10, 12]
            >>> ind = Individual(33, 2)
            >>> ind.end_service_date = 7
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 0, Individual 1, Individual 2, Individual 33, Individual 3, Individual 4, Individual 5]
            >>> [ind.end_service_date for ind in node.individuals]
            [2, 4, 6, 7, 8, 10, 12]

            TESTS 3
            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [2, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals
            []
            >>> [ind.end_service_date for ind in node.individuals]
            []
            >>> ind = Individual(1, 2)
            >>> ind.end_service_date = 3.5
            >>> node.include_individual(ind)
            >>> node.individuals
            [Individual 1]
            >>> [ind.end_service_date for ind in node.individuals]
            [3.5]
        """
        index = self.find_index_for_individual(individual)
        if index:
            self.individuals.insert(self.find_index_for_individual(individual), individual)
        else:
            self.individuals.append(individual)



    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

        A example of finding the next event time before and after accepting an individual.
            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.individuals
            []
            >>> node.next_event_time
            50
            >>> node.update_next_event_date()
            >>> node.next_event_time
            50
            >>> ind = Individual(10, 2)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> round(node.next_event_time, 5)
            1.01443

        And again.
            >>> seed(8)
            >>> Q = Simulation([[3, 3, 1]], [[6, 12, 2]], [1, 1, 3], [[[.2, .4, .4], [.4, .4, .1], [.1, .1, .1]]], 40)
            >>> node = Q.transitive_nodes[1]
            >>> node.individuals
            []
            >>> node.next_event_time
            40
            >>> node.update_next_event_date()
            >>> node.next_event_time
            40
            >>> ind = Individual(2, 3)
            >>> node.accept(ind, 1)
            >>> node.update_next_event_date()
            >>> round(node.next_event_time, 5)
            1.02142
        """
        if len(self.individuals) == 0:
            self.next_event_time = self.simulation.max_simulation_time
        else:
            self.next_event_time = self.individuals[0].end_service_date

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.

        An example showing a node choosing both nodes and exit node randomly.
            >>> seed(6)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.35, .35], [.4, .4]]], 50)
            >>> node = Q.transitive_nodes[0]
            >>> node.next_node(0)
            Exit Node
            >>> node.next_node(0)
            Exit Node
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 1
            >>> node.next_node(0)
            Node 1
            >>> node.next_node(0)
            Node 2

        Another example.
            >>> seed(54)
            >>> Q = Simulation([[4, 5, 6]], [[12, 5, 9]], [1, 3, 2], [[[0.1, 0.2, 0.5], [0.4, 0.2, 0.2], [0.3, 0.3, 0.3]]], 80)
            >>> node = Q.transitive_nodes[2]
            >>> node.next_node(0)
            Exit Node
            >>> node.next_node(0)
            Node 1
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Exit Node
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2
            >>> node.next_node(0)
            Node 2

        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row[customer_class])):
            if rnd_num < self.cum_transition_row[customer_class][p]:
                return self.simulation.transitive_nodes[p]
        return self.simulation.nodes[-1]

    def write_individual_record(self, individual):
        """
        Write a data record for an individual:

        - Arrival date
        - Wait
        - Service date
        - Service time
        - Exit date

        An example showing the data records written; can only write records once an exit date has been determined.
            >>> seed(7)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.35, .35], [.4, .4]]], 50)
            >>> N = Q.transitive_nodes[0]
            >>> ind = Individual(6, 2)
            >>> N.accept(ind, 3)
            >>> N.write_individual_record(ind)
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> ind.exit_date = 7
            >>> N.write_individual_record(ind)
            >>> ind.data_records[1][0].arrival_date
            3
            >>> round(ind.data_records[1][0].wait, 5)
            3.96087
            >>> round(ind.data_records[1][0].service_date, 5)
            6.96087
            >>> round(ind.data_records[1][0].service_time, 5)
            0.03913
            >>> ind.data_records[1][0].exit_date
            7
            >>> ind.data_records[1][0].node
            1

        Another example.
            >>> seed(12)
            >>> Q = Simulation([[2, 1]], [[6, 3]], [1, 2], [[[.4, .3], [.2, .7]]], 70)
            >>> N = Q.transitive_nodes[0]
            >>> ind = Individual(28, 2)
            >>> N.accept(ind, 6)
            >>> N.write_individual_record(ind)
            Traceback (most recent call last):
            ...
            AttributeError: Individual instance has no attribute 'exit_date'
            >>> ind.exit_date = 9
            >>> N.write_individual_record(ind)
            >>> ind.data_records[1][0].arrival_date
            6
            >>> round(ind.data_records[1][0].wait, 5)
            2.89274
            >>> round(ind.data_records[1][0].service_date, 5)
            8.89274
            >>> round(ind.data_records[1][0].service_time, 5)
            0.10726
            >>> ind.data_records[1][0].exit_date
            9
            >>> ind.data_records[1][0].node
            1

        """
        record = DataRecord(individual.arrival_date, individual.service_time, individual.exit_date, self.id_number)
        individual.number_of_visits[self.id_number] += 1
        if self.id_number in individual.data_records:
            individual.data_records[self.id_number].append(record)
        else:
            individual.data_records[self.id_number] = [record]

    def count_up(self, current_time):
        """
        Records the time that the node gains an individual and the current number of individuals

        An example showing the attribute numbers_in_node before and after count_up.
            >>> Q = Simulation([[2, 1, 4]], [[6, 3, 1]], [1, 2, 7], [[[.4, .3, .1], [.2, .7, .0], [.2, .2, .2]]], 70)
            >>> N = Node(1, Q)
            >>> N.numbers_in_node
            [[0.0, 0]]
            >>> N.count_up(4.2)
            >>> N.numbers_in_node
            [[0.0, 0], [4.2, 1]]
        """
        self.numbers_in_node.append([current_time, self.numbers_in_node[-1][1] + 1])

    def count_down(self,current_time):
        """
        Recored the time that the node loses an individual and the current number of individuals

        An example showing the attribute numbers_in_node before and after count_down.
            >>> Q = Simulation([[2, 1]], [[6, 3]], [1, 2], [[[.4, .3], [.2, .7]]], 70)
            >>> N = Node(2, Q)
            >>> N.numbers_in_node = [[0.0, 0], [0.3, 1], [0.5, 2]]
            >>> N.count_down(0.9)
            >>> N.numbers_in_node
            [[0.0, 0], [0.3, 1], [0.5, 2], [0.9, 1]]
        """
        self.numbers_in_node.append([current_time, self.numbers_in_node[-1][1] - 1])



class ArrivalNode:
    """
    Class for the arrival node on our network
    """
    def __init__(self, simulation):
        """
        Initialise a node.

        Here is an example::
            >>> Q = Simulation([[5, 10, 25]], [[20, 30, 30]], [1, 2, 2], [[[0.1, 0.3, 0.1], [0.2, 0.2, 0.2], [0.6, 0.1, 0.1]]], 100)
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            40
            >>> N.transition_row_given_class
            [[0.125, 0.25, 0.625]]
            >>> N.next_event_time
            0
            >>> N.number_of_individuals
            0
            >>> N.cum_transition_row
            [[0.125, 0.375, 1.0]]
            >>> N.cum_class_probs
            [1.0]

        And another example::
            >>> Q = Simulation([[3, 2, 3]], [[4, 5, 3]], [2, 1, 2], [[[.1, .1, .1], [.3, .4, .1], [.2, .2, .5]]], 100)
            >>> N = Q.nodes[0]
            >>> N.lmbda
            8
            >>> N.transition_row_given_class
            [[0.375, 0.25, 0.375]]
            >>> N.cum_transition_row
            [[0.375, 0.625, 1.0]]
            >>> N.simulation.max_simulation_time
            100
        """

        self.simulation = simulation
        self.lmbda = self.simulation.overall_lmbda
        self.class_probs = self.simulation.class_probs
        self.transition_row_given_class = self.simulation.node_given_class_probs
        self.next_event_time = 0
        self.number_of_individuals = 0
        self.cum_transition_row = self.find_cumulative_transition_row()
        self.cum_class_probs = self.find_cumulative_class_probs()

    def find_cumulative_transition_row(self):
        """
        Finds the cumulative transition row for the arrival node

        An example of finding the cumulative transition row of an arrival node.
            >>> Q = Simulation([[3, 5, 7, 4, 5, 1]], [[6, 7, 8, 8, 6, 5]], [1, 2, 2, 1, 2, 2], [[[0.1, 0.1, 0.1, 0.1, 0.1, 0.1], [0.1, 0.1, 0.1, 0.1, 0.1, 0.1], [0.1, 0.1, 0.1, 0.1, 0.1, 0.1], [0.1, 0.1, 0.1, 0.1, 0.1, 0.1], [0.1, 0.1, 0.1, 0.1, 0.1, 0.1], [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]], 500)
            >>> N = ArrivalNode(Q)
            >>> [[round(pr, 2) for pr in N.cum_transition_row[cls]] for cls in range(len(N.cum_transition_row))]
            [[0.12, 0.32, 0.6, 0.76, 0.96, 1.0]]

        Another example.
            >>> Q = Simulation([[5, 10, 25]], [[20, 30, 30]], [1, 2, 2], [[[0.1, 0.3, 0.1], [0.2, 0.2, 0.2], [0.6, 0.1, 0.1]]], 100)
            >>> N = Q.nodes[0]
            >>> N.cum_transition_row
            [[0.125, 0.375, 1.0]]
        """

        cum_transition_row = []
        for cls in range(len(self.transition_row_given_class)):
            sum_p = 0
            cum_transition_row.append([])
            for p in self.transition_row_given_class[cls]:
                sum_p += p
                cum_transition_row[cls].append(sum_p)
        return cum_transition_row


    def find_cumulative_class_probs(self):
        """
        Returns the cumulative class probs

        An example of finding the cumulative probabilities of a new customer being in each class.
            >>> Q = Simulation([[5, 10, 25], [10, 20, 30]], [[20, 30, 30], [10, 13, 10]], [1, 2, 2], [[[0.1, 0.3, 0.1], [0.2, 0.2, 0.2], [0.6, 0.1, 0.1]], [[0.1, 0.3, 0.1], [0.2, 0.2, 0.2], [0.6, 0.1, 0.1]]], 100)
            >>> N = ArrivalNode(Q)
            >>> N.find_cumulative_class_probs()
            [0.4, 1.0]

        Another example.
            >>> Q = Simulation([[30, 10], [5, 5]], [[20, 30], [40, 10]], [1, 2], [[[0.1, 0.3], [0.2, 0.2]], [[0.4, 0.1], [0.7, 0.1]]], 100)
            >>> N = ArrivalNode(Q)
            >>> N.find_cumulative_class_probs()
            [0.8, 1.0]
        """

        cum_class_probs = []
        sum_p = 0
        for p in self.class_probs:
            sum_p += p
            cum_class_probs.append(sum_p)
        return cum_class_probs


    def __repr__(self):
        """
        Representation of a node::

        An example showing how an arrival node is represented.
            >>> Q = Simulation([[2, 2]], [[3, 3]], [1, 1], [[[1.0, 0.0], [0.0, 1.0]]], 500)
            >>> N = ArrivalNode(Q)
            >>> N
            Arrival Node

        Another example.
            >>> Q = Simulation([[4]], [[4]], [2], [[[0.5]]], 40)
            >>> N = Q.nodes[0]
            >>> N
            Arrival Node

        """
        return 'Arrival Node'

    def release(self):
        """
        Update node when a service happens.

        An example of creating an individual instance, releasing it to a node, and then updating its next event time.
            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.lmbda
            8
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            [Individual 1]
            >>> round(N.next_event_time,5)
            0.03681

        Another example.
            >>> seed(12)
            >>> Q = Simulation([[8, 1]], [[10, 3]], [1, 1], [[[.1, .5], [.4, .3]]], 50)
            >>> Q.transitive_nodes[0].individuals
            []
            >>> Q.transitive_nodes[1].individuals
            []
            >>> N = ArrivalNode(Q)
            >>> N.next_event_time
            0
            >>> N.release()
            >>> Q.transitive_nodes[0].individuals
            [Individual 1]
            >>> Q.transitive_nodes[1].individuals
            []
            >>> round(N.next_event_time,5)
            0.01709
        """
        self.number_of_individuals += 1
        next_individual = Individual(self.number_of_individuals, self.simulation.number_of_nodes, self.choose_class())
        next_node = self.next_node(next_individual.customer_class)
        next_node.accept(next_individual, self.next_event_time)
        self.update_next_event_date()

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> N = ArrivalNode(Q)
            >>> N.next_event_time
            0
            >>> N.update_next_event_date()
            >>> round(N.next_event_time, 5)
            0.01804
        """
        self.next_event_time += expovariate(self.lmbda)

    def next_node(self, customer_class):
        """
        Finds the next node according the random distribution.

        An example of finding the individual's starting node.
            >>> seed(1)
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> N = Q.nodes[0]
            >>> N.cum_transition_row
            [[0.625, 1.0]]
            >>> N.next_node(0)
            Node 1
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 2

        And another example.
            >>> seed(401)
            >>> Q = Simulation([[2, 9]], [[7, 9]], [1, 3], [[[.2, .5], [.4, .4]]], 50)
            >>> N = Q.nodes[0]
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 2
            >>> N.next_node(0)
            Node 2
        """
        rnd_num = random()
        for p in range(len(self.cum_transition_row[customer_class])):
            if rnd_num < self.cum_transition_row[customer_class][p]:
                return self.simulation.transitive_nodes[p]

    def choose_class(self):
        """
        Returns the customer's class from the class probabilities

            >>> seed(6)
            >>> Q = Simulation([[7, 6, 5]], [[10, 12, 10]], [2, 2, 2], [[[0.5, 0.2, 0.2], [0.2, 0.5, 0.2], [0.2, 0.2, 0.5]]], 100)
            >>> N = ArrivalNode(Q)
            >>> N.choose_class()
            0
        """

        rnd_num = random()
        for p in range(len(self.cum_class_probs)):
            if rnd_num < self.cum_class_probs[p]:
                return p


class ExitNode:
    """
    Class for the exit node on our network
    """
    def __init__(self, max_simulation_time):
        """
        Initialise a node.

        An example of an exit node instance.
            >>> N = ExitNode(100)
            >>> N.individuals
            []
            >>> N.id_number
            -1
            >>> N.next_event_time
            100

        And another.
            >>> N = ExitNode(4)
            >>> N.id_number
            -1
            >>> N.next_event_time
            4
        """
        self.individuals = []
        self.id_number = -1
        self.next_event_time = max_simulation_time


    def __repr__(self):
        """
        Representation of a node::

        An example of how an exit node is represented.
            >>> N = ExitNode(500)
            >>> N
            Exit Node

        And another.
            >>> N = ExitNode(320)
            >>> N
            Exit Node
        """
        return 'Exit Node'

    def accept(self, next_individual, current_time):
        """
        Accepts a new customer to the queue

        An example of a customer leaving the system (getting accepted to the exit node).
            >>> N = ExitNode(200)
            >>> N.individuals
            []
            >>> N.next_event_time
            200
            >>> next_individual = Individual(5, 1)
            >>> N.accept(next_individual, 1)
            >>> N.individuals
            [Individual 5]
            >>> N.next_event_time
            200

        Another example.
            >>> Q = Simulation([[2, 9]], [[7, 9]], [1, 3], [[[.2, .5], [.4, .4]]], 12)
            >>> N = Q.nodes[-1]
            >>> N.individuals
            []
            >>> N.next_event_time
            12
            >>> next_individual = Individual(3, 2)
            >>> N.accept(next_individual, 3)
            >>> N.individuals
            [Individual 3]
            >>> N.next_event_time
            12
        """
        self.individuals.append(next_individual)

    def update_next_event_date(self):
        """
        Finds the time of the next event at this node

        An example showing that this method does nothing.
            >>> N = ExitNode(25)
            >>> N.next_event_time
            25
            >>> N.update_next_event_date()
            >>> N.next_event_time
            25

        And again.
            >>> Q = Simulation([[4, 1]], [[2, 4]], [5, 1], [[[.8, .1], [.3, .25]]], 60)
            >>> N = Q.nodes[-1]
            >>> N.next_event_time
            60
            >>> N.update_next_event_date()
            >>> N.next_event_time
            60

        And again, even when parameters don't make sense.
            >>> N = ExitNode(False)
            >>> N.next_event_time
            False
            >>> N.update_next_event_date()
            >>> N.next_event_time
            False
        """
        pass


class Simulation:
    """
    Overall simulation class
    """
    def __init__(self, lmbda, mu, c, transition_matrix, max_simulation_time, warm_up=0):
        """
        Initialise a queue instance.

        Here is an example::

        An example of creating a simulation instance.
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50, 10)
            >>> Q.lmbda
            [[5, 3]]
            >>> Q.mu
            [[10, 10]]
            >>> Q.c
            [1, 1]
            >>> Q.transition_matrix
            [[[0.2, 0.5], [0.4, 0.4]]]
            >>> Q.nodes
            [Arrival Node, Node 1, Node 2, Exit Node]
            >>> Q.transitive_nodes
            [Node 1, Node 2]
            >>> Q.max_simulation_time
            50
            >>> Q.warm_up
            10

        Another example of creating a simulation instance.
            >>> Q = Simulation([[5.5]], [[12.2]], [1], [[[0]]], 600, 250)
            >>> Q.lmbda
            [[5.5]]
            >>> Q.mu
            [[12.2]]
            >>> Q.c
            [1]
            >>> Q.transition_matrix
            [[[0]]]
            >>> Q.nodes
            [Arrival Node, Node 1, Exit Node]
            >>> Q.transitive_nodes
            [Node 1]
            >>> Q.max_simulation_time
            600
            >>> Q.warm_up
            250

        Some tests to raise errors.
            >>> Q = Simulation([[10, 8], [9, 11]], [[5, 5]], [7, 7], [[[0.5, 0.2], [0.3, 0.1]]], 500)
            Traceback (most recent call last):
            ...
            ValueError: Lambda, Mu and the Transition Matrix should all have the same number of classes

            >>> Q = Simulation([[7, 7], [15]], [[6], [7]], [10], [[0.0], [0.0]], 50)
            Traceback (most recent call last):
            ...
            ValueError: Lambda should have same length as c for every class

            >>> Q = Simulation([[5, 6]], [[5, 3, 6]], [3, 3], [[[0.5, 0.3], [0.1, 0.1]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: Mu should have same length as c for every class

            >>> Q = Simulation([[10, 10]], [[12, 12]], [3, 3], [[[0.1, 0.1, 0.3], [0.1, 0.1]]], 50)
            Traceback (most recent call last):
            ...
            ValueError: Transition matrix should be square matrix of length c for every class

            >>> Q = Simulation([[30, 30]], [[20, 20]], [4, 4], [[[0.4, 0.1], [0.4, 0.1], [0.4, 0.1]]], 500)
            Traceback (most recent call last):
            ...
            ValueError: Transition matrix should be square matrix of length c for every class

            >>> Q = Simulation([[-4]], [[5]], [2], [[[0.6]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: All arrival rates should be positive

            >>> Q = Simulation([[4, 8], [5, 6]], [[5, 7], [-1, 2]], [2, 3], [[[0.6, 0.1], [0.1, 0.1]], [[0.2, 0.2], [0.1, 0.4]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: All service rates should be positive

            >>> Q = Simulation([[6]], [[7]], [4.5], [[[0.0]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: All servers must be positive integer number

            >>> Q = Simulation([[6]], [[7]], [-4], [[[0.0]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: All servers must be positive integer number

            >>> Q = Simulation([[6, 7]], [[7, 7]], [2, 2], [[[0.1, 0.4], [1.2, 0.2]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: All transition matrix entries should be probabilities 0<=p<=1 and all transition matrix rows should sum to 1 or less

            >>> Q = Simulation([[6, 7]], [[7, 7]], [2, 2], [[[0.1, 0.4], [0.2, -0.2]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: All transition matrix entries should be probabilities 0<=p<=1 and all transition matrix rows should sum to 1 or less

            >>> Q = Simulation([[6, 7]], [[7, 7]], [2, 2], [[[0.6, 0.7], [0.2, 0.2]]], 100)
            Traceback (most recent call last):
            ...
            ValueError: All transition matrix entries should be probabilities 0<=p<=1 and all transition matrix rows should sum to 1 or less

            >>> Q = Simulation([[5.5]], [[12.2]], [1], [[[0]]], 600, -250)
            Traceback (most recent call last):
            ...
            ValueError: Warm up period should be positive or 0

            >>> Q = Simulation([[5.5]], [[12.2]], [1], [[[0]]], 200, 250)
            Traceback (most recent call last):
            ...
            ValueError: Maximum simulation time should be positive, and greater than the warm up period

            >>> Q = Simulation([[5.5]], [[12.2]], [1], [[[0]]], -30)
            Traceback (most recent call last):
            ...
            ValueError: Maximum simulation time should be positive, and greater than the warm up period
        """

        if len(lmbda) != len(mu) or len(lmbda) != len(transition_matrix) or len(mu) != len(transition_matrix):
            raise ValueError('Lambda, Mu and the Transition Matrix should all have the same number of classes')

        if any(len(lmbdacls) != len(c) for lmbdacls in lmbda):
            raise ValueError('Lambda should have same length as c for every class')

        if any(len(mucls) != len(c) for mucls in mu):
            raise ValueError('Mu should have same length as c for every class')

        if any(len(transmatrxcls) != len(c) for transmatrxcls in transition_matrix):
            raise ValueError('Transition matrix should be square matrix of length c for every class')

        if any(len(transmatrxrow) != len(c) for transmatrxcls in transition_matrix for transmatrxrow in transmatrxcls):
            raise ValueError('Transition matrix should be square matrix of length c for every class')

        if any(l <= 0 for lmbdaclass in lmbda for l in lmbdaclass):
            raise ValueError('All arrival rates should be positive')

        if any(m <= 0 for muclass in mu for m in muclass):
            raise ValueError('All service rates should be positive')

        if any(type(k) is not int or k <= 0 for k in c):
            raise ValueError('All servers must be positive integer number')

        if any(tmval < 0 for transmatrxcls in transition_matrix for transmatrxrow in transmatrxcls for tmval in transmatrxrow) or any(tmval > 1 for transmatrxcls in transition_matrix for transmatrxrow in transmatrxcls for tmval in transmatrxrow) or any(sum(transmatrxrow) > 1 for transmatrxcls in transition_matrix for transmatrxrow in transmatrxcls):
            raise ValueError('All transition matrix entries should be probabilities 0<=p<=1 and all transition matrix rows should sum to 1 or less')

        if warm_up < 0:
            raise ValueError('Warm up period should be positive or 0')

        if max_simulation_time < 0 or max_simulation_time< warm_up:
            raise ValueError('Maximum simulation time should be positive, and greater than the warm up period')

        self.lmbda = lmbda
        self.overall_lmbda = sum([sum(lmbda[i]) for i in range(len(lmbda))])
        self.class_probs = [sum(lmbda[i])/self.overall_lmbda for i in range(len(lmbda))]
        self.node_given_class_probs = [[lmbda[j][i]/(self.class_probs[j]*self.overall_lmbda) for i in range(len(lmbda[0]))] for j in range(len(lmbda))]
        self.mu = mu
        self.c = c
        self.transition_matrix = transition_matrix
        self.max_simulation_time = max_simulation_time
        self.warm_up = warm_up
        self.transitive_nodes = [Node(i + 1, self) for i in range(len(self.c))]
        self.nodes = [ArrivalNode(self)] + self.transitive_nodes + [ExitNode(self.max_simulation_time)]
        self.number_of_nodes = len(self.transitive_nodes)

    def find_next_active_node(self):
        """
        Return the next active node:

        A mock example testing if this method works.
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> i = 0
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i += 1
            >>> Q.find_next_active_node()
            Arrival Node

        And again.
            >>> Q = Simulation([[5, 3]], [[10, 10]], [1, 1], [[[.2, .5], [.4, .4]]], 50)
            >>> i = 10
            >>> for node in Q.nodes[:-1]:
            ...     node.next_event_time = i
            ...     i -= 1
            >>> Q.find_next_active_node()
            Node 2
        """
        return min(self.nodes, key=lambda x: x.next_event_time)

    def simulate(self):
        """
        Run the actual simulation.

        An example of simulating the simulation.
            >>> seed(99)
            >>> Q = Simulation([[1]], [[2]], [1], [[[0]]], 50, 5)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.76087

        Another example of simulating a simulation.
            >>> seed(2)
            >>> Q = Simulation([[2, 3]], [[2, 5]], [2, 1], [[[0.2, 0.2], [0.3, 0.3]]], 60, 10)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            4.39175
            >>> round(Q.mean_waits()[2], 5)
            4.07729

        And another, with two classes.
            >>> seed(99)
            >>> Q = Simulation([[2, 3], [4, 5]], [[4, 5], [4, 5]], [5, 5], [[[0.2, 0.2], [0.3, 0.3]], [[0.1, 0.0], [0.5, 0.2]]], 60, 10)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.02166

        And an example of simulating a simple M/M/c queue.
            >>> seed(9)
            >>> Q = Simulation([[4]], [[3]], [3], [[[0]]], 100)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.03224
        """
        next_active_node = self.find_next_active_node()
        while next_active_node.next_event_time < self.max_simulation_time:
            next_active_node.release()
            next_active_node = self.find_next_active_node()

    def get_all_individuals(self):
        """
        Returns list of all individuals with at least one record

        An example of obtaining the list of all individuals who completed service.
            >>> seed(1)
            >>> Q = Simulation([[1]], [[2]], [1], [[[0]]], 5)
            >>> Q.simulate()
            >>> Q.get_all_individuals()
            [Individual 1, Individual 2, Individual 3, Individual 4]

        Another example.
            >>> seed(10)
            >>> Q = Simulation([[2, 3]], [[2, 5]], [2, 1], [[[0.2, 0.2], [0.3, 0.3]]], 2)
            >>> Q.simulate()
            >>> Q.get_all_individuals()
            [Individual 9, Individual 1, Individual 2, Individual 5, Individual 6, Individual 4, Individual 3, Individual 8, Individual 7, Individual 11]

        """
        return [individual for node in self.nodes[1:] for individual in node.individuals if len(individual.data_records) > 0]

    def get_individuals_by_node(self):
        """
        Return a dictionary with keys nodes and values: lists of players who have a complete record for that node.

        An example of obtaining the number of individuals who completed service at that node.
            >>> seed(1)
            >>> Q = Simulation([[1]], [[2]], [1], [[[0]]], 5)
            >>> Q.simulate()
            >>> len(Q.get_individuals_by_node()[1])
            4

        An example of obtaining the list of all individuals who completed service at that node.
            >>> seed(10)
            >>> Q = Simulation([[2, 3]], [[2, 5]], [2, 1], [[[0.2, 0.2], [0.3, 0.3]]], 2)
            >>> Q.simulate()
            >>> len(Q.get_individuals_by_node()[1])
            5
            >>> Q.get_individuals_by_node()[2]
            [Individual 9, Individual 1, Individual 2, Individual 5, Individual 6, Individual 7]

        An example where no individual competed service at that node.
            >>> seed(2)
            >>> Q = Simulation([[1]], [[0.01]], [1], [[[0]]], 5)
            >>> Q.simulate()
            >>> Q.get_individuals_by_node()[1]
            []
        """
        all_individuals = self.get_all_individuals()
        return {node.id_number:[individual for individual in all_individuals if node.id_number in individual.data_records] for node in self.transitive_nodes}

    def get_records_by_node(self):
        """
        Returns all records of an individual

        An example of obtaining a dictionart of the records of everyone who has completed service at that node, for each node.
            >>> seed(1)
            >>> Q = Simulation([[1]], [[2]], [1], [[[0]]], 5)
            >>> Q.simulate()
            >>> Q.get_records_by_node()[1][0].wait
            0.0
            >>> round(Q.get_records_by_node()[1][1].arrival_date, 5)
            0.29446

        Another example.
            >>> seed(5)
            >>> Q = Simulation([[1, 2]], [[2, 2]], [1, 2], [[[0.2, 0.2], [0.2, 0.2]]], 5)
            >>> Q.simulate()
            >>> round(Q.get_records_by_node()[1][0].wait, 5)
            1.45746
            >>> round(Q.get_records_by_node()[1][1].service_date, 5)
            0.9517
            >>> round(Q.get_records_by_node()[2][1].wait, 5)
            0.21825

        Keys of the dictionary are the node id numbers, can only call on transitive nodes.
            >>> seed(2)
            >>> Q = Simulation([[8]], [[8]], [2], [[[0]]], 5)
            >>> Q.simulate()
            >>> Q.get_records_by_node()[0][0].wait
            Traceback (most recent call last):
            ...
            KeyError: 0
        """
        individuals_by_node = self.get_individuals_by_node()
        return {node_id:[record for individual in individuals_by_node[node_id] for record in individual.data_records[node_id]] for node_id in individuals_by_node}

    def mean_waits(self):
        """
        A method to return the mean wait in the system (after simulation has been run)

        An example of finding the mean waits at a node of a simulation.
            >>> seed(11)
            >>> Q = Simulation([[6]], [[12]], [1], [[[0]]], 25)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            0.06419

        Another example, with more nodes.
            >>> seed(18)
            >>> Q = Simulation([[5, 7]], [[6, 7]], [1, 2], [[[0.1, 0.1], [0.2, 0.1]]], 30)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            1.32958
            >>> round(Q.mean_waits()[2], 5)
            0.03866
            >>> round(Q.mean_waits()[0], 5)
            Traceback (most recent call last):
            ...
            KeyError: 0

        An example when no individual has completed service.
            >>> seed(25)
            >>> Q = Simulation([[5, 7]], [[6, 7]], [1, 2], [[[0.1, 0.1], [0.2, 0.1]]], 0.01, 0)
            >>> Q.simulate()
            >>> round(Q.mean_waits()[1], 5)
            Traceback (most recent call last):
            ...
            ValueError: No data simulated

        An example when no individual has completed service at a certain node.
            >>> seed(1)
            >>> Q = Simulation([[0.00005, 7]], [[6, 7]], [1, 2], [[[0, 0.1], [0, 0.1]]], 10, 0)
            >>> Q.simulate()
            >>> Q.mean_waits()[1]
            False
        """
        records_by_node = self.get_records_by_node()
        if all(len(r) == 0 for r in records_by_node.values()):
            raise ValueError("No data simulated")
        mean_waits = {node_id:mean([r.wait for r in records_by_node[node_id] if r.arrival_date > self.warm_up]) for node_id in records_by_node}
        return mean_waits

    def records(self):
        """
        Return all records

        An eample of finding the records of all completed visits in a very short simulation.
            >>> seed(2)
            >>> Q = Simulation([[11, 2]], [[4, 3]], [4, 2], [[[0.6, 0.1], [0.3, 0.1]]], 0.2824)
            >>> Q.simulate()
            >>> Q.records()
            3 0.0351582971806 0.0 0.0351582971806 0.0431075208553 0.0782658180359 1
            5 0.123759750491 1.38777878078e-17 0.123759750491 0.0069571257192 0.13071687621 1

        Another example.
            >>> seed(8)
            >>> Q = Simulation([[3]], [[7]], [1], [[[0]]], 0.5)
            >>> Q.simulate()
            >>> Q.records()
            1 0 0.0 0.0 0.0192933682271 0.0192933682271 1
            2 0.406719838233 0.0 0.406719838233 0.0335657332557 0.440285571489 1
        """
        all_individuals = sorted([individual for node in self.nodes[1:] for individual in node.individuals], key=lambda x:x.id_number)
        for ind in all_individuals:
            if 1 in ind.data_records:
                record = ind.data_records[1][0]
                print ind.id_number, record.arrival_date, record.wait, record.service_date, record.service_time, record.exit_date, record.node
    
    def max_customers_per_node(self):
        """
        Returns the maximum number of customers that have visited that node at any time

        An example of finding the maximum number of customers that visited a node together.
            >>> Q = Simulation([[3, 3]], [[7, 7]], [1, 1], [[[0.1, 0.5], [0.1, 0.2]]], 0.5)
            >>> Q.nodes[1].numbers_in_node = [[0, 1], [3, 2], [4, 1], [6, 0], [9, 1], [11, 0]]
            >>> Q.nodes[2].numbers_in_node = [[0, 0], [2, 1], [4, 0], [5, 1], [8, 2], [12, 1], [13, 2], [15, 1], [17, 0]]
            >>> Q.max_customers_per_node()
            [2, 2]
        """

        return [max([node.numbers_in_node[k][1] for k in range(len(node.numbers_in_node))]) for node in self.transitive_nodes]

    def find_times_in_state(self):
        """
        Returns a list of dictionaries for each node, with the amount of time that node spent in each state

        An example of finding the times spent in each state.
            >>> Q = Simulation([[3, 3]], [[7, 7]], [1, 1], [[[0.1, 0.5], [0.1, 0.2]]], 0.5)
            >>> Q.nodes[1].numbers_in_node = [[0, 1], [3, 2], [4, 1], [6, 0], [9, 1], [11, 0]]
            >>> Q.nodes[2].numbers_in_node = [[0, 0], [2, 1], [4, 0], [5, 1], [8, 2], [12, 1], [13, 2], [15, 1], [17, 0]]
            >>> Q.find_times_in_state()
            [{0: 3, 1: 4, 2: 1}, {0: 1, 1: 8, 2: 6}]

        Another example of finding the times spent in each state.
            >>> Q = Simulation([[3, 3, 1]], [[7, 7, 2]], [1, 1, 1], [[[0.1, 0.5, 0.1], [0.1, 0.2, 0.1], [0.3, 0.5, 0.1]]], 0.5)
            >>> Q.nodes[1].numbers_in_node = [[0, 0], [0.3, 1], [0.4, 2], [0.7, 1], [1.1, 0], [1.6, 1], [1.7, 2], [1.9, 3], [2.4, 2], [2.5, 1], [2.7, 2], [2.8, 1], [3, 0]]
            >>> Q.nodes[2].numbers_in_node = [[0, 0], [0.1, 1], [0.3, 0], [0.8, 1], [1.0, 2], [1.2, 3], [1.6, 2], [1.9, 3], [2.4, 4], [2.5, 3], [2.7, 2]]
            >>> Q.nodes[3].numbers_in_node = [[0, 0], [0.6, 1], [0.8, 0], [1.7, 1], [2.3, 2], [2.4, 1], [2.6, 1], [2.9, 0]]
            >>> Q.find_times_in_state()
            [{0: 0.5, 1: 1.0000000000000004, 2: 0.6999999999999996, 3: 0.5}, {0: 0.5, 1: 0.3999999999999999, 2: 0.4999999999999998, 3: 1.1000000000000003, 4: 0.10000000000000009}, {0: 0.8999999999999999, 1: 1.2999999999999998, 2: 0.10000000000000009}]
        """

        max_cust_node = self.max_customers_per_node()
        return [{j:sum([node.numbers_in_node[i+1][0] - node.numbers_in_node[i][0] for i in range(len(node.numbers_in_node)-1) if node.numbers_in_node[i][1]==j if node.numbers_in_node[i][0] > self.warm_up]) for j in range(max_cust_node[node.id_number-1]+1)} for node in self.transitive_nodes]

    def mean_customers(self):
        """
        Returns a dictionary of the mean number of customers at each node

        An example of finding the mean amount of customers per node.
            >>> Q = Simulation([[3, 3]], [[7, 7]], [1, 1], [[[0.1, 0.5], [0.1, 0.2]]], 0.5)
            >>> Q.nodes[1].numbers_in_node = [[0, 1], [3, 2], [4, 1], [6, 0], [9, 1], [11, 0]]
            >>> Q.nodes[2].numbers_in_node = [[0, 0], [2, 1], [4, 0], [5, 1], [8, 2], [12, 1], [13, 2], [15, 1], [17, 0]]
            >>> Q.mean_customers() 
            {1: 0.5454545454545454, 2: 1.1764705882352942}
        """
        max_cust_node = self.max_customers_per_node()
        times_in_state = self.find_times_in_state()
        return {node.id_number:(sum([times_in_state[node.id_number-1][i]*i for i in range(max_cust_node[node.id_number-1]+1)]))/node.numbers_in_node[-1][0] for node in self.transitive_nodes}

    def mean_visits(self):
        """
        Returns the mean visits per node

        An example of finding the mean visits per node.
            >>> seed(5)
            >>> Q = Simulation([[1]], [[2]], [1], [[[0]]], 100)
            >>> Q.simulate()
            >>> Q.mean_visits()
            {1: 1.0}

        And another example.
            >>> seed(9)
            >>> Q = Simulation([[1, 2]], [[2, 5]], [1, 2], [[[0.0, 1.0], [0.0, 0.5]]], 100)
            >>> Q.simulate()
            >>> Q.mean_visits()
            {1: 1.0, 2: 2.0167224080267561}
        """
        individuals_by_node = self.get_individuals_by_node()
        return {node.id_number:mean([ind.number_of_visits[node.id_number] for ind in individuals_by_node[node.id_number]]) for node in self.transitive_nodes}


if __name__ == '__main__':
    Q = Simulation([[5.0, 2.0, 4.0], [3.0, 7.0, 4.0]], [[8.0, 9.0, 6.0], [5.0, 4.0, 9.0]], [8, 6, 6], [[[0.2, 0.3, 0.4], [0.2, 0.1, 0.1], [0.2, 0.7, 0.1]], [[0.5, 0.1, 0.1], [0.3, 0.1, 0.1], [0.8, 0.1, 0.0]]], 2000, 500)
    Q.simulate()
    print 'Mean waiting times: '
    print Q.mean_waits()
    print 'Mean number of visits: '
    print Q.mean_visits()
    print 'Mean number of customers: '
    print Q.mean_customers()