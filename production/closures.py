
'''
Input: a positive integer n; a relation R on Xn
Output: the smallest relation R'
that contains R and is reflexive (such a relation is
called the reflexive closure of R).
'''
def reflexive_closure(n, R):
    # copy R as set with original relations
    R_prime = set(R)

    # Add reflexive pairs if needed
    for i in range(n):
        if (i, i) not in R_prime:
            R_prime.add((i, i))

    return R_prime


'''
Input: a positive integer n; a relation R on Xn
Output: the smallest relation R'
that contains R and is symmetric (such a relation
is called the symmetric closure of R).
'''
def symmetric_closure(n, R):
    # copy R as set with original relations
    R_prime = set(R)

    # Add pairs for symmetric
    for (a, b) in R:
        if (b, a) not in R_prime:
            R_prime.add((b, a))

    return R_prime

'''
Input: a positive integer n; a relation R on Xn
Output: the transitive closure of R.
'''
def transitive_closure(n, R):
    # copy R as set with original relations
    R_prime = set(R)

    # Add pairs for transitive 
    for (a, b) in R:
        for (c, d) in R:
            if b == c:
                if (a,d) not in R_prime:
                    R_prime.add((a,d))

    return R_prime


'''
Input: a positive integer n; a relation R on Xn
Output: the connected components of (Xn, R ∪ R^(−1)).
'''

def main():

    n = 4
    R = {(0, 1), (1, 2), (2, 0), (3,2)}
    print(f"R: {R}\n")

    # Reflexive test
    R_prime = reflexive_closure(n, R)
    # R + {(0,0), (1,1), (2,2), (3,3)}
    print(f"Reflexive closure of R: {R_prime}\n")

    # Symmetric test
    R_prime = symmetric_closure(n, R)
    # R + {(1,0), (2,1), (0,2), (2,3)}
    print(f"Symmetric closure of R: {R_prime}\n")

    # Transitive test
    R_prime = transitive_closure(n, R)
    # R + {(0,2), (3,0), (1,0), (2,1)}
    print(f"Transitive closure of R: {R_prime}\n")

if __name__ == "__main__":
    main()


