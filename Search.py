import Graph 
import numpy as np

def bfs(graph : Graph, node : int):
    """
    Performs a Breadth-First Search (BFS) to discover all reachable nodes 
    from a given starting point.

    This acts as a validation layer to check graph connectivity. This pre-check prevents 
    the routing engine from attempting to compute paths between disconnected components.

    Parameters:
    -----------
    graph : Graph
        The graph object containing topology and adjacency relations.
    node : int
        The unique ID of the node where the exploration begins.

    Returns:
    --------
    list
        A list of all node IDs belonging to the same connected component.
    """
    # Using a Python set provides O(1) average time complexity for lookups.
    visited = {node} 
    q = [node]
    while q:
        current_id = q.pop(0)
        # Dynamically extract neighbors from the structural graph object
        neighbors = [neighbor.id for neighbor in graph.get_node(current_id).adjacent_nodes()]
        for next_id in neighbors:
            if next_id not in visited:
                visited.add(next_id)
                q.append(next_id)
    return list(visited)

def dijkstra(graph : Graph, node : int):
    """
    Computes the single-source shortest paths using an optimized, 
    vectorized Dijkstra's algorithm.

    Graph Theory Note:
    ------------------
    Dijkstra's algorithm structurally constructs a 'Shortest-Path Tree' (SPT) 
    rooted at the start node. The returned list of edges represents the finalized 
    branches of this tree, which the plotting engine later uses to map out the route.

    Parameters:
    -----------
    graph : Graph
        The graph topology containing coordinates and the distance matrix.
    node : int
        The origin node ID for the routing simulation.

    Returns:
    --------
    list
        A list of directed tuples (predecessor, successor) forming the Shortest-Path Tree.
    """
    distance_matrix = graph.distance_matrix()
    n = len(distance_matrix)
    shortest_edges = []
    predecessors = np.full(n, -1)
    predecessors[node] = node
    # State tracking arrays optimized via NumPy vectorization
    visited = np.full(n, False)
    distance_list = np.full(n, np.inf)
    distance_list[node] = 0
    # Since Dijkstra will not change a node's distance more than |V| times (Greedy Choice Property), 
    # we can safely use a for-loop with exactly n iterations.
    for i in range(n):
        # Extracting the unvisited node with the absolute minimum distance using NumPy
        index_of_min_dist = np.argmin(np.where(visited == False,distance_list,np.inf))
        weight_of_min_index = distance_list[index_of_min_dist]
        # EARLY EXIT: Break in case there are isolated components we did not consider yet
        if weight_of_min_index == np.inf:
            break
        visited[index_of_min_dist] = True
        shortest_edges.append((predecessors[index_of_min_dist],index_of_min_dist))
        neighbors = [n.id for n in graph.get_node(index_of_min_dist).adjacent_nodes()]
        for j in neighbors:
            if visited[j] == False:
                if distance_list[j] == np.inf:
                    distance_list[j] = weight_of_min_index + distance_matrix[index_of_min_dist][j]
                    predecessors[j] = index_of_min_dist
                elif weight_of_min_index + distance_matrix[index_of_min_dist][j] < distance_list[j]:
                    distance_list[j] = weight_of_min_index + distance_matrix[index_of_min_dist][j]
                    predecessors[j] = index_of_min_dist
    # Remove the self-loop element (node, node) at the root of the tree before returning
    shortest_edges.pop(0)
    return(shortest_edges)