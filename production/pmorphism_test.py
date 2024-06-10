
import time
import random

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





def printIsPMorph_array(f):
    
    
    isPMorp = (f != None)
    if(not isPMorp):
        print("G is NOT a p-morphic image of F")
    
    else:
        print("F ->-> G when: ")
        print("f = ")
        for x1 in  range(len(f)):
            x2 = f[x1]
            print(f"\t {{ {x1} --> {x2}")
    print()

'''
    Helper method to display result of p-morphism methods
'''
def printIsPMorph(f):
    
    
    isPMorp = (f != None)
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
    max_relations = c * (c - 1) // 2  # Max number of relations

    for _ in range(random.randint(1, max_relations)): # number of relations to add
        x = random.choice(tuple(points)) 
        y = random.choice(tuple(points)) 
        relation.add((x, y)) # add (x,y) to relation set
    
    return Frame(points, relation)




'''
    
    ******************  FORWARD ****************

'''





def pMorph(F, G, k, f, assigned, points_F, points_G):
    n = len(points_F)
    m = len(points_G)
    R = F.relation
    S = G.relation

    if k >= n:
        return is_p_morphism(f, F, G)

    for y in points_G:
        if y not in assigned  or set(assigned) == set(G.points):
            f[points_F[k]] = y
            assigned.append(y)

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
            
            for i in range(k):
                if (f[points_F[k]], f[points_F[i]]) in S:
                    if not any((points_F[k], points_F[j]) in R and f[points_F[j]] == f[points_F[i]] for j in range(k)):
                        valid = False
                        break
                if (f[points_F[i]], f[points_F[k]]) in S:
                    if not any((points_F[j], points_F[k]) in R and f[points_F[j]] == f[points_F[i]] for j in range(k)):
                        valid = False
                        break
            
            if valid and pMorph(F, G, k + 1, f, assigned, points_F, points_G):
                return True

            assigned.remove(y)

    return False

def check_pMorph_forward(F, G):
    points_F = list(F.points)
    points_G = list(G.points)
    n = len(points_F)
    m = len(points_G)
    if n < m:
        return None

    f = {}
    assigned = []
    if pMorph(F, G, 0, f, assigned, points_F, points_G):
        return f
    return None


'''
 
    ******************  CONSTRAINT-SATISFACTION ****************

'''

'''


variables with possible values which fall into ranges known as domains.
 Constraints between the variables must be satisfied in order for constraint-satisfaction problems to be solved.
 


'''


from constraint import Problem, AllDifferentConstraint

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

    solution = problem.getSolution()
    if solution:
        return solution  
    return None

    # Find  ALL solutions
    '''
    solutions = problem.getSolutions()
    if solutions:
        return solutions
    return None
    '''




'''
 
    ******************  BACKTRACKING ****************

'''

'''
    Incrementally build a mapping f, while checking if the current partial 
    mapping can potentially lead to a valid p-morphism. 
    If a valid mapping is found, return True; otherwise, backtrack.
'''
def backtrack(f, F, G, assigned):
    
    X1 = F.points
    X2 = G.points
    
    # Base case: all points in F are assigned to G. 
    # Return whether f is p-morphism
    if len(f) == len(X1):
        #print(f)
        return is_p_morphism(f, F, G)

    # map x --> u where x in X1 and u in X2
    for x in X1:
        if x not in f: # Only consider unassigned points in X1
            for u in X2:
                # Don't re-assign u to x unless all points in X2 mapped
                if u not in assigned or set(assigned) == set(X2):
                    # Assign u to x
                    f[x] = u
                    assigned.append(u) 
                    
                    # Recursively build the mapping
                    if backtrack(f, F, G, assigned): 
                        return True # Found a valid p-morphism
                    del f[x]  # Backtrack: remove the assignment
                    assigned.remove(u)   # Backtrack: unmark u as assigned

            return False  # No valid assignment found for this x
        
    return False  



def check_pMorph_backtracking(F, G):
    # surjective not possible
    if len(F.points) < len(G.points):
        return None

    f = {}
    assigned = []
    if backtrack(f, F, G, assigned):
        return f
    return None




def main():

    '''
        Known Examples
    '''

    F = Frame(points=[0,1,2], relation={(0,0),(1,1),(2,2),(0,1),(1,0),(0,2),(2,0),(1,2),(2,1)})
    G = Frame(points=[0], relation={(0,0)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    print("ELIMINATION BY FORWARD CONDITION: ")
    f = check_pMorph_forward(F, G)
    printIsPMorph(f) # True

    F = Frame(points=[0,1,2,3], relation={(0,0),(3,3),(3,2), (2,1), (1,0)})
    G = Frame(points=[0,1,2,3], relation={(0,0),(0,1),(1,2),(2,3), (3,3)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    print("ELIMINATION BY FORWARD CONDITION: ")
    f = check_pMorph_forward(F, G)
    printIsPMorph(f) # True

    F = Frame(points=[0,1,2,3,4], relation={(3,3),(3,2), (2,1), (1,0),(0,4)})
    G = Frame(points=[0,1,2,3], relation={(0,0),(0,1),(1,2),(2,3)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    print("ELIMINATION BY FORWARD CONDITION: ")
    f = check_pMorph_forward(F, G)
    printIsPMorph(f) # True
    

    # Exercise 2.13
    F = Frame(points=['a','b','c'], relation={('a', 'b'), ('a','c')})
    G = Frame(points=['e', 'd'], relation={('d','e')})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    print("ELIMINATION BY FORWARD CONDITION: ")
    f = check_pMorph_forward(F, G)
    printIsPMorph(f) # True
    

    print("CSP: ")
    f = check_pMorph_csp(F, G)
    printIsPMorph(f) # True


    print("BACK-TRACKING: ")
    f = check_pMorph_backtracking(F, G)
    printIsPMorph(f) # True
    



    F = Frame(points=[0, 1,2], relation={})
    G = Frame(points=[0,1], relation={})
    f = check_pMorph_forward(F, G)
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    print("ELIMINATION BY FORWARD CONDITION: ")
    f = check_pMorph_forward(F, G)
    printIsPMorph_array(f) # True
    

    print("CSP: ")
    f = check_pMorph_csp(F, G)
    printIsPMorph(f) # True


    print("BACK-TRACKING: ")
    f = check_pMorph_backtracking(F, G)
    printIsPMorph(f) # True

    F = Frame(points=[0,1,2], relation={(0, 1), (1,2)})
    G = Frame(points=[0], relation={(0,0)})
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    print("ELIMINATION BY FORWARD CONDITION: ")
    f = check_pMorph_forward(F, G)
    printIsPMorph_array(f) # False
    

    print("CSP: ")
    f = check_pMorph_csp(F, G)
    printIsPMorph(f) # False


    print("BACK-TRACKING: ")
    f = check_pMorph_backtracking(F, G)
    printIsPMorph(f) # False





    '''
        Time needed to run check_pMorph_forward(F, G)
    '''

    F_card = int(input("Enter |F|: "))
    G_card = int(input("Enter |G|: "))

    F = generate_random_frame(F_card)
    G = generate_random_frame(G_card)

    print("Frame F:", F)
    print("Frame G:", G)
    
    
    start_time = time.time()
    f = check_pMorph_forward(F, G)
    end_time = time.time()
    ellapsed = (end_time -start_time) * 1e9
    

    if ellapsed != None:
        with open("pMorphism_forward_times.txt", "a") as file:
            file.write(f"|F| = {len(F.points)} |G| = {len(G.points)} F->->G? {f != None}\n")
            file.write(f"\tTime (ns): {ellapsed}\n")
    

    print(f"|F| = {len(F.points)} |G| = {len(G.points)} F->->G? {f != None}\n")
    print(f"\tTime (ns): {ellapsed}\n")
    





if __name__ == "__main__":
    main()
