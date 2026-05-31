import Graph
import Search as s

def main():
    start = 103 # Example start node
    end = 1758 # Example target node
    # Initialize the custom GIS graph structure with geospatial raw data
    graph = Graph.Graph("graph.txt","xcoords.txt","ycoords.txt")
    # Phase 1: Validate reachability using BFS
    reached_nodes = s.bfs(graph, start)
    # Phase 2: Logging and handling data anomalies safely
    with open("graph_structure.txt", "w", encoding="utf-8") as f:
        if len(reached_nodes) < graph.num_nodes:
            f.write("WARNING: Graph is not connected!\n")
            # Raise a clean exception if routing is mathematically impossible
            if end not in reached_nodes:
                raise NotImplementedError(f"Invalid input; {start} and {end} are not connected!")
        f.write(str(graph))
    # Phase 3: Visualize and compute the Shortest-Path Tree
    graph.plot_graph()
    edges = s.dijkstra(graph,start)
    # Phase 4: Reconstruct and render the final route path
    graph.plot_Path(edges,start,end)

if __name__ == "__main__":
    main()