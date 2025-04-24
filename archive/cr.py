# chains of recurrences stuff
class BR():

    def __init__(self, base, operator, fxn, name = None):
        self.name = name 
        self.operator = operator 
        self.base = base 
        self.name = name
        
        if isinstance(fxn, BR):
            self.depth = fxn.depth + 1
        else:
            self.depth = 1

        self.cache = {}

        if callable(fxn):
            self.fxn = fxn
        else:
            self.fxn = lambda _ : fxn
        
    def __call__(self, i):
        if i == 0:
            return self.base

        if i in self.cache:
            return self.cache[i]

        left = self.__call__(i-1)
        right = self.fxn(i-1)
        if self.operator == '+':
            res = left + right
        else:
            res = left * right
        
        self.cache[i] = res 
        return res 
    
    def __repr__(self):
        if isinstance(self.fxn, BR):
            clause = repr(self.fxn)
        else:
            clause = self.name
        return f"BR({self.base}, {self.operator}, {clause})"
    
    # Algebraic Properties of CR's
    # ADAPTED FROM PAPER 1984
    # DEPRECATED AS OF PAPER 1994

    def __add__(self,target):
        if isinstance(target, (int,float)):
            return BR(self.base + target, '+', self.fxn)
        
        else:
            return BR(self.base + target.base, '+', lambda i: self.function(i) + target)
    
    def __radd__(self,target):
        return self + target

    def __mul__(self,target):
        if isinstance(target, (int,float)):
            return BR(self.base * target, self.operator, lambda i: self.fxn(i) * (target if self.operator == '+' else 1))
        
        aux = lambda i : (self(i) * target.fxn(i) + target(i) * self .fxn(i)) if self.operator == '*' else 0
        return BR(self.base * target.base, self.operator, lambda i : self.fxn(i) * target.fxn(i) + aux(i))

    def __rmul__(self,target):
        return self * target 

    # CHECK CASE FOR POTENTIAL CRPROD or CREXPT
    

    
class CR():
    def __init__(self, *chains):
        self.cache = {}
        fxn = chains[-1]
        self.chains = [fxn]

        for i in range(len(chains)//2):
            operator = chains[-2*i-2]
            base = chains[-2*i-3]
            fxn = BR(base,operator, fxn)
            self.chains.append(fxn)
        
        self.function = fxn 
