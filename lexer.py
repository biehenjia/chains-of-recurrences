import re
lex = {
    # digits and decimals
    'NUMERIC': r'\d+(?:\.\d*)?',
    'SYMBOLIC' : r'[A-Za-z]\w*',
    'OPERATOR' : r'[\+\-\*/\^!\(\),]',
    'SKIP' : r'[ \t]+'
}

master = re.compile('|'.join(f"(?P<{group}>{pattern})" for group, pattern in lex.items()))

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