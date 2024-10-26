
import time
import random
import math
from itertools import product
import os
import sys 

# Get absolute path to program's data directory
def get_data_file_path(filename):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, filename)

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
        f: dictionary representing the mapping, where each key is a point in F, and each
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
    Helper method to display result of p-morphism methods
'''
def printIsPMorph(f):
    
    
    isPMorp = (f != None and f != [])
    if(not isPMorp):
        print("G is NOT a p-morphic image of F")
    
    else:
        print("F ->-> G when: ")
        print("f = ")
        for x1 in  f:
            x2 = f[x1]
            print(f"\t {{ {x1} --> {x2}")
    print()





'''
    Generate a random frame of specified size c
   
'''
def generate_random_frame(c):
    points = set(range(c)) #  {0, 1, ..., n-1}
    relation = set() 
    max_relations =  math.ceil(math.log(c))  # Max number of relations
   
    for _ in range(max_relations): # number of relations to add random.randint(1, max_relations)
        x = random.choice(tuple(points)) 
        y = random.choice(tuple(points)) 
        relation.add((x, y)) # add (x,y) to relation set

     # 10% chance
    '''
    for i in range(c):
        for j in range(c):
            if random.random() < .001:
                relation.add((i,j))
    '''
    
    return Frame(points, relation)

   



'''
    
    ******************  FORWARD AND BACK ****************

'''





def pMorphForwardBack(F, G, k, f, points_F, points_G, results):
    R = F.relation
    S = G.relation
    n = len(points_F)
    
    if k >= n:
        if is_p_morphism(f, F, G):
            results.append(f.copy())
        return # changed from return True

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
                            if ((p < k) and (points_F[i],points_F[p]) in R and f[points_F[p]] == j):
                                valid = True
                                break
                            elif ((p >= k) and (points_F[i], points_F[p]) in R):
                                valid = True
                                break
                            
                        if valid == False:
                            print("BACK CONDITION BROKE")
                            break
                        
        
        if valid:
            pMorphForwardBack(F, G, k + 1, f,  points_F, points_G, results)
          
    return results 


def check_pMorph_forward_back(F, G):
    points_F = list(F.points)
    points_G = list(G.points)
    n = len(points_F)
    m = len(points_G)
    if n < m:
        return None

    f = {}
    results = []
    results =  pMorphForwardBack(F, G, 0, f,  points_F, points_G, results)
    return results

'''
    FORWARD ONLY
'''
def pMorphForward(F, G, k, f, points_F, points_G, results):
    R = F.relation
    S = G.relation
    n = len(points_F)
    
    if k >= n:
        if is_p_morphism(f, F, G):
            results.append(f.copy())
        return # changed from return True

    for y in points_G:
        #if y not in assigned  or set(assigned) == set(G.points):
        f[points_F[k]] = y
        #assigned.append(y)

        valid = True
        # Forward condition
        for i in range(k):
            if (points_F[i], points_F[k]) in R and (f[points_F[i]], f[points_F[k]]) not in S:
                valid = False
                break
            if (points_F[k], points_F[i]) in R and (f[points_F[k]], f[points_F[i]]) not in S:
                valid = False
                break

        if valid:
            pMorphForward(F, G, k + 1, f, points_F, points_G, results)

        #assigned.remove(y)

    return results 


def check_pMorph_forward(F, G):
    points_F = list(F.points)
    points_G = list(G.points)
    n = len(points_F)
    m = len(points_G)
    if n < m:
        return None

    f = {}
    #assigned = []
    results = []
    results =  pMorphForward(F, G, 0, f, points_F, points_G, results)
    return results




'''
 
    ******************  CONSTRAINT-SATISFACTION ****************

'''

'''


variables with possible values which fall into ranges known as domains.
 Constraints between the variables must be satisfied in order for constraint-satisfaction problems to be solved.
 


'''


from constraint import Problem

def check_pMorph_csp(F, G):
    if len(F.points) < len(G.points):
        return None

    problem = Problem()

    # Add variables with domains
    for x in F.points:
        problem.addVariable(x, list(G.points))

    # Add surjectivity constraint
    def surjectivity(*args):
        surj = set(args) == set(G.points)
        return surj

    problem.addConstraint(surjectivity, F.points)

    # Add the homomorphism constraint
    def homomorphism_constraint(*args):
        f = dict(zip(F.points, args))
        for (x, y) in F.relation:
            if (f[x], f[y]) not in G.relation:
                return False
        return True

    # Add the back condition constraint
    def back_condition_constraint(*args):
        f = dict(zip(F.points, args))
        for x in F.points:
            for u in G.points:
                if (f[x], u) in G.relation:
                    found = False
                    for x_prime in F.points:
                        if (x, x_prime) in F.relation and f[x_prime] == u:
                            found = True
                            break
                    if not found:
                        return False
        return True

    problem.addConstraint(homomorphism_constraint, F.points)
    problem.addConstraint(back_condition_constraint, F.points)

    # find one solution
    '''
    solution = problem.getSolution()
    if solution:
        return solution  
    return None
    '''
    # Find  ALL solutions
    
    solutions = problem.getSolutions()
    if solutions:
        return solutions
    return None
    




'''
 
    ******************  BACKTRACKING ****************

'''

'''
    Incrementally build a mapping f, while checking if the current partial 
    mapping can potentially lead to a valid p-morphism. 
    If a valid mapping is found, return True; otherwise, backtrack.
'''
def backtrack(f, F, G, assigned, results):
    
    X1 = F.points
    X2 = G.points
    
    # Base case: all points in F are assigned to G. 
    # Return whether f is p-morphism
    if len(f) == len(X1):
        if is_p_morphism(f,F,G):
            results.append(f.copy())
        return # changed from return True

    # map x --> u where x in X1 and u in X2
    for x in X1:
        if x not in f: # Only consider unassigned points in X1
            for u in X2:
    
                # Assign u to x
                f[x] = u
                assigned.append(u) 
                
                # Recursively build the mapping
                backtrack(f, F, G, assigned, results)
                    
                del f[x]  # Backtrack: remove the assignment
                assigned.remove(u)   # Backtrack: unmark u as assigned

            return results # No valid assignment found for this x
        
    return results



def check_pMorph_backtracking(F, G):
    # surjective not possible
    if len(F.points) < len(G.points):
        return None

    f = {}
    assigned = []
    results = []
    results = backtrack(f, F, G, assigned, results)
    return results

'''
    ENUMERATION
'''
def generate_mappings(F, G):
    
    functs = []
   
    # Generate all possible mappings from F.points to G.points
    all_mappings = product(G.points, repeat=len(F.points))
    for mapping in all_mappings:
        functs.append({x: mapping[i] for i, x in enumerate(F.points)})
        
    return functs


def check_pMorph_enum(F, G):
    
    # surjective not possible
    if len(F.points) < len(G.points):
        return None
    
    results = []
    candidate_functions = generate_mappings(F, G)
    for f in candidate_functions:
        if is_p_morphism(f, F, G):
            results.append(f)
    return results



'''
    Run all p-morphism methods and record execution time

'''
def runCompare(F,G):

    print("Recursively build to satisfy homomorphism condition: ")
    start_time = time.time()
    results = check_pMorph_forward(F, G)
    end_time = time.time()
    ellapsed = (end_time -start_time) * 1e9
    recordTime(ellapsed, len(results), len(F.points), len(G.points), "Forward" )

    print("Recursively build to satisfy homomorphism and back condition: ")
    start_time = time.time()
    results = check_pMorph_forward_back(F, G)
    end_time = time.time()
    ellapsed = (end_time -start_time) * 1e9
    recordTime(ellapsed, len(results), len(F.points), len(G.points), "Forward and back" )

    print("Recursively build using backtracking: ")
    start_time = time.time()
    results = check_pMorph_backtracking(F, G)
    end_time = time.time()
    ellapsed = (end_time -start_time) * 1e9
    recordTime(ellapsed, len(results), len(F.points), len(G.points), "Back-tracking" )


    '''
    print("Build using Python's CSP library: ")
    start_time = time.time()
    results = check_pMorph_csp(F, G)
    end_time = time.time()
    ellapsed = (end_time -start_time) * 1e9
    if results == None:
        num_results = 0
    else:
        num_results =  len(results)
    recordTime(ellapsed, num_results, "CSP" )
    '''

    print("Check all possible mappings: ")
    start_time = time.time()
    results = check_pMorph_enum(F, G)
    end_time = time.time()
    ellapsed = (end_time -start_time) * 1e9
    recordTime(ellapsed, len(results), len(F.points), len(G.points),"Enumeration" )



def recordTime(ellapsed, num_found, F_card, G_card, name):

    with open("times/pMorphism_times.txt", "a") as file:
        file.write(f"|F| = {F_card} |G| = {G_card}\n")
        file.write(f"\tMethod: {name}. Number of p-morphs: {num_found}. Time (ns): {ellapsed}\n")

    print(f"\tMethod: {name}. Number of p-morphs: {num_found}. Time (ns): {ellapsed}\n")
    
    





def main():
    
    F = Frame(points=[0,1,2,3,4,5,6], relation={(1,3),(6,4)})
    G = Frame(points=[0,1,2,3,4,5], relation={(5,4),(3,2)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)
    
    
    output_path = get_data_file_path("times") 
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created output directory {output_path}")
    
    while True:
        F_card = int(input("Enter |F|: "))
        G_card = int(input("Enter |G|: "))
    
        F = generate_random_frame(F_card)
        G = generate_random_frame(G_card)

        print("Frame F:", F)
        print("Frame G:", G)
        runCompare(F,G)

    '''
        Known Examples

    '''
    '''
    
    F = Frame(points=[0,1,2,3,4,5], relation={(0,0), (0,1),(1,2),(2,0),(3,3),(3,4),(4,5),(5,3)})
    G = Frame(points=[0,1,2], relation={(0,0),(0,1),(1,2),(2,0)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)
    


    F = Frame(points=[0,1,2,3], relation={(0,1),(1,3),(0,2),(2,3),(0,3)})
    G = Frame(points=[0,1], relation={(0,0)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)
    
  
    F = Frame(points=[0,1,2], relation={(0,0),(1,1),(2,2),(0,1),(1,0),(0,2),(2,0),(1,2),(2,1)})
    G = Frame(points=[0], relation={(0,0)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)

   

    F = Frame(points=[0,1,2,3], relation={(0,0),(3,3),(3,2), (2,1), (1,0)})
    G = Frame(points=[0,1,2,3], relation={(0,0),(0,1),(1,2),(2,3), (3,3)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)

    
    

    F = Frame(points=[0,1,2,3,4], relation={(3,3),(3,2), (2,1), (1,0),(0,4)})
    G = Frame(points=[0,1,2,3], relation={(0,0),(0,1),(1,2),(2,3)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)

    F = Frame(points=['a','b','c'], relation={('a', 'b'), ('a','c')})
    G = Frame(points=['e', 'd'], relation={('d','e')})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)



    F = Frame(points=[0, 1,2], relation={})
    G = Frame(points=[0,1], relation={})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)

    F = Frame(points=[0,1,2], relation={(0, 1), (1,2)})
    G = Frame(points=[0], relation={(0,0)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    runCompare(F,G)
    '''


if __name__ == "__main__":
    main()
