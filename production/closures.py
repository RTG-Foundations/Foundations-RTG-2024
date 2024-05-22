import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from collections import deque



''' 
    Displays 3D graph. Modified to work with matplotlib
'''
def visualize_3d(graph, positions, title, ax):
    ax.set_title(title)
    color_refl = 'blue'
    color_irr = 'red'
    color_edge = 'blue'
    color_startrr = 'red'

    # draw nodes
    for node in graph:
        coord = positions[node]
        ax.scatter(coord[0], coord[1], coord[2], color=color_refl if (node, node) in graph.edges else color_irr)

    # draw edges
    for edge in graph.edges:
        if edge[0] != edge[1]:
            coordinates_start = positions[edge[0]]
            coordinates_end = positions[edge[1]]

            vector_start = np.array(coordinates_start)
            vector_end = np.array(coordinates_end)

            ax.plot([vector_start[0], vector_end[0]], 
                    [vector_start[1], vector_end[1]], 
                    [vector_start[2], vector_end[2]], color=color_edge)

            vector_arrow = vector_end - vector_start
            axis = 0.5 * vector_arrow
            ax.quiver(vector_start[0], vector_start[1], vector_start[2],
                      axis[0], axis[1], axis[2],
                      color=color_startrr, length=np.linalg.norm(vector_arrow)/3)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')


'''
    Create  a 0-1 matrix to represent the 
    binary relation R on Xn = {0, 1, ..., n-1}
'''
def getMatrix(n,R):
    M = np.zeros((n, n)) # create 0 matrix of size nxn
    
    for (i,j) in R:
        M[i][j] = 1

    return M

'''
    Create a relation to represent the 0-1 matrix
'''
def getRelation(n, M):
    R = set()
    for i in range(0,n):
        for j in range(0,n):
            if M[i][j] == 1:
                R.add((i,j))
    return R
            

'''
Input: a positive integer n; a relation R on Xn
Output: the smallest relation R'
that contains R and is reflexive (such a relation is
called the reflexive closure of R).
'''
def reflexive_closure(n, R):
    M = getMatrix(n,R)
    
    # Mii = 1 for all i = 0, 1, ..., n-1
    for i in range(n):
        M[i][i] = 1
   
    R_prime = getRelation(n,M)
    return R_prime


'''
Input: a positive integer n; a relation R on Xn
Output: the smallest relation R'
that contains R and is symmetric (such a relation
is called the symmetric closure of R).
'''
def symmetric_closure(n, R):

    M = getMatrix(n,R)
    
    # Mij = Mji for all i = 0, 1, ..., n-1
    for i in range(0,n):
        for j in range(0,n):
            if M[i][j] == 1:
                M[j][i] = 1
    
    R_prime = getRelation(n,M)
    return R_prime


'''
Input: a positive integer n; a relation R on Xn
Output: the transitive closure of R.

https://www.geeksforgeeks.org/transitive-closure-of-a-graph/
'''
def transitive_closure(n, R):

    M = getMatrix(n,R)
   
    # Floyd-Warshall algorithm for finding transitive closure
    for k in range(n):
        for i in range(n):
            for j in range(n):
                M[i][j] = M[i][j] or (M[i][k] and M[k][j])
                
    R_prime = getRelation(n,M)
    return R_prime


'''
    Input: a positive integer n; a relation R on Xn
    Output: the connected components of (Xn, R U R^-1)
'''
def find_connected_components(n, R):
    
    # Write the graph as dictionary,  
    # where each key is a node, and each 
    # value is an array of neighbors
    graph = {}
    
    for i in range(n):
        graph[i] = []

    for (a, b) in R:
        graph[a].append(b)  # R
        graph[b].append(a)  # R^-1 

    # set for tracking visited nodes
    visited = set() 

    # array of sets for tracking connected components
    components = []

    # Find all connected components using BFS
    for node in range(1, n):
        if node not in visited:
            result =  bfs(graph, node)
            for node in result:
                visited.add(node)
            components.append(result)
    
    return components


'''
    Helper method to perform BFS to find all nodes 
    in same connected component
'''
def bfs(graph, start_node):
    # set for tracking visited nodes
    visited = set()

    # queue to track the nodes to explore
    # add start node to the queue
    queue = deque([start_node])
    
    while queue:
        # dequeue front node
        node = queue.popleft()
        if node not in visited:
            # add current node to visted array
            visited.add(node)

            # Add neighbors to the queue
            neighbors = graph[node]
            queue.extend(neighbors)
    
    return visited


def main():

    '''
        Calculate the closures
    '''
    n = 4
    R = {(0, 1), (1, 2), (2, 0), (3,2)}
    print(f"R: {R}\n")

   
    # Reflexive test
    R_reflex = reflexive_closure(n, R)
    # R + {(0,0), (1,1), (2,2), (3,3)}
    print(f"Reflexive closure of R: {R_reflex}\n")


    # Symmetric test
    R_sym = symmetric_closure(n, R)
    # R + {(1,0), (2,1), (0,2), (2,3)}
    print(f"Symmetric closure of R: {R_sym}\n")


    # Transitive test
    R_trans = transitive_closure(n, R)
    # R + R^2 + ... + R^(n-1)
    print(f"Transitive closure of R: {R_trans}\n")

   
    # Connected components
    n2 = 7
    R2 = {(0, 4), (4, 2), (2, 3), (5,1), (6,6)}
    print(f"R: {R2}\n")
    components = find_connected_components(n2, R2)
    for idx, component in enumerate(components):
        print(f"Component {idx + 1}: {component}")

   
    '''
        Create graph for closures
    '''

    
    graph_R = nx.DiGraph()
    for (x, y) in R:
        graph_R.add_edge(x, y)

    graph_reflexive = nx.DiGraph()
    for (x, y) in R_reflex:
        graph_reflexive.add_edge(x, y)

    graph_symmetric = nx.DiGraph()
    for (x, y) in R_sym:
        graph_symmetric.add_edge(x, y)

    graph_transitive = nx.DiGraph()
    for (x, y) in R_trans:
        graph_transitive.add_edge(x, y)

   
    # 3D positions
    pos_R = nx.spring_layout(graph_R, dim=3)
    pos_reflexive = nx.spring_layout(graph_reflexive, dim=3)
    pos_symmetric = nx.spring_layout(graph_symmetric, dim=3)
    pos_transitive = nx.spring_layout(graph_transitive, dim=3)

    # Create subplots
    fig = plt.figure(figsize=(24, 18))  

    ax1 = fig.add_subplot(221, projection='3d')
    visualize_3d(graph_R, pos_R, "R", ax1)

    ax2 = fig.add_subplot(222, projection='3d')
    visualize_3d(graph_reflexive, pos_reflexive, "Reflexive Closure of R", ax2)

    ax3 = fig.add_subplot(223, projection='3d')
    visualize_3d(graph_symmetric, pos_symmetric, "Symmetric Closure of R", ax3)

    ax4 = fig.add_subplot(224, projection='3d')
    visualize_3d(graph_transitive, pos_transitive, "Transitive Closure of R", ax4)

    plt.suptitle("Red = irreflexive, Blue = reflexive")
    plt.show()

   
if __name__ == "__main__":
    main()

