import re
import json
from pathlib import Path
from mcr import *

# ll1 stuff
# TODO : Still need to learn more about parse table in general
p = Path(__file__).parent / "ll1.json"
with open(p) as f:
    ll1 = json.load(f)

terminals = set()
for x,y in ll1.items():
    terminals.update(y.keys())
terminals.add('EOF')

lex = {
    'NUMERIC' : r'(?:\d+\.\d*|\d+|\.\d+)',
    'TRIGONOMETRIC' : r'\b(?:sin|cos|tan)\b',
    'SYMBOLIC' : r'[A-Za-z]\w*',
    'OPERATOR' : r'[\+\-\*/\^!\(\),]',
    'SKIP' : r'[ \t]+'
}

master = re.compile('|'.join(f"(?P<{group}>{pattern})" for group, pattern in lex.items()))

# lexing stuff
class Token:
    def __init__(self, kind, text, pos):
        self.kind = kind
        self.text = text
        self.pos = pos 
    
    def __repr__(self):
        return f"{self.kind} Token '{self.text}' @ {self.pos}"

def tokenize(src):
    tokens = []
    for m in master.finditer(src):
        kind = m.lastgroup
        text = m.group(kind)
        pos = m.start()
        if kind == 'SKIP':
            continue 
        if kind == 'OPERATOR':
            kind = text
        tokens.append(Token(kind, text, pos))
    tokens.append(Token('EOF', '', len(src)))
    return tokens

# ast stuff
def astadd(stack,text):
    right = stack.pop()
    left = stack.pop()
    stack.append(Summation(left,right))

def astsub(stack,text):
    right = stack.pop()
    left = stack.pop()
    stack.append(Summation(left,Negative(right)))

def astmul(stack,text):
    right = stack.pop()
    left = stack.pop()
    stack.append(Multiplication(left,right))

def astdiv(stack,text):
    
    right = stack.pop()
    left = stack.pop()
    stack.append(Division(left,right))

def astexp(stack,text):
    
    right = stack.pop()
    left = stack.pop()
    stack.append(Exponentiate(left,right))

def astneg(stack,text):
    stack.append(Negative(stack.pop()))

def astfac(stack,text):
    stack.append( Factorial(stack.pop()))

def astsin(stack,text):
    stack.append( Sinusoid(stack.pop()))

def astnum(stack,text):
    if float(text) == int(text):
        stack.append(Numeric(int(text)))
    else:
        stack.append(Numeric(float(text)))

def astsym(stack,text):
    stack.append(Symbolic(text))

# TODO: Modularize, strange code writing ahead...
functions = { 
    "#B+" : astadd,
    "#B-" : astsub,
    "#B*" : astmul,
    "#B/" : astdiv,
    "#B^" : astexp,
    "#U!" : astfac,
    "#U-" : astneg,
    "#N" : astnum, 
    "#T" : astsin,
    "#S" : astsym
}


# simple LL1 parsing
class Parser:
    def __init__(self,src):
        self.tokens = tokenize(src)
        self.kinds = [token.kind for token in self.tokens]
        # add terminating EOF
        self.stack = ['EOF', 'E']
        self.pos = 0
        self.ast = []
    
    # TODO: fix parse table logic
    def parse(self): 
        while self.stack: 
            next = self.stack.pop()
            lookahead = self.kinds[self.pos]
            # ast stuff
            if next.startswith("#"): 
                # handle node construction
                text = None
                if next in ("#N", "#S", "#T"):
                    text = self.tokens[self.pos-1].text
                functions[next](self.ast,text)
                continue
            # handle terminal 
            if next in terminals:
                if next != lookahead: 
                    # debugging; turn off
                    raise SyntaxError(f"EXPECTED {next} GOT {lookahead}!!!")
                self.pos +=1
                continue
            # nonterminal
            production = ll1[next].get(lookahead)
            if production is None:
                # debugging; turn off
                raise SyntaxError(f"NO RULE FOR {next} FOR {lookahead}")
            for symbol in reversed(production):
                self.stack.append(symbol)
        print(self.ast)
        return self.ast[0]
