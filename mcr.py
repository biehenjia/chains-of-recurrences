from math import sin
from br import BR

# TODO: Canonical forms, expression initialization, parsing
# TODO: fix repr

# AST stuff
class Expression:
    def __init__(self, subexp = None, environment = None):
        self.environment = {} if environment is None else environment
        self.subexp = subexp

    # Evaluate subexpression
    def evaluate(self):
        if self.subexp is None:
            return 0
        return self.subexp.evaluate()

    # TODO: implement simplification algorithm 
    # Can assume that given expression is simplified.
    # CRMAKE implicitly simplifies?
    def simplify(self): 
        if self.subexp is None:
            return
        self.simplify(self.subexp)

    # remap environment variables to different configuration
    def remap(self, remapping):
        for k,v in remapping.items():
            self.environment[k] = v
        self.subexp.remap(remapping)

    def contextualize(self,mapping):
        self.environment = mapping
        if self.subexp is None:
            return
        # mutable environment assignment
        self.subexp.contextualize(mapping)

    def __repr__(self):
        return f"Exp({repr(self.subexp)})"
    
    # WIP: Add tree representation
    # WIP: Fix inheritence logic, some bloat here
    def hierarchize(self, prefix = '', terminal = True):
        sublabel = ""
        if self.subexp is not None:
            sublabel += '\n' +self.subexp.hierarchize(prefix + ("    " if terminal else "│   "),True)
        return f"{prefix + ('└── ' if terminal else '├── ')}{self.label()}{sublabel}"
    
    def label(self):
        return self.__class__.__name__
    

    def CRMAKE(self, x0, h):
        return BR(self.subexp,x0, h)

# Atomic subexpressions have no child subexpresisons 
class Atomic(Expression):
    def __init__(self):
        super().__init__()


class Symbolic(Atomic): 
    def __init__(self,name):
        super().__init__()
        self.name = name
    

    def evaluate(self):
        if not self.name in self.environment:
            print(f'{self.name} undefined')
        return self.environment.get(self.name,0)

    
    def label(self):
        return f'{self.__class__.__name__}({self.name})'
    
    

class Numeric(Atomic):
    def __init__(self,value):
        super().__init__()
        self.value = value
    
    def evaluate(self):
        return self.value

    def label(self):
        return f'{self.__class__.__name__}({self.value})'
    
    def __repr__(self):
        return f"Num({self.value})"
    

    def CRMAKE(self, x0, h):
        return BR(x0,'+',0)

class Operator(Expression):
    def __init__(self, subexp):
        super().__init__(subexp= subexp)
    
class Unary(Operator):
    def __init__(self, subexp):
        super().__init__(subexp = subexp)
    
class Factorial(Unary):
    pass 

class Negative(Unary):
    def evaluate(self):
        return -1 * self.subexp.evaluate()
    
    def label(self):
        return "Neg"
    
class Sinusoid(Unary):
    def evaluate(self):
        return sin(self.subexp.evaluate())
    
    def label(self):
        return "Sin"

class Binary(Operator):
    def __init__(self, leftexp, rightexp):
        super().__init__(None)
        self.leftexp = leftexp
        self.rightexp = rightexp
    
    def contextualize(self, mapping):
        # should not happen 
        if not self.leftexp and not self.rightexp:
            return
        
        # contextualize left and right subexpressions
        self.leftexp.contextualize(mapping)
        self.rightexp.contextualize(mapping)
    
    def remap(self, remapping):
        for k,v in remapping.items():
            self.environment[k] = v
        self.rightexp.remap(remapping)
        self.leftexp.remap(remapping)
    
    def hierarchize(self, prefix='', terminal=True):
        label = prefix + ("└── " if terminal else "├── ") + self.label()
        prefix += ("    " if terminal else "│   ")
        # right label will always be terminal
        leftlabel = self.leftexp.hierarchize(prefix, False)
        rightlabel = self.rightexp.hierarchize(prefix, True)
        return f'{label}\n{leftlabel}\n{rightlabel}'

    def label():
        return 'Bin'
    
class Summation(Binary):
    def evaluate(self): 
        return  self.rightexp.evaluate() + self.leftexp.evaluate()
    
    def label(self):
        return 'Add'



class Multiplication(Binary):
    def evaluate(self):
        return self.rightexp.evaluate() * self.leftexp.evaluate()
    
    def label(self):
        return 'Mul'

class Exponentiate(Binary):
    def evaluate(self):
        return self.leftexp.evaluate() ** self.rightexp.evaluate()
    
    def label(self):
        return 'Pow'
    
class Division(Binary):
    def evaluate(self):
        return self.leftexp.evaluate() / self.rightexp.evaluate()

    def label(self):
        return 'Div'


# TODO: FIX
def CRMAKE(expr, x0, h):
    if expr.__class__ is Expression:
        return CRMAKE(expr.subexp, x0, h)
    if isinstance(expr, Numeric):
        return BR(x0, '+', 0)
    if isinstance(expr, Symbolic):
        return BR(x0, '+', h)

    if isinstance(expr, Exponentiate):
       
        if isinstance(expr.rightexp, Numeric):
           
            n_val = expr.rightexp.value
            if not (n_val >= 0 and float(n_val).is_integer()):
                raise ValueError("")
            n = int(n_val)

            # build base once
            base_cr = CRMAKE(expr.leftexp, x0, h)
            if n == 0:
                return BR(x0, '+', 0)
            result = base_cr
            for _ in range(n - 1):
                if not (result.puresum and base_cr.puresum):
                    raise ValueError("")
                result = result.crprod(base_cr)
            return result

        left = CRMAKE(expr.leftexp, x0, h)
        right = CRMAKE(expr.rightexp, x0, h)

        if left.pureprod and right.puresum:
            return left.crexpt(right)

        raise NotImplementedError

    if isinstance(expr, Summation):
        left = CRMAKE(expr.leftexp, x0, h)
        right = CRMAKE(expr.rightexp, x0, h)
        return left.crsum(right)

    if isinstance(expr, Multiplication):
        left = CRMAKE(expr.leftexp, x0, h)
        right = CRMAKE(expr.rightexp, x0, h)
        if left.puresum and right.puresum:
            return left.crprod(right)
        if left.pureprod and right.pureprod:
            return left.crexpt(right)
        raise NotImplementedError

            









    
