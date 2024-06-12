'''
    For a frame F = (X, R), let ♢ R be the unary operation on the powerset P(X)
    defined as follows: for Y ⊆ X, ♢ R (Y) = R^−1 [Y]
    Let (X, R) be a finite frame.
    
    Given a family V of subsets of X, 
    1)  Computes the smallest family [V] of subsets of X that contains V 
        and is closed under set-theoretic operations and ♢ R .
    2)  Computes the frame F/∼ [V]

    
    Given two finite frames F and G and a natural number m, decides if the
    frames are m-equivalent using the following condtion:
    F is a m-subset of G iff for all point generated subframes of F, 
    denoted F'=(X_F',R_F'), and for all U contained in the powerset of X_F', 
    where |U| = m, there exists a point generated subframe of G, 
    denoted G' = (XG', RG') and a V contained in the powerset of 
    XG' where |V| = m such that G'/~[v] ->-> F'/~[u]. 

'''


import pmorphism
from itertools import chain, combinations


"""
    Computes ♢R (Y) = R^−1 [Y]

    Input: 
        Y: a set contained in V
        R: set of (x,y) pairs representing relations from x to y
    Output:
        Return elements needed to close V under ♢R (Y)  

"""
def diamond_R(Y, R):
    result = set()
    for (x, y) in R:
        if y in Y:
            result.add(x)
    return result


"""
    Returns the closure of V under the set-theoretic operations
    union, intersection, and set difference
    
    Input:
        V: array of sets representing a family of subsets of X 
        X: all worlds in the Frame
    Output:
        Return the closure of V under union, intersection, 
        and set difference

"""
def closure_under_set_theoretic_operations(V, X):
    closure = set(V)
    
    while True:
        new_sets = set(closure)

        for A in closure:
            new_sets.add(X - A) # complement

            for B in closure:
                new_sets.add(A.union(B)) # union
                new_sets.add(A.intersection(B)) # intersection
            
        
        if new_sets == closure:
            break
        closure = new_sets
        
    return closure


"""
    Exercise 2.16
    For a frame F = (X, R), let ♢ R be the unary operation on the powerset P(X)
    defined as follows: for Y ⊆ X, ♢ R (Y ) = R −1 [Y ]
    
    Computes the smallest family [V] that contains V and  is closed under 
    set-theoretic operations and ♢ R

    Input:
        V: array of sets representing a family of subsets of X 
        R: set of (x,y) pairs representing relations from x to y
        X: all worlds in the frame
    Output:
        Return the closure of V under set-theoretic operations and ♢ R

"""
def compute_closure(V, R, X):
    closure = set(map(frozenset, V))
    X = frozenset(X)
    
    while True:
        new_closure = set(closure)
        
        # Add ♢R (Y) for each Y in closure
        for Y in closure:
            new_closure.add(frozenset(diamond_R(Y, R)))
        
        # Ensure closure under set-theoretic operations
        new_closure = closure_under_set_theoretic_operations(new_closure, X)
        
        if new_closure == closure:
            break
        
        closure = new_closure
    
    return closure


'''
    Helper method to display result of compute_closure

'''
def print_compute_closure(V,R,X, closure_V):
    print(f"X: {X}")
    print(f"R: {R}")
    print(f"V: {V}")
    
    if closure_V is None:
        print("Closure of V is empty")
    else:
        print(f"Length of [V]: {len(closure_V)}")
        
        print("[V] = {")
        for x in closure_V:
              print(f"\t{set(x)}")
        print("}\n")


"""
    Computes the equivalence classes in [V]
    Two elements a and b are in the same equivalence class if they 
    belong to exactly the same subsets in [V]

    Input:
        X: all worlds in the frame
        V_closure: closure of V under set operations and  ♢ R 
        to find equivalence classes in
    Output:
        return a dictionary where each key is a label  V0, V1, V2, ... 
        for the equivalence class, and each value is a set of 
        corresponding worlds 


"""
def equivalence_relation_V(X, V_closure):
   
    
    equivalence_classes = {}
    unprocessed = set(X)
    i = 0
    while unprocessed:
        eq_class = set()
        a = unprocessed.pop()

        eq_class.add(a)
        for b in X:
            if all((a in v) == (b in v) for v in V_closure):
                eq_class.add(b)
        
        equivalence_classes[f"V{i}"] = (frozenset(eq_class))
        unprocessed -= eq_class
        i += 1
    
    return equivalence_classes


"""
    Computes the induced relation on the equivalence classes

    Input: 
        classes: equivalence classes
        R: set of (x,y) pairs representing relations from x to y 
        in the original frame

    Output: 
        Returns a set of (x,y) pairs representing relations from x to y
        in the equivalence classes.
        
        Equivalence classes in the relation are represented by a label V0, V1, V2, ...

"""
def induced_relation(classes, R):
    induced_R = set()
    for name_a, class_a in classes.items():
        for name_b, class_b in classes.items():
            if any((a, b) in R for a in class_a for b in class_b):
                induced_R.add((name_a, name_b))
    return induced_R


'''
    Exercise 2.18.
    The structure A(F) = (P(X), ∪, ∩, −, ∅, X, ♢ R ) is called the modal
    algebra of F . The structure ([V], ∪, ∩, −, ∅, X, ♢ R ) is called the subalgebra of A(F)
    generated by V.
    
    For a frame F = (X, R) and an equivalence ∼, define the frame F/∼ = (X/∼, R̃),
    where [a] R̃[b] iff a ′ Rb ′ for some a ∼ a ′ and b ∼ b ′ .
    For a family V of subsets of X, consider the equivalence ∼ V on X:
    a ∼ b iff ∀V ∈ V (x ∈ V iff y ∈ V ).

    Given R and the smallest family [V] of subsets of X, computes the frame F/∼ [V].

    Input:
        X: all worlds in the frame
        R: set of (x,y) pairs representing relations from x to y in V
        V_closure: array of sets representing the closure of V under
        set-operations and ♢ R
        
    Output:
        I. a dictionary where each key is a label for  the equivalence class, 
        and each value is a set of corresponding worlds 
        II. a set of (x,y) pairs representing relations from x to y
        in the between the equivalence classes.


'''
def quotient_frame(X, R, V_closure):
    classes = equivalence_relation_V(X, V_closure)
    induced_R = induced_relation(classes, R)
    return classes, induced_R


'''
    Helper method to print the result of quotient_frame
'''
def print_quotient_frame(pts_sets, R):
    
    print("F/∼ [V]: ")
    print("X: ")
    for my_point, my_set in pts_sets.items():
        print(f"\t{my_point} : {set(my_set)}")
   
    print(f"R: {R}\n")


"""
    Generate the powerset of the set G
"""
def generate_powerset(G):
    n = len(G)
    powerset = []
    for i in range(1 << n):
        subset = {G[j] for j in range(n) if (i & (1 << j))}
        powerset.append(subset)
    return powerset


"""
    Generate combinations using Gosper's hack.
"""
def gosper_combination(n, k):
    c = (1 << k) - 1
    while c < (1 << n):
        yield c
        x = c & -c
        y = c + x
        c = (((c & ~y) // x) >> 1) | y

"""
    Convert a bit representation to a combination of sets

    """
def get_combination_from_bits(powerset, bits):
    return [powerset[i] for i in range(len(powerset)) if bits & (1 << i)]


"""
    Generate all combinations of m sets from the powerset of G using Gosper's hack.

"""
def generate_m_combinations_of_powerset(G, m):
    powerset = generate_powerset(G)
    n = len(powerset)
    combinations_of_sets = []
    
    for bits in gosper_combination(n, m):
        combination = get_combination_from_bits(powerset, bits)
        combinations_of_sets.append(combination)
    
    return combinations_of_sets



'''
    Determines if F is a m-subset of G using the following condition:
    F is a m-subset of G iff for all point generated subframes of F, 
    denoted F'=(X_F',R_F'), and for all U contained in the powerset of X_F', 
    where |U| = m, there exists a point generated subframe of G, 
    denoted G' = (XG', RG') and a V contained in the powerset of 
    XG' where |V| = m such that G'/~[v] ->-> F'/~[u]. 

    Input:
        F, G: frames containing an array of worlds and set of ordered pair relations
        m: positive integer

    Output:
        Return whether F is a m-subset of G

'''
def m_subset(F,G,m):


    # for all point-generated subframes of F
    for nodeF in F.points:
        reachable = pmorphism.find_reachable(F.points, nodeF, F.relation)
        subrelation = {(x, y) for x, y in F.relation if x in reachable and y in reachable}
        sub_F = pmorphism.Frame(reachable, subrelation)

        # generate all possible combinations of m sets from the powerset of F
        F_subsets = generate_m_combinations_of_powerset(list(sub_F.points), m)
       
        for U in F_subsets:

            # F/∼ [U]
            closure = compute_closure(U, F.relation, F.points)
            pts_sets, eq_R = quotient_frame(F.points, F.relation, closure)
            points = pts_sets.keys()
            F_quotient = pmorphism.Frame(points,eq_R)
        

            foundGPrime = False
            for nodeG in G.points: 
                reachable = pmorphism.find_reachable(G.points, nodeG, G.relation)
                subrelation = {(x, y) for x, y in G.relation if x in reachable and y in reachable}
                sub_G = pmorphism.Frame(reachable, subrelation)
            
                # generate all possible combinations of m sets from the powerset of G
                G_subsets = generate_m_combinations_of_powerset(list(sub_G.points), m)
                
                for V in G_subsets:
                    
                    # G/∼ [V]
                    closure = compute_closure(V, G.relation, G.points)
                    pts_sets, eq_R = quotient_frame(G.points, G.relation, closure)
                    points = pts_sets.keys()
                    G_quotient = pmorphism.Frame(points,eq_R)

                    # Check G'/~[v] ->-> F'/~[u]
                    f = pmorphism.check_p_morphism(G_quotient, F_quotient)
                    if f is not None:
                        foundGPrime = True
                        break

                if foundGPrime:
                    break

            if not foundGPrime:
                return False
           
    return True
        

'''
    Problem 2.15. 
    Given two finite frames and a natural number m, to decide if the
    frames are m-equivalent.

    Input:
        F, G: frames containing an array of worlds and set of ordered pair relations
        m: positive integer
    Output: Return whether F is a m-subset of G

'''
def mEquiv(F,G,m):
    return m_subset(F, G,m) and m_subset(G, F,m)


'''
    Write the result of mEquiv() to M_Equivalent.txt
'''
def write_mEquiv(F,G,m, result):
    with open("M_Equivalent.txt", "a") as file:
        file.write(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}\n")
        file.write(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}\n")
        file.write(f"{m}-Equivalent? {result}\n\n")    
    print_mEquiv(F,G,m, result)


'''
    Print the result of mEquiv() 
'''
def print_mEquiv(F,G,m, result):
    print(f"F(X1, R1): X1 = {F.points}, R1 = {F.relation}")
    print(f"G(X2, R2): X2 = {G.points}, R2 = {G.relation}")
    print(f"{m}-Equivalent? {result}\n")



def main():

    F = pmorphism.Frame(points=[0,1,2,3,4], relation={(0, 1),(1,0),(1,3),(3,1),(2,3),(3,2),(0,2),(2,0),(2,1),(1,2),(0,3),(3,0),(0,4),(4,0),(1,4),(4,1),(2,4),(4,2),(3,4),(4,3)})
    G = pmorphism.Frame(points=[0,1,2,3], relation={(0, 1),(1,0),(1,3),(3,1),(2,3),(3,2),(0,2),(2,0),(2,1),(1,2),(0,3),(3,0),(3,3)})

    m = 2
    result = mEquiv(F,G, m) # true
    write_mEquiv(F,G,m, result)
    
    m = 3
    result = mEquiv(F,G, m) # false
    write_mEquiv(F,G,m, result)


    F = pmorphism.Frame(points=[0,1,2,3], relation={(0, 1),(1,0),(1,3),(3,1),(2,3),(3,2),(0,2),(2,0),(2,1),(1,2),(0,3),(3,0)})
    G = pmorphism.Frame(points=[0,1,2,3], relation={(0, 1),(1,0),(1,3),(3,1),(2,3),(3,2),(0,2),(2,0),(2,1),(1,2),(0,3),(3,0),(3,3)})
    m = 1
    result = mEquiv(F,G, m) # true
    write_mEquiv(F,G,m, result)
    
    m = 2
    result = mEquiv(F,G, m)
    write_mEquiv(F,G,m, result)  # false


    X = {0, 1, 2, 3,4,5,6,7,8,9,10,11}
    R = {(0, 1), (1,2),(2,3),(3,4),(4,5),(5,0),(6,7),(7,8),(8,9),(9,10),(10,11),(11,6)}
    V = [{0,6}]
    
    # [V]
    closure_V = compute_closure(V, R, X)
    print_compute_closure(V,R,X, closure_V)
    # F/∼ [V]
    eq_pts_sets, eq_R = quotient_frame(X, R, closure_V)
    print_quotient_frame(eq_pts_sets, eq_R)

    X = {0, 1, 2, 3,4,5}
    R = {(0, 1), (0,2),(1,3),(1,4),(2,4),(2,5)}
    V = [{0,1},{2,4}]
    
    # [V]
    closure_V = compute_closure(V, R, X)
    print_compute_closure(V,R,X, closure_V)
    # F/∼ [V]
    eq_pts_sets, eq_R = quotient_frame(X, R, closure_V)
    print_quotient_frame(eq_pts_sets, eq_R)
    

    X = {0, 1, 2, 3}
    R = {(0, 1), (1, 3), (3, 0)}
    V = [{0,1,2,3}, {1,2,3}]

    # [V]
    closure_V = compute_closure(V, R, X)
    print_compute_closure(V,R,X, closure_V)
    # F/∼ [V]
    eq_pts_sets, eq_R = quotient_frame(X, R, closure_V)
    print_quotient_frame(eq_pts_sets, eq_R)

    X = {0, 1, 2, 3, 4, 5}
    R = {(0, 1), (0,2),(1,2),(1,3),(2,3),(2,4),(3,4),(3,0),(4,0),(4,1)}
    V = [{5}]
    
    # [V]
    closure_V = compute_closure(V, R, X)
    print_compute_closure(V,R,X, closure_V)
    # F/∼ [V]
    eq_pts_sets, eq_R = quotient_frame(X, R, closure_V)
    print_quotient_frame(eq_pts_sets, eq_R)


    m = 2
    F = pmorphism.Frame(points=[0,1,2], relation={(0, 1),(1,0),(1,2), (2,1)})
    result = mEquiv(F,F, m)
    print_mEquiv(F,F,m, result)

    m = 1
    F = pmorphism.Frame(points=[0,1,2], relation={(0, 1),(1,0),(1,2), (2,1)})
    G = pmorphism.Frame(points=[0,1,2], relation={(0, 1), (1,0), (1,2), (2,1), (2,2)})
    result = mEquiv(F,G, m)
    print_mEquiv(F,G,m, result)
    

    
   
if __name__ == "__main__":
    main()