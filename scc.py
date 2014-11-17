#!/usr/bin/env python
#Jayson Gallardo: jayson.gallardo
#Zack Flowers: zackary.flowers
#Josh Allen: josh.allen
# Analyzing strongly connected components

from random import random
from time import time

TOGGLE_DEBUG = False


#############################################################################################################
#                                         HELPER FUNCTIONS                                                  #
#############################################################################################################
def DEBUG(msg):
    assert(type(msg) is str)
    if TOGGLE_DEBUG:
        print(msg)


def error(msg):
    print('\nError:')
    print('\t'+msg)
    print('\nPress [enter] to continue...')
    input()


def timeIt(func):
    def wrapper(*args, **kwargs):
        start = time()
        func(*args, **kwargs)
        end = time()
        delta = end-start
        print('runtime: ' + str(delta) + ' seconds\n')
        print('\nPress [enter] to continue...')
        input()
    return wrapper


#############################################################################################################
#                                               CLASSES                                                     #
#############################################################################################################
class Graph:
    """Describes a graph"""
    def __init__(self):
        self.edgeList = []
        self.vertexList = []

    def insert(self, edge):
        """
        Inserts an edge to the Graph, and adds vertices to the list if it
        hasn't been added already

        @param string edge      Space delimited string of a pair of vertices
        """
        DEBUG('In Graph.insert(), edge = '+edge)
        self.edgeList.append(edge)
        u, v = edge.split()
        u = Vertex(u)
        v = Vertex(v)

        if u not in self.vertexList:
            self.vertexList.append(u)
        else:   # if u already exists, have u point to the existing one
            i = self.vertexList.index(u)
            u = self.vertexList[i]

        if v not in self.vertexList:
            self.vertexList.append(v)
        else:   # if v already exists, have u point to the existing one
            i = self.vertexList.index(v)
            v = self.vertexList[i]

        if u != v and v not in u.Adj:   # u doesn't need to be adjacent to itself
            u.Adj.append(v)

    def transpose(self):
        tempEdge = self.edgeList    # store current lists temporarily
        tempVertex = self.vertexList
        self.edgeList = []  # clear the lists
        self.vertexList = []
        for edge in tempEdge:  # swap nodes for each edge and insert
            edge = edge.split()[1] + ' ' + edge.split()[0]
            self.insert(edge)
        for u in self.vertexList:  # copy fTimes over to newly generated vertices
            i = tempVertex.index(u)
            u.fTime = tempVertex[i].fTime


class Vertex:
    """Describes nodes"""
    def __init__(self, name):
        self.name = name
        self.color = None
        self.fTime = -1
        self.dTime = -1
        self.Adj = []
        self.parent = None

    def __eq__(self, other):  # overload equals operator
        return self.name == other.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


#############################################################################################################
#                                           GRAPH GENERATORS                                                #
#############################################################################################################
def generateRandomGraph(size):
    """
    Generates a random graph with number of vertices = size.
    The number of adjacent vertices for each is a random number between 0 and 10.
    """
    graph = Graph()
    for u in range(size):
            graph.insert(str(u)+' '+str(u))

    for u in range(size):
        numAdj = int(random()*10)
        for i in range(numAdj):
            graph.insert(str(u)+' '+str(int(random()*size)))

    return graph


def generateDaisyChainGraph(size):
    """
    Generates a graph by daisy chaining a number (size) of prebuilt SCCs.
    Each SCC contains 5 vertices and 5 edges. Each SCC is daisy chained
    via an extra edge.

    @param int size      Number of predetermined SCCs
    """
    graph = Graph()
    count = 0
    for link in range(size):
        for i in range(4):
            graph.insert(str(count)+' '+str(count+1))
            count += 1
        graph.insert(str(count)+' '+str(count-4))
        if link < size-1:
            graph.insert(str(count)+' '+str(count+1))
        count += 1
    return graph


def getGraphFromFile():
    """Returns a graph if successful, otherwise returns None"""
    graph = Graph()
    for attempt in range(3):
        print('Please enter file name to read from:')
        filename = input()
        success = False
        try:
            with open(filename) as f:
                for edge in f.readlines():
                    graph.insert(edge.strip())
            success = True
        except FileNotFoundError:
            error('File doesn\'t exist. Please try again.')
        if success:
            break
    graph.vertexList.sort(key=lambda x: x.name)     # allows us to predict what SCC should look like
    DEBUG(str(graph.vertexList))
    for u in graph.vertexList:
        u.Adj.sort(key=lambda x: x.name)

    if success:
        print('Graph loaded. Press [enter] to continue...')
    else:
        print('Failed to load graph. Press [enter] to continue...')
    input()
    return graph


def getGraphFromInput():
    """Returns a graph if successful, otherwise returns None"""
    graph = Graph()
    print('Please enter edges as space delimited pairs. (exa.: \'a b\')')
    print('Enter one edge per line. Enter a blank line to finish.')
    edge = input()
    while edge:
        if len(edge.split()) == 2:
            graph.insert(edge)
        else:
            error('Invalid edge definition. Please try again.')
        edge = input()
    graph.vertexList.sort(key=lambda x: x.name)     # allows us to predict what SCC should look like
    for u in graph.vertexList:
        u.Adj.sort(key=lambda x: x.name)
    if len(graph.vertexList) == 0:
        error('No edges entered. Graph not loaded.')
        graph = None
    else:
        print('Graph loaded. Press [enter] to continue...')
        input()
    return graph


#############################################################################################################
#                                               DFS                                                         #
#############################################################################################################
def dfs(graph, printTree=False):
    # initialize:
    time = 0
    count = 0
    for u in graph.vertexList:
        u.color = 'white'

    # main loop:
    for u in graph.vertexList:
        if u.color == 'white':
            DEBUG(str([x.color for x in graph.vertexList]))
            count += 1
            if printTree:
                print(str(count)+': ', end='')
                print(u, end='')
            else:
                print('', end='')
            time = dfsVisit(u, time, printTree)
            if printTree:
                print('\n')
            else:
                print('', end='')


def dfsVisit(u, time, printTree=False):
    u.color = 'gray'
    time += 1
    u.dTime = time
    DEBUG(str(u)+': '+str(u.Adj)+' '+str([x.color for x in u.Adj]))
    for v in u.Adj:
        if v.color == 'white':
            v.parent = u
            if printTree:
                print(', ', end='')
                print(v, end='')
            else:
                print('', end='')
            time = dfsVisit(v, time, printTree)
    u.color = 'black'
    time += 1
    u.fTime = time
    DEBUG(str(u)+' '+str(time))
    return time


#############################################################################################################
#                                      STRONGLY CONNECTED COMPONENTS                                        #
#############################################################################################################
def scc(graph, printTree=True):
    start = time()
    dfs(graph)
    graph.transpose()
    graph.vertexList.sort(key=lambda x: x.fTime, reverse=True)
    if printTree:
        print('\n\nStrongly connected components:')
    dfs(graph, printTree=printTree)
    end = time()
    return end-start


#############################################################################################################
#                                              MAIN BODY                                                    #
#############################################################################################################
def main():
    graph = None
    while True:
        print('\n\n')
        print('Choose an option:')
        print('(1) Read edges from file')
        print('(2) Read edges from keyboard')
        print('(3) Generate Random graph')
        print('(4) Generate Daisy Chained graph')
        print('(P) Print strongly connected components')
        print('(L) Calculate avg runtime for 1000 iterations of scc')
        print('(Q) Quit program')

        opt = input().lower()

        if opt == '1':
            graph = getGraphFromFile()
        elif opt == '2':
            graph = getGraphFromInput()
        elif opt == '3':
            while True:
                print('Enter number of desired vertices.')
                x = input()
                try:
                    x = int(x)
                    break
                except ValueError:
                    error('Invalid input.')
            graph = generateRandomGraph(x)
        elif opt == '4':
            while True:
                print('Enter number of desired SCCs.')
                x = input()
                try:
                    x = int(x)
                    break
                except ValueError:
                    error('Invalid input.')
            graph = generateDaisyChainGraph(x)
        elif opt == 'p':
            if graph is not None:
                delta = scc(graph)
                print('Finished in {0} seconds'.format(delta))
                print('Press [enter] to continue...')
                input()
            else:
                error('No graph found. Please run a numerical option first.')
        elif opt == 'l':
            if graph is not None:
                sum = 0
                for i in range(1000):
                    sum += scc(graph, printTree=False)
                print('Average runtime is {0} seconds'.format(sum/1000))
                print('Press [enter] to continue...')
                input()
            else:
                error('No graph found. Please run a numerical option first.')
        elif opt == 'q':
            print('Goodbye!')
            break  # while loop
        else:
            error('Invalid option. Please try again')

if __name__ == "__main__":
    main()
