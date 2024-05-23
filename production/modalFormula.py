'''
Let A = {(,), ⊥, →, ♢, p0, p1, . . .} be a set.
By A∗ we denote the set of finite sequences of elements of A.

This program decides if s ∈ A∗ is a modal formula, using 
the following syntax for modal formulas:

<expr> = <term> --> <expr>
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

# Token types
TOKEN_TYPE_MAP = {
    'T_PROPOSITION': r"p\d+",
    'T_FALSITY': '⊥',
    'T_BOX': '♢',
    'T_LEFTPAREN': r'\(',
    'T_RIGHTPAREN': r'\)',
    'T_IMPLICATION': r'-->',
}

class Token:
    def __init__(self, token_type, value=None, position=None):
        self.type = token_type
        self.value = value
        self.position = position

class Tokenizer:
    def __init__(self, input_str):
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
        raise ValueError("Invalid token at position {}".format(self.index))

class Parser:
    num_paren = 0
    num_implic = 0

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.subformulas = []
        self.numImplic = 0
        self.numParen = 0

    def parse(self):
        try:
            self.expr()
            if self.match('END_OF_INPUT'):
                return self.subformulas
            else:
                return None
        except ValueError as e:
            print(e)
            return None

    '''
        <expr> = <term> --> <expr> | <term>
                        
    '''
    def expr(self):
       
            start = self.index
            self.term()
            if self.match('T_IMPLICATION'):
                self.term()
            end = self.index
            self.add_subformula(start, end)

     

    '''
        <term> = '('<expr>')' | '♢('<expr>')' | <var>
    '''
    def term(self):
        start = self.index
        if self.match('T_LEFTPAREN'):
            self.expr()
            self.expect('T_RIGHTPAREN')
        elif self.match('T_BOX'):
            self.expect('T_LEFTPAREN')
            self.expr()
            self.expect('T_RIGHTPAREN')
        else:
            self.var()
        end = self.index
        self.add_subformula(start, end)



    '''
        <var>  =  ⊥ | p0 | p1 | ... 
    '''
    def var(self):
        token = self.tokens[self.index]
        if token.type not in ['T_FALSITY', 'T_PROPOSITION']:
            raise ValueError("Expected variable at position {}".format(token.position))
        self.index += 1

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
        if subformula_str not in self.subformulas:
            self.subformulas.append(subformula_str)

def find_subformulas(input_str):
    input_str = input_str.replace(' ', '')  # Remove all spaces
    tokens = Tokenizer(input_str).tokenize()
    parser = Parser(tokens)
    subformulas = parser.parse()
    return subformulas if subformulas else False


# Examples
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
