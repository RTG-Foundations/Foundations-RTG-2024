import networkx as nx

graph = nx.DiGraph()
graph.add_edge(1, 2)
graph.add_edge(2,3)
graph.add_edge(3,4)
graph.add_edge(4,1) 
graph.add_edge(10, 20) 
graph.add_edge(20,30)
graph.add_edge(30,40)
graph.add_edge(40,10)
graph.add_edge(1, 10)
graph.add_edge(2, 20)
graph.add_edge(3, 30)
graph.add_edge(4, 40) 
graph.add_edge(1, 1) 
graph.add_edge(2, 2) 
graph.add_edge(10, 1) 


positions3d = nx.spring_layout(graph,dim=3)
#positions3d = nx.circular_layout(graph, dim=5) #2D
#positions3d = nx.fruchterman_reingold_layout(graph, dim=3, k=0.5, iterations=1000) #parameters - from graphviz; expreinments