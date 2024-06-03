'''
    For a frame F = (X, R), let ♢ R be the unary operation on the powerset P(X)
    defined as follows: for Y ⊆ X, ♢ R (Y) = R^−1 [Y]

    Exercise 2.16. Let (X, R) be a finite frame. For a family V of subsets of X,
    compute the smallest family [V] of subsets of X that contains V and is closed under
    set-theoretic operations and ♢ R .

    
    Set-theoretic operations

    Powerset closed under union, intersection, set difference
    https://proofwiki.org/wiki/Power_Set_is_Closed_under_Intersection
    

'''


"""
    Computes ♢R (Y) = R^−1 [Y]
"""
def diamond_R(Y, R):
    result = set()
    for (x, y) in R:
        if y in Y:
            result.add(x)
    return result


"""
    Returns the closure of V under set-theoretic operations
"""
def closure_under_set_theoretic_operations(V, X):
    closure = set(V)
    
    # Union, intersection, and complement of subsets in closure
    while True:
        new_sets = set(closure)

        for A in closure:
            new_sets.add(X - A)

            for B in closure:
                new_sets.add(A.union(B))
                new_sets.add(A.intersection(B))
            
        
        if new_sets == closure:
            break
        closure = new_sets
        
    return closure

"""
    Computes the smallest family [V] that contains V and 
    is closed under set-theoretic operations and ♢R
    
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
    

    return closure #set(map(set, closure))


def main():
    X = {0, 1, 2, 3}
    R = {(0, 1), (1, 3), (3, 0)}
    V = [{0,1,2}, {3}]
    result = compute_closure(V, R, X)
    print(f"X: {X}\nR: {R}\nV: {V}\nlength of [V]: {len(result)}\n[V]: {[set(x) for x in result]}\n")

    X = {0, 1, 2, 3, 4, 5}
    R = {(0, 1), (0,2),(1,2),(1,3),(2,3),(2,4),(3,4),(3,0),(4,0),(4,1)}
    V = [{5}]
    result = compute_closure(V, R, X)
    print(f"X: {X}\nR: {R}\nV: {V}\nlength of [V]: {len(result)}\n[V]: {[set(x) for x in result]}\n")

if __name__ == "__main__":
    main()