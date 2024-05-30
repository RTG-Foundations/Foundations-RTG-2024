import sys
import numpy as np
import time

'''
    Create a relation to represent the 0-1 matrix
'''
def getRelation(n, M):
    R = set()
    for i in range(0,n):
        for j in range(0,n):
            if M[i][j] != 0:
                R.add((i,j))
    return R

'''
    Get transitive closure using Floyd Warshall's algorithm
'''
def floyd_transitive_closure(n, M):
    for k in range(n):
        for i in range(n):
            for j in range(n):
                M[i][j] = M[i][j] or (M[i][k] and M[k][j])
    return M

'''
    Get transitive closure as M U M^2 U M^4 U ...
'''
def transitive_closure(n, M):
    a = 1
    while a < n:
        a *= 2
        M += np.dot(M, M)
    return M

'''
    Generate random nxn binary matrix
'''
def generate_random_binary_matrix(n):
    return np.random.choice([0, 1], size=(n, n))



def main():
   
    # get n
    if len(sys.argv) != 2:
        print("Usage: python script.py <n>")
        return
    n = int(sys.argv[1])
    
    # random binary matrix
    M = generate_random_binary_matrix(n)
    
    # Floyd Warshall
    M_floyd = M.copy()
    
    start_floyd = time.time()
    M_prime_floyd = floyd_transitive_closure(n, M_floyd)
    end_floyd = time.time()
    
    time_floyd = (end_floyd - start_floyd) * 1e9
    R_Floyd = getRelation(n, M_prime_floyd)
    
    # Trans. Closure time
    M_trans = M.copy()
    
    start_trans = time.time()
    M_prime_trans = transitive_closure(n, M_trans)
    end_trans = time.time()
    
    time_trans = (end_trans - start_trans) * 1e9
    R_Trans = getRelation(n, M_prime_trans)
    
    # check relations are equal
    if R_Floyd != R_Trans:
        raise ValueError("Transitive closures are not equal!")
   
    # write results to outputRace.txt
    with open("outputRace.txt", "a") as f:
        f.write(f"N = {n}\n")
        f.write(f"\tFloyd-Warshall Time (ns): {time_floyd}\n")
        f.write(f"\tTrans. Closure Time (ns): {time_trans}\n")
    
    print(f"N = {n}. Floyd-Warshall Time (ns): {time_floyd}\n")
    print(f"N = {n}. Trans. Closure Time (ns): {time_trans}\n")

if __name__ == "__main__":
    main()
