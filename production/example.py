import networkx as nx
from visualize import visualize_3d

graph = nx.DiGraph()
graph.add_edge(1, 2)
graph.add_edge(2, 3)
graph.add_edge(3, 4)
graph.add_edge(4, 1)
graph.add_edge(10, 20)
graph.add_edge(20, 30)
graph.add_edge(30, 40)
graph.add_edge(40, 10)
graph.add_edge(1, 10)
graph.add_edge(2, 20)
graph.add_edge(3, 30)
graph.add_edge(4, 40)
graph.add_edge(1, 1)
graph.add_edge(2, 2)
graph.add_edge(10, 1)


positions = nx.spring_layout(graph, dim=3)
visualize_3d(graph, positions)