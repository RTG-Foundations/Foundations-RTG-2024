'''
Let A = {(,), ⊥, →, ♢, p0, p1, . . .} be a set. By A∗ we denote the set of finite
sequences of elements of A.

This program decides if s ∈ A∗ is a modal formula, using the following syntax for
modal formulas:

<expr> = <term> --> <expr>
	| <term>

<term> = '('<expr>')'
	| ♢<expr>
	| <var>
	
<var> =  ⊥ | p0 | p2 
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
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def parse(self):
        try:
            self.expr()
            return self.match('END_OF_INPUT')
        except ValueError as e:
            print(e)
            return False

    '''
        <expr> = <term> --> <expr> | <term>
    '''
    def expr(self):
        self.term()
        while self.match('T_IMPLICATION'):
            self.term()

    '''
        <term> = '('<expr>')' | ♢<expr> | <var>
    '''
    def term(self):
        if self.match('T_LEFTPAREN'):
            self.expr()
            self.expect('T_RIGHTPAREN')
        elif self.match('T_BOX'):
            self.expr()
        else:
            self.var()

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

def is_valid_expression(input_str):
    input_str = input_str.replace(' ', '')  # Remove all spaces
    tokens = Tokenizer(input_str).tokenize()
    parser = Parser(tokens)
    return parser.parse()

# Examples
expression = 'p0 --> p2'
print(f"{expression} : {is_valid_expression(expression)}")  
expression = '♢(⊥ --> ⊥)'
print(f"{expression} : {is_valid_expression(expression)}")  
expression = '♢(p0) --> ♢p2'
print(f"{expression} : {is_valid_expression(expression)}")   
expression = 'p0 p2'
print(f"{expression} : {is_valid_expression(expression)}") 
expression = '♢♢♢((p0))'
print(f"{expression} : {is_valid_expression(expression)}")  
expression = 'p0 --> ♢♢p2 --> ⊥'
print(f"{expression} : {is_valid_expression(expression)}") 
