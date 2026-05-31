import numpy as np
from matplotlib import pyplot as plt
import math as m

# This is a modified class Graph, it is rewritten by myself for this specific problem.

class Graph:
    def __init__(self, num_or_file, xCords = None, yCords = None, directed = False):
        """
        Initializes the Graph structure either as an empty shell with a fixed number of nodes
        or parses it dynamically from geospatial text files containing coordinates and edge maps.

        Parameters:
        -----------
        num_or_file : int or str
            If int: Initializes a graph with n empty nodes.
            If str: Path to the text file mapping out the node edges.
        xCords : str, optional
            Path to the text file containing the X-coordinates of the nodes.
        yCords : str, optional
            Path to the text file containing the Y-coordinates of the nodes.
        directed : bool, default=False
            Determines whether edges are unidirectional or bidirectional.
        """
        self._directed = directed
        if type(num_or_file) == int and type(xCords) == None and type(yCords) == None:
            self._nodes = [self.Node() for _ in range(num_or_file)]
        elif type(num_or_file) == str and type(xCords) == str and type(yCords) == str:
            # Synchronized parsing of three structural text files
            with open(num_or_file, "r") as file, open(xCords, "r") as x, open(yCords, "r") as y:
                num_nodes = int(file.readline())
                # Instantiating geographic Nodes with parsed physical coordinates
                self._nodes = [self.Node(float(x.readline()),float(y.readline())) for _ in range(num_nodes)]
                # Building the adjacency structure line by line
                for line in file:
                    tail = int(line.split()[0])
                    head = int(line.split()[1])
                    if tail != head:
                        self.add_edge(tail, head)
                    else:
                        # Self-loops violate basic routing metrics
                        raise RuntimeError("Invalid file format: loops not allowed")
            # Pre-compute and cache the distance weight matrix to guarantee efficient Dijkstra lookups
            self._distance_matrix = self.distance_matrix()
        else:
            raise NotImplementedError("Type of Argument not allowed")

    @property
    def num_nodes(self):
        return len(self._nodes)

    def add_nodes(self, num_new_nodes):
        self._nodes.extend([self.Node() for i in range(num_new_nodes)])

    def add_edge(self, tail, head):
        """Adds a directed or undirected connection between two verified node IDs."""
        if tail >= self.num_nodes or tail < 0 or head >= self.num_nodes or head < 0:
            raise ValueError("Edge cannot be added due to undefined endpoint")
        self._nodes[tail].add_neighbor(head)
        if not self._directed:
            self._nodes[head].add_neighbor(tail)

    def get_node(self, node_id):
        if node_id < 0 or node_id >= self.num_nodes:
            raise ValueError("Invalid nodeId")
        return self._nodes[node_id]

    def __str__(self):
        """Used for generating graph_structure.txt validation logs."""
        out = ""
        if self._directed:
            out += "Digraph "
        else:
            out += "Undirected Graph "
        out += "with {} vertices, numbered 0, ..., {}\n".format(self.num_nodes, self.num_nodes - 1)
        for nodeId in range(self.num_nodes):
            if self._directed:
                s = "leaving"
            else:
                s = "incident to"
            out += "The following edges are " + s + " vertex {}:\n".format(nodeId)
            for neighbor in self._nodes[nodeId].adjacent_nodes():
                out += "{} - {}\n".format(nodeId, neighbor.id)
        return out

    def distance_matrix(self):
        """
        Generates a dense matrix storing Euclidean distances between adjacent nodes.
        Non-adjacent nodes natively remain initialized at a weight cost of 0.0.

        Returns:
        --------
        np.ndarray
            A 2D NumPy array mapping the physical distance weights of the topology.
        """
        matrix = np.zeros((self.num_nodes, self.num_nodes), dtype=float)
        for node_id, node in enumerate(self._nodes):
            adjacent_ids = [adjacent_node.id for adjacent_node in node.adjacent_nodes()]
            for x in adjacent_ids:
                # Euclidean distance calculation based on geographical coordinate grids
                matrix[node_id][x] = m.sqrt(float(abs(self.get_node(node_id).get_X()-self.get_node(x).get_X()))+(float(abs(self.get_node(node_id).get_Y()-self.get_node(x).get_Y()))**2))
        return matrix

    def plot_graph(self):
        """Renders the entire unrouted street network infrastructure via Matplotlib geometry blocks."""
        for i in range(len(self._nodes)):
            n = self._nodes[i]
            neighbors = n.adjacent_nodes()
            for ne in neighbors:
                plt.plot([n.get_X(),self._nodes[ne.id].get_X()],[n.get_Y(),self._nodes[ne.id].get_Y()], color = "black")
        plt.title("Street map of Bonn")
        plt.show()

    def plot_Path(self, t = None, s = None, e = None):
        """
        Traces and visualizes the calculated shortest route onto the street map layout.

        Graph Theory & Reconstruction Note:
        -----------------------------------
        The parameter 't' contains the Shortest-Path Tree (edges) generated by Dijkstra.
        This method uses an inversion algorithm to reconstruct the route: It performs 
        a backward traversal starting at the target node 'e', matching predecessors 
        recursively until the origin source node 's' is successfully closed. 
        Matched routing paths are rendered in high-visibility red.
        """
        check = False
        if type(t) == list and type(s) == int and type(e) == int:
            check = True
        if check:
            # Step 1: Render background street topology map
            for i in range(len(self._nodes)):
                n = self._nodes[i]
                neighbors = n.adjacent_nodes()
                for ne in neighbors:
                    plt.plot([n.get_X(),self._nodes[ne.id].get_X()],[n.get_Y(),self._nodes[ne.id].get_Y()], color = "black")
            # Step 2: Traverse the Shortest Path Tree backwards from target to start; this is possible due to the fact that
            # Djkstra returns a tree (implicitely in this case)
            index = 0
            while s != e and index < len(self._nodes):
                for i in range(len(t)):
                    if e == t[i][1]:
                        a = t[i][0]
                        b = t[i][1]
                        # Plot the specific routing segment in red
                        plt.plot([self._nodes[a].get_X(),self._nodes[b].get_X()],[self._nodes[a].get_Y(),self._nodes[b].get_Y()], color = "red")
                        # Step backwards to the parent node
                        e = a
                index += 1
            # Error Layer: Triggers if start and end nodes are isolated in separated subsets
            if s != e:
                raise NotImplementedError("Invalid points selected")
            plt.title("Found path")
            plt.show()
        else:
            raise NotImplementedError("Type of Argument not allowed")

    class Node:
        """Inner representation of a distinct street intersection / grid coordinate point."""
        def __init__(self,x = None, y = None):
            self._neighbors = []
            self._x = x
            self._y = y

        def get_X(self):
            return self._x
        
        def set_X(self,xNew):
            self._x = xNew

        def get_Y(self):
            return self._y
        
        def set_Y(self,yNew):
            self._y = yNew

        def add_neighbor(self, node_id):
            self._neighbors.append(Graph.Neighbor(node_id))

        def adjacent_nodes(self):
            return self._neighbors

        def number_of_neighbors(self):
            return len(self._neighbors)

    class Neighbor:
        """Inner representation of an adjacent directed link to a target vertex."""
        def __init__(self, node_id):
            self._id = node_id

        @property
        def id(self):
            return self._id