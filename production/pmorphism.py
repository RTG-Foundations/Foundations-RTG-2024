from itertools import product

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
        value is the mapped point in G
        F, G: frames containing an array of worlds and set of ordered pair relations
    Output:
        Returns whether f is a p-morphism from F to G
'''
def is_p_morphism(f, F, G):

    X1 = F.points
    X2 = G.points
    R1 = F.relation
    R2 = G. relation

    #  surjective
    mappedVals = []
    for key in f:
        mappedVals.append(f[key])

    if set(mappedVals) != set(X2):
        return False
    
    
    
    # for all x,y ∈ X1 we have x R1 y --> f(x) R2 f(y)
    for (x, y) in R1:
        if (f[x], f[y]) not in R2:
            return False
    

    # for all x ∈ X1, u ∈ X2 we have f(x) R2 u --> ∃ x' ∈ x1  x R1 x' and f(x') = u
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
    Generate all possible mappings from F to G
'''
def generate_mappings(F, G):
    
    functs = []
   
    # Generate all possible mappings from F.points to G.points
    all_mappings = product(G.points, repeat=len(F.points))
    for mapping in all_mappings:
        functs.append({x: mapping[i] for i, x in enumerate(F.points)})
        
    return functs


'''
    Exercise 2.13. 
    Given two finite frames F and G, to decide if F ↠ G.

    Time complexity:
    O(|G|^|F|) 
'''
def check_p_morphism(F, G):
    
    # surjective not possible
    if len(F.points) < len(G.points):
        return None
    
    candidate_functions = generate_mappings(F, G)
    for f in candidate_functions:
        if is_p_morphism(f, F, G):
            return f
    return None



def printAns(F,G, f):
    
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")

    if(f == None):
        print("G is NOT a p-morphic image of F")
    
    else:
        print("F ->-> G when: ")
        print("f = ")
        for x1 in f:
            x2 = f[x1]
            print(f"\t {{ {x1} --> {x2}")
    print()



def main():

    # good
    F = Frame(points=['a','b','c'], relation={('a', 'b'), ('a','c')})
    G = Frame(points=['e', 'd'], relation={('d','e')})
    f = check_p_morphism(F, G)
    printAns(F,G,f)

    F = Frame(points=['a','b','c'], relation={})
    G = Frame(points=['e', 'd'], relation={})
    f = check_p_morphism(F, G)
    printAns(F,G,f)

    F = Frame(points=[0,1,2], relation={(0, 1), (1,2)})
    G = Frame(points=['a'], relation={('a','a')})
    f = check_p_morphism(F, G)
    printAns(F,G,f)

    




if __name__ == "__main__":
    main()
