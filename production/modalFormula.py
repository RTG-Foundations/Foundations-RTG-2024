'''
Let A = {(,), ⊥, →, ♢, p0, p1, . . .} be a set.
By A∗ we denote the set of finite sequences of elements of A.

Implements a parser to check if s ∈ A∗ is a  valid modal formula, using 
the following syntax for modal formulas:

<expr> = <term> --> <term>
	    | <term>

<term> = '('<expr>')'
	| '♢''('<expr>')'
	| <var>
	
<var> =  ⊥ | p0 | p1 | p2 | ...

During parsing, stores the formula s as an abstract syntax tree, which can be evaluated to 
1)  Return an ordered set (ψ1, . . . , ψk) of all subformulas of s such that if 
    ψi is a subformula of ψj , then i < j.
2)  Given a positive integer n, a relation R on Xn and subsets V1 , . . . Vm of Xn, 
    return the set of points x in Xn such that M, x ⊨ s, where the valuation of pi in M is Vi
3)  Given a positive integer n and a relation R on X n, return whether s is valid in (X n , R)?

'''
import re # for matching regular expressions
from itertools import product


# Token types
TOKEN_TYPE_MAP = {
    'T_PROPOSITION': r"p\d+",
    'T_FALSITY': '⊥',
    'T_DIAMOND': '♢',
    'T_LEFTPAREN': r'\(',
    'T_RIGHTPAREN': r'\)',
    'T_IMPLICATION': r'-->',
}


# Abstract Syntax Tree Node Types
A_PROPOSITION = 'PROPOSITION'
A_FALSITY = 'FALSITY'
A_IMPLICATION = 'IMPLICATION'
A_DIAMOND = 'DIAMOND'


'''
    Defines an ASTNode

    Input:
        self: parser creating this node
        node_type: valid node types are A_PROPOSITION, A_FALSITY,
        A_IMPLICATION, A_DIAMOND 
        value: name of the propositional variable,if applicable
        
    Output: Creates a ASTNode object


'''
class ASTNode:
    def __init__(self, node_type, value=None):
        self.type = node_type
        self.value = value
        # children
        self.s1 = None
        self.s2 = None


'''
    Defines a token 
    
    Input:
        token_type:  valid  token types are T_PROPOSITION, T_FALSITY, T_DIAMOND, T_LEFTPAREN,
        T_RIGHTPAREN, T_IMPLICATION
        value:  name of the propositional variable,  if applicable. Valid names are of form p0, p1, ...
        position: location of token

    Output: Creates a token object

'''
class Token:
    def __init__(self, token_type, value=None, position=None):
        self.type = token_type
        self.value = value
        self.position = position

'''
    Class to split the input string into tokens

'''
class Tokenizer:
    def __init__(self, input_str):
        input_str = input_str.replace(' ', '')  # Remove all spaces
        self.input = input_str
        self.index = 0

    def tokenize(self):
        tokens = []
        while self.index < len(self.input):
            token = self.next_token()
            if token:
                tokens.append(token)
        tokens.append(Token('END_OF_INPUT'))  
        return tokens

    def next_token(self):
        for token_type, pattern in TOKEN_TYPE_MAP.items():
            match = re.match(pattern, self.input[self.index:])
            if match:
                value = match.group()
                token = Token(token_type, value, self.index)
                self.index += len(value)
                return token
        raise ValueError(f"Invalid token {self.input[self.index]} at position {self.index}")


'''
    Checks if the token sequence is a valid modal formula and constructs an AST.
    
    Valid modal formulas are defined using the BNF grammer:
    <expr> = <term> --> <term>
	    | <term>

    <term> = '('<expr>')'
        | '♢''('<expr>')'
        | <var>
        
    <var> =  ⊥ | p0 | p2 


    Input:
        a valid modal formula
    
    Output:
        I. the AST representation of the formula
        II. an ordered set (ψ 1 , . . . , ψ k ) of all subformulas of s such that 
        if ψi is a subformula of ψj , then i < j.
        III. a list of all propostions in the subformula

'''
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        
    def parse(self):
        self.subformulas = []
        self.propositions = set()


        ast = self.expr() # 
        if self.match('END_OF_INPUT'):
            return ast, self.subformulas, self.propositions
        else:
            raise ValueError("Not a modal valid formula")
      

    '''
        <expr> = <term> --> <term> | <term>                 
    '''
    def expr(self):
            
            start = self.index
            s1 = self.term()
            if self.match('T_IMPLICATION'): # implication
                s2 = self.term()
                
                root = ASTNode(A_IMPLICATION)
                root.s1 = s1
                root.s2 = s2
            else: # not implication. Return s1
                root = s1
            
            end = self.index
            self.add_subformula(start, end)

            return root

     

    '''
        <term> = '('<expr>')' | '♢('<expr>')' | <var>
    '''
    def term(self):
        start = self.index

        if self.match('T_LEFTPAREN'):
            root = self.expr()
            self.expect('T_RIGHTPAREN')
        elif self.match('T_DIAMOND'):
            root = ASTNode(A_DIAMOND)
            self.expect('T_LEFTPAREN')
            root.s1 = self.expr()
            self.expect('T_RIGHTPAREN')
        else:
            root = self.var()
        end = self.index
        self.add_subformula(start, end)

        return root



    '''
        <var>  =  ⊥ | p0 | p1 | ... 
    '''
    def var(self):
        token = self.tokens[self.index]
        if token.type == 'T_FALSITY':
            root = ASTNode(A_FALSITY)
        elif token.type == 'T_PROPOSITION':
            self.propositions.add(token.value)
            root = ASTNode(A_PROPOSITION, token.value)
        else:
            raise ValueError("Expected variable at position {}".format(token.position))
            
        self.index += 1
        return root

    '''
        If the input matches token_type, go to the next token and return True. 
        Otherwise, return false
    '''
    def match(self, token_type):
        if self.tokens[self.index].type == token_type:
            self.index += 1
            return True
        return False

    '''
        If the input matches token_type, go to the next token
        Otherwise, throw an error
    '''
    def expect(self, token_type):
        if not self.match(token_type):
            raise ValueError("Expected {} at position {}".format(token_type, self.tokens[self.index].position))

    '''
        Adds formula between start_index and end_index to the list of subformulas
    '''
    def add_subformula(self, start_index, end_index):
        subformula_tokens = self.tokens[start_index:end_index]
        subformula_str = ''.join(token.value for token in subformula_tokens if token.value)
        if subformula_str not in self.subformulas:
            self.subformulas.append(subformula_str)



'''
    Recursively evaluates the AST at a given world x in the 
    model using the provided valuation V and relation R

    Preconditon:
        node: root of the AST tree
        x: world to check
        R:  dictionary of relations,  where each key is a node, and each
        value is an array of neighbors
        V:  dictionary of valuations,  where each key is a proposition, and each
        value is an array of nodes where the proposition is true
    
    Postcondition:
        evaluates whether the formula represented by the AST is true in world x

'''
def evaluate_formula_ast(node, x, R, V):
   
    #print(node.type)
    
    if node.type == A_PROPOSITION:
        prop = node.value
        return x in V[prop]
       
    elif node.type == A_FALSITY:
        return False
    elif node.type == A_IMPLICATION:
        s1 = evaluate_formula_ast(node.s1, x, R, V)
        s2 = evaluate_formula_ast(node.s2, x, R, V)

        # evaluate implication. True if Hypothesis false or conclusion true
        return (not s1) or s2
    
    elif node.type == A_DIAMOND:
        expr = node.s1
        neighbors = R[x]
        for neighbor in neighbors:
            if evaluate_formula_ast(expr, neighbor, R, V):
                return(True)
        return(False)
    else:
        raise ValueError("Unknown formula type")



'''
    Exercise 2.9 b
    Input: A modal formula s ∈ A ∗
    Output: the ordered set (ψ 1 , . . . , ψ k ) of all subformulas of s such that if 
    ψi is a subformula of ψj , then i < j.
'''
def find_subformulas(input_str):
    tokens = Tokenizer(input_str).tokenize()
    parser = Parser(tokens)
    
    ast, subformulas, propositions = parser.parse()
    return subformulas
    
   

'''
    Exercise 2.10
    Input: a modal formula φ in variables p 1 , . . . , p m ; a positive integer n; a relation
    R on Xn ; subsets V1 , . . . Vm of Xn ;
    Output: the set of points x in Xn such that M, x ⊨ φ, where the valuation of pi in
    M is Vi.

    Time complexity:
    O(n*t*d) where n is the number of worlds, t is the number of nodes of the AST corresponding to phi,
    and d is the maximum depth of the relation R


'''
def get_satisfying_points_ast(phi, n, R, V):
    tokens = Tokenizer(phi).tokenize()
    parser = Parser(tokens)
    
    ast, subformulas, propositions = parser.parse()
    

    # Write the R as dictionary,  
    # where each key is a node, and each 
    # value is an array of neighbors
    graph = {}
    for i in range(n):
        graph[i] = []
    for (a, b) in R:
        graph[a].append(b)  # R

    # find satisfying points
    satisfying_points = set()
    for x in range(n):
        if evaluate_formula_ast(ast, x, graph, V):
            satisfying_points.add(x)
    return satisfying_points


'''
    Exercise 2.11
    Input: a modal formula φ; a positive integer n; a relation R on Xn ;
    Output: is φ valid in (Xn , R)?

    Time complexity:
    O(2^(n*m)*n*d), where n is the number of worlds,  m is the number of 
    propositional variables in phi, and d is depth of the AST
'''

def is_formula_valid_in_model(phi, n, R):
    # parse formula
    tokens = Tokenizer(phi).tokenize()
    parser = Parser(tokens)
    
    ast, subformulas, propositions = parser.parse()
    

    # Write the R as dictionary,  
    # where each key is a node, and each 
    # value is an array of neighbors
    graph = {}
    for i in range(n):
        graph[i] = []
    for (a, b) in R:
        graph[a].append(b)  # R

    # generate list of all valuations
    #print(len(generate_all_valuations(propositions, n)))
    for V in generate_all_valuations(propositions, n):
        for x in range(n):
            if not(evaluate_formula_ast(ast, x, graph, V)):
                return False
    return True

'''
    Helper method for  is_formula_valid_in_model(phi, n, R)   

    Input: 
        variables: array of propostional variables of form p0, p1, ...
        n: positive integer such that Xn = {0,1, ..., n-1}

    Output:
        A set of all possible valuations. Every valuation is represented as a dictionary,
        where each key is a proposition, and each value is an array of 
        nodes where the proposition is true

'''
def generate_all_valuations(variables, n):
    valuations = []

    #  generates all combinations of True/False for len(variables) * n boolean values.
    for values in product([True, False], repeat=n * len(variables)):
        # Initialize valuation dictionary with empty sets for each variable
        valuation = {var: set() for var in variables}
        
        # for each proposition
        for i, var in enumerate(variables):
            # for each world (0 to n-1)
            for j in range(n):
                # Calculate the index in the `values` list for the (i, j) combination
                if values[i * n + j]:
                    # If the value at this index is True, add the point to the variable's set
                    valuation[var].add(j)
        
        # Append this valuation to the list of valuations
        valuations.append(valuation)

    return valuations




def main():
    '''
    # Exercise 2.9 b
    expression = '♢(♢(p1 -->  ⊥)) --> p2'
    print(f"{expression}\n{find_subformulas(expression)}\n")  

    expression = '♢(p4 --> (♢(p1)))'
    print(f"{expression}\n{find_subformulas(expression)}\n")  

    # bad example
    expression = '(♢())'
    print(f"{expression}\n{find_subformulas(expression)}\n")  

    expression = 'p0 --> p2 --> ♢(p3)'
    print(f"{expression}\n{find_subformulas(expression)}\n")  
    expression = '(p0 --> p2) --> p3'
    print(f"{expression}\n{find_subformulas(expression)}\n")  
    expression = 'p0 --> (p2 --> p3)'
    print(f"{expression}\n{find_subformulas(expression)}\n")  
    expression = '(p0 --> p2) --> (♢(p3) --> p4)'

    print(f"{expression}\n{find_subformulas(expression)}\n")  
    expression = '♢(⊥ --> ⊥)'
    print(f"{expression}\n{find_subformulas(expression)}\n") 
    expression = '♢(p0) --> ♢p2'
    print(f"{expression}\n{find_subformulas(expression)}\n")  
    expression = 'p0 p2'
    print(f"{expression}\n{find_subformulas(expression)}\n") 
    expression = '♢(♢(♢((p0))))'
    print(f"{expression}\n{find_subformulas(expression)}\n")  
    expression = 'p0 --> ♢(♢(p2)) --> ⊥' # p0 --> (♢♢p2 --> ⊥)
    print(f"{expression}\n{find_subformulas(expression)}\n") 
    expression = '(p0 --> ♢(♢(p2))) --> ⊥' 
    print(f"{expression}\n{find_subformulas(expression)}\n") 
    '''

        
    # Exercise 2.10
    n = 6
    R = {(4,5),(1,4),(1,5), (3,4),(2,3)} 
    V = {'p1': {1, 3, 5}, 'p2':{2, 4}}

    phi = '(p1 --> p2)'
    print(f"phi = {phi}\n"
        f"Xn= {', '.join(str(num) for num in range(n))}\n" 
        f"V={V}")
    print(f"Satisfying points: {get_satisfying_points_ast(phi, n, R, V)}\n")  

    phi = '♢(p1 --> p2)'
    print(f"phi = {phi}\n"
        f"Xn= {', '.join(str(num) for num in range(n))}\n" 
        f"V={V}")
    print(f"Satisfying points: {get_satisfying_points_ast(phi, n, R, V)}\n")  
    

    phi = '♢(⊥ --> p2)'
    print(f"phi = {phi}\n"
        f"Xn= {', '.join(str(num) for num in range(n))}\n" 
        f"V={V}") 
    print(f"Satisfying points: {get_satisfying_points_ast(phi, n, R, V)}\n")  


    # Exercise 2.11
    phi = '(p1 --> ♢(p2)) --> (p1 --> ♢p2)'
    n = 3
    R = {(0,0),(0,1),(1,2),(2,0),(0,2)} 

    print(f"phi = {phi}\n"
    f"Xn= {', '.join(str(num) for num in range(n))}\n" 
    f"R={R}") 
    print(f"Is valid: {is_formula_valid_in_model(phi, n, R)}\n")  


    phi = '((p1 --> ⊥) --> p1) --> p1'
    n = 3
    R = {(0,0),(0,1),(1,2),(2,0),(0,2)} 

    print(f"phi = {phi}\n"
    f"Xn= {', '.join(str(num) for num in range(n))}\n" 
    f"R={R}") 
    print(f"Is valid: {is_formula_valid_in_model(phi, n, R)}\n")  
    
  


if __name__ == "__main__":
    main()
