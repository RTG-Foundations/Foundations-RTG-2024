
import time
import random
from collections import deque
import json
'''
    Defines a Frame

    Input:
        self: calling method
        points: array of worlds 
        relation: set of (x,y) pairs representing relation from x to y
        
    Output: Creates a Frame object


'''
class Frame:
    def __init__(self, points, relation):
        self.points = points
        self.relation = relation

    def __repr__(self):
        return f"Frame(points={self.points}, relation={self.relation})"


'''
    Input:
        f: dictionary representing the SURJECTIVE mapping, where each key is a point in F, and each
        value is the mapped point in G. 
        F, G: frames containing an array of worlds and set of ordered pair relations
    Output:
        Returns whether f is a p-morphism from F to G
'''
def is_p_morphism(f, F, G):

    X1 = F.points
    X2 = G.points
    R1 = F.relation
    R2 = G.relation

    # surjective 
    mappedVals = []
    for key in f:
        mappedVals.append(f[key])

    if set(mappedVals) != set(X2):
        return False
    
    # for all x,y ∈ X1, if x R1 y --> f(x) R2 f(y)
    for (x, y) in R1:
        if (f[x], f[y]) not in R2:
            return False
    

    # for all x ∈ X1, u ∈ X2 , if f(x) R2 u --> ∃ x' ∈ x1  x R1 x' and f(x') = u
    for x in X1:
        for u in X2:
            if (f[x], u) in R2:
                found = False
                
                for x_prime in X1:
                    if (x, x_prime) in R1 and f[x_prime] == u:
                        found = True
                        break
               
                if not found:
                    return False
    
    # all conditions hold
    return True


'''
    Incrementally build a mapping f, while checking if the current partial 
    mapping can potentially lead to a valid p-morphism. 
    If a valid mapping is found, return True; otherwise, backtrack.

'''
def build_pMorph(F, G, k, f, points_F, points_G):
    R = F.relation
    S = G.relation
    n = len(points_F)
    
    # Base case: all points in F are assigned to G. 
    # Return whether f is p-morphism
    if k >= n:
        return(is_p_morphism(f, F, G))
          
    for y in points_G:
        f[points_F[k]] = y

        valid = True
        # Forward condition
        for i in range(k):
            if (points_F[i], points_F[k]) in R and (f[points_F[i]], f[points_F[k]]) not in S:
                valid = False
                break
            if (points_F[k], points_F[i]) in R and (f[points_F[k]], f[points_F[i]]) not in S:
                valid = False
                break


        # Back condition
        # for all x ∈ X1, u ∈ X2 , if f(x) R2 u --> ∃ x' ∈ x1  x R1 x' and f(x') = u
        if valid == True:
            for i in range(k):
                
                for j in points_G:
                    if (f[points_F[i]], j) in S:
                        valid = False
                        for p in range(n):
                            if ((p < k) and (points_F[i],points_F[p]) in R and f[points_F[p]] == j)\
                                or ((p >= k) and (points_F[i], points_F[p]) in R):
                                valid = True
                                break
                            
                        if valid == False:
                            break

        if valid and build_pMorph(F, G, k + 1, f, points_F, points_G):
            return True
    return False





'''
    Exercise 2.13. 
    Given two finite frames F and G, decide if F ↠ G.

    Input:
        F, G: frames containing an array of worlds and set of ordered pair relations
    
    Output: 
        If possible, return a mapping f such that F ↠ G. Otherwise, return None
    
    Time complexity:
    O(|G|^|F|) 
'''
def check_p_morphism(F, G):
    # surjective not possible
    if len(F.points) < len(G.points):
        return None

    f = {}
    if build_pMorph(F, G, 0, f, list(F.points), list(G.points)):
        return f
    return None


'''
    Helper method to display result of check_p_morphism
'''
def printIsPMorph(F,G, f):
    result = []
    result.append(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    result.append(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    
    if f is None:
        result.append("G is NOT a p-morphic image of F")
    else:
        result.append("F ->-> G when:")
        result.append("f =")
        for x1 in f:
            x2 = f[x1]
            result.append(f"{{ {x1} --> {x2} }}")
    
    print("\n".join(result))
    return "\n".join(result)
    
   


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


'''
    Exercise 2.7
    Input: 
        worlds: set of all possible worlds
        start: starting world
        R: set of (x,y) pairs representing relation from x to y
        
    Output: set of the reachable worlds from the start node
'''
def find_reachable(worlds, start, R):
    
    # Write the graph as dictionary,  
    # where each key is a node, and each 
    # value is an array of neighbors
    graph = {}
    
    for world in worlds:
        graph[world] = []

    for (a, b) in R:
        graph[a].append(b) 

    # Find connected components starting from l using BFS
    reachable =  bfs(graph, start)

    return reachable


'''
    Returns whether Log(F) ⊆ Log(G)
'''
def log_subset(F, G):
    subframes_F = []
    for node in F.points:
        reachable = find_reachable(F.points, node, F.relation)
        subrelation = {(x, y) for x, y in F.relation if x in reachable and y in reachable}
        subframes_F.append(Frame(reachable, subrelation))
    
    subframes_G = []
    for node in G.points:
        reachable = find_reachable(G.points, node, G.relation)
        subrelation = {(x, y) for x, y in G.relation if x in reachable and y in reachable}
        subframes_G.append(Frame(reachable, subrelation))


    # Exercise 1.10
    # Let F be a pretransitive frame, G a finite point-generated frame.
    # Log(F) ⊆ Log(G ) iff F′ ↠ G for some point-generated subframe F′ of F.
    for sub_G in subframes_G:
        foundFPrime = False
        for sub_F in subframes_F:
            f = check_p_morphism(sub_F, sub_G)
            if f is not None:
                foundFPrime = True
                break
        
        if foundFPrime == False:
            return False
    
    return True

'''
    Helper method to display result of log_equal
'''        
def printLogEqual(F,G, result):
    output = []
    output.append(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    output.append(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    if (result == True):
        output.append("Log(F) = Log(G)")
    else:
        output.append("Log(F) != Log(G)")
    
    print("\n".join(output))
    return "\n".join(output)


   


'''
    Exercise 2.14
    Given two finite frames F and G, decide if Log(F) = Log(G). 
'''
def log_equal(F, G):
    return log_subset(F, G) and log_subset(G, F)






'''
    Generate a random frame of specified size c
'''
def generate_random_frame(c):
    points = set(range(c)) #  {0, 1, ..., n-1}
    relation = set() 
    max_relations = c * (c - 1) // 2  # Max number of relations

    for _ in range(random.randint(1, max_relations)): # number of relations to add
        x = random.choice(tuple(points)) 
        y = random.choice(tuple(points)) 
        relation.add((x, y)) # add (x,y) to relation set
    
    return Frame(points, relation)



def main():
    
    '''
        Known Examples
    '''
    # Exercise 2.13
    F = Frame(points=['a','b','c'], relation={('a', 'b'), ('a','c')})
    G = Frame(points=['e', 'd'], relation={('d','e')})
    f = check_p_morphism(F, G)
    printIsPMorph(F,G,f) # True

    F = Frame(points=['a','b','c'], relation={})
    G = Frame(points=['e', 'd'], relation={})
    f = check_p_morphism(F, G)
    printIsPMorph(F,G,f) # True

    F = Frame(points=[0,1,2], relation={(0, 1), (1,2)})
    G = Frame(points=['a'], relation={('a','a')})
    f = check_p_morphism(F, G)
    printIsPMorph(F,G,f) # False


    # Exercise 2.14
    F = Frame(points=[0,1,2,3,4,5], relation={(0, 1),(2,3),(4,5)})
    G = Frame(points=[0,1,2,3,4,5], relation={(1,2), (3,4), (5,0)})
    printLogEqual(F, G, log_equal(F, G)) # True

    F = Frame(points=['a','b','c'], relation={('a', 'b'), ('a','c')})
    printLogEqual(F, F, log_equal(F, F)) # True

    F = Frame(points=['x'], relation={})
    G = Frame(points=[0,1], relation={})
    printLogEqual(F, G, log_equal(F, G)) # True

    F = Frame(points=[0,1,2,3], relation={(0,1),(2,3)})
    G = Frame(points=['a','b'], relation={('a','b')})
    printLogEqual(F, G, log_equal(F, G)) # True
   
    F = Frame(points = {0, 1, 2}, relation={(0, 1), (1, 2)})
    G = Frame(points = {0, 1, 2, 3}, relation = {(0, 1), (1, 2), (2, 3)})
    printLogEqual(F, G, log_equal(F, G)) # False

    
    


    '''
        Time needed to run check_p_morphism(F, G)
    '''

    F_card = int(input("Enter |F|: "))
    G_card = int(input("Enter |G|: "))

    F = generate_random_frame(F_card)
    G = generate_random_frame(G_card)

    print("Frame F:", F)
    print("Frame G:", G)
    
    
    start_time = time.time()
    f = check_p_morphism(F, G)
    end_time = time.time()
    ellapsed = (end_time -start_time) * 1e9
    

    if ellapsed != None:
        with open("pMorphism_backtracking_times.txt", "a") as file:
            file.write(f"|F| = {len(F.points)} |G| = {len(G.points)} F->->G? {f != None}\n")
            file.write(f"\tTime (ns): {ellapsed}\n")
    

    print(f"|F| = {len(F.points)} |G| = {len(G.points)} F->->G? {f != None}\n")
    print(f"\tTime (ns): {ellapsed}\n")
   





if __name__ == "__main__":
    main()
