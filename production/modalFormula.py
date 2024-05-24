'''
Let A = {(,), ⊥, →, ♢, p0, p1, . . .} be a set.
By A∗ we denote the set of finite sequences of elements of A.

This program decides if s ∈ A∗ is a modal formula, using 
the following syntax for modal formulas:

<expr> = <term> --> <term>
	    | <term>

<term> = '('<expr>')'
	| '♢''('<expr>')'
	| <var>
	
<var> =  ⊥ | p0 | p2 

* This grammer uses right-associativity, so p0 --> p1 --> p2 is parsed p0 --> (p1 --> p2)

If the formula is valid,  returns an ordered set (ψ1, . . . , ψk) 
of all subformulas of s such that if ψi is a subformula
of ψj , then i < j.



'''

import re
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

class ASTNode:
    def __init__(self, node_type, value=None):
        self.type = node_type
        self.value = value
        self.s1 = None
        self.s2 = None

class Token:
    def __init__(self, token_type, value=None, position=None):
        self.type = token_type
        self.value = value
        self.position = position

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

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        
    def parse(self):
        self.subformulas = []

        try:
            ast = self.expr()
            if self.match('END_OF_INPUT'):
                return ast, self.subformulas
            else:
                return None
        except ValueError as e:
            print(e)
            return None

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
            root = ASTNode(A_PROPOSITION, token.value)
        else:
            raise ValueError("Expected variable at position {}".format(token.position))
            
        self.index += 1
        return root

    def match(self, token_type):
        if self.tokens[self.index].type == token_type:
            self.index += 1
            return True
        return False

    def expect(self, token_type):
        if not self.match(token_type):
            raise ValueError("Expected {} at position {}".format(token_type, self.tokens[self.index].position))

    def add_subformula(self, start_index, end_index):
        subformula_tokens = self.tokens[start_index:end_index]
        subformula_str = ''.join(token.value for token in subformula_tokens if token.value)
        subformula_str = subformula_str.replace('(', '')  # Remove parenthesis
        subformula_str = subformula_str.replace(')', '')  
        if subformula_str not in self.subformulas:
            self.subformulas.append(subformula_str)




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
        #subformula_result = evaluate_formula_ast(node.s1, x, R, V)
        expr = node.s1
        neighbors = R[x]
        for neighbor in neighbors:
            if evaluate_formula_ast(expr, neighbor, R, V):
                return(True)
        return(False)
    else:
        raise ValueError("Unknown formula type")


def find_subformulas(input_str):
   
    tokens = Tokenizer(input_str).tokenize()
    parser = Parser(tokens)
    try:
        ast, subformulas = parser.parse()
    except:
        return False
   
    return subformulas if subformulas else False


def get_satisfying_points_ast(phi, n, R, V):
    tokens = Tokenizer(phi).tokenize()
    parser = Parser(tokens)
    try:
        ast, subformulas = parser.parse()
    except:
        return(False)

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


def main():

    # Exercise 2.10
    n = 5
    R = {(4,5),(1,4),(3,4),(2,3)} 
    V = {'p1': {1, 3, 5}, 'p2':{2, 4}}

    phi = '(p1 --> p2)'
    print(f"phi = {phi}\n"
        f"Xn= {', '.join(str(num) for num in range(n))}\n" 
        f"V={V}\n" 
        f"Satisfying points: {get_satisfying_points_ast(phi, n, R, V)}\n")  

    phi = '♢(p1 --> p2)'
    print(f"phi = {phi}\n"
        f"Xn= {', '.join(str(num) for num in range(n))}\n" 
        f"V={V}\n" 
        f"Satisfying points: {get_satisfying_points_ast(phi, n, R, V)}\n")  

    phi = '♢(⊥ --> p2)'
    print(f"phi = {phi}\n"
        f"Xn= {', '.join(str(num) for num in range(n))}\n" 
        f"V={V}\n" 
        f"Satisfying points: {get_satisfying_points_ast(phi, n, R, V)}\n")  


    # Exercise 2.9 b
   

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
   



if __name__ == "__main__":
    main()
