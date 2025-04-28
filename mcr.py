from math import comb, log, exp, sin

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
    
    def crmake(self,x0, h):
        return self.subexp.crmake(x0,h)

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

    def crmake(self, x0,h):
        return BR(x0,'+',h)
    
    def label(self):
        return f'{self.__class__.__name__}({self.name})'
    

class Numeric(Atomic):
    def __init__(self,value):
        super().__init__()
        self.value = value
    
    def evaluate(self):
        return self.value

    def crmake(self, x0, h):
        return self.value
    
    def label(self):
        return f'{self.__class__.__name__}({self.value})'
    
    def __repr__(self):
        return f"Num({self.value})"
    

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


# PROTOTYPING BR CLASS
class BR:
    def __init__(self, basis, operator, function):
        self.basis, self.operator, self.simple = basis, operator, False
        self.puresum = operator == '+'
        self.pureprod = operator == '*'
        # 1 denotes BR. > 1 denotes CR. Operations linked.
        self.depth = 1
        # initialize cache
        # TODO: necessary? is it faster? maybe can consolidate 1 loop
        self.cache = {}

        # check if BR first before interrogating
        if isinstance(function,BR):
            self.puresum = self.puresum and function.puresum
            self.pureprod = self.pureprod and function.pureprod
            # BR is only simple if child is simple
            self.simple = function.simple
            self.function = function
            self.depth += function.depth
        else:
            # Constant function case: wrap and set to simple.
            if not callable(function):
                self.simple = True
            self.function = function
            
            self.tail = function # save the function regardless

        # TODO: is it faster to perform recursive call? More cached calls to retrieve?

    def __call__(self, i):
        if not isinstance(i, int) or i < 0:
            raise ValueError('INVALID INDEX')
        
        # check cache first
        if i in self.cache:
            return self.cache[i]

        if i == 0:
            val = self.basis
        else:
            # recursive step
            prev = self.__call__(i - 1)
            if callable(self.function):
                term = self.function(i - 1)
            else:
                term = self.function
            if self.operator == '+':
                val = prev + term
            elif self.operator == '*':
                val = prev * term
            else:
                raise ValueError(f'INVALID OPERATOR {self.operator}')
        
        # store and return
        self.cache[i] = val
        return val

    def coefficients(self):
        if not (self.puresum or self.pureprod):
            # debugging
            raise ValueError('NOT PURESUM OR PUREPROD!!!!!')

        # compute coefficients once.
        if 'COEFFICIENTS' in self.cache:
            return self.cache['COEFFICIENTS']
        
        coefficient = [self.basis]
        if isinstance(self.function, BR):
            coefficient.extend(self.function.coefficients())
        else: 
            coefficient.append(self.function)
        self.cache['COEFFICIENTS'] = coefficient
        return coefficient
        
    def crsum(self,target):
        if not (self.puresum and target.puresum):
            raise ValueError('NOT PURESUM!!')
        
        c1 = self.coefficients()
        c2 = target.coefficients()
        res = []
        for i in range(min(len(c1),len(c2))):
            res.append(c1[i] + c2[i])
        for i in range(len(c1),len(c2)):
            res.append(c2[i])
        for i in range(len(c2),len(c1)):
            res.apend(c1[i])
        
        return self.coeffRestore(res, '+')


    def crpureprod(self,target):
        if not (self.pureprod and target.pureprod):
            raise ValueError('NOT PUREPROD!!')
        c1 = self.coefficients()
        c2 = target.coefficients()
        res = []
        for i in range(min(len(c1),len(c2))):
            res.append(c1[i] * c2[i])
        for i in range(len(c1),len(c2)):
            res.append(c2[i])
        for i in range(len(c2),len(c1)):
            res.append(c1[i])

        return self.coeffRestore(res,'*')
    
    # optimize crprod
    def crprod(self,target):
        c1 = self.coefficients()
        c2 = target.coefficients()
        res = self.crprodaux(c1,c2)
        return self.coeffRestore(res,'+')
    
    def crprodaux(self, c1,c2):
        if len(c1) < len(c2):
            c2,c1 = c1,c2
        
        if len(c2) == 1:
            return [c2[0] * c for c in c1]
        
        f1 = c1[1:]
        g1 = c2[1:]

        g2 = [g1[i] + c2[i] for i in range(len(g1))]
        g2.append(c2[-1])
        
        r1 = self.crprodaux(c1,g1)
        r2 = self.crprodaux(f1,g2)

        res = [c1[0] * c2[0]]
        for i in range(len(r1)):
            res.append(r1[i] + r2[i])
        return res
    
    # TODO: convolutional alternative to crexpt
    # switch to logarithmic form to perform crprod
    def crexpt(self,target):
        c1 = self.coefficients()
        c2 = target.coefficients()
        res = self.crexptaux(c1,c2)
        return self.coeffRestore(res,'+')
    
    def crexptaux(self, c1,c2):
        if len(c1) < len(c2):
            c2,c1 = c1,c2
        if len(c2) == 1:
            return [c2[0] ** c for c in c1]
        f1 = c1[1:]
        g1 = c2[1:]
        g2 = [g1[i] ** c2[i] for i in range(len(g1))]
        g2.append(c2[-1])
        r1 = self.crexptaux(c1,g1)
        r2 = self.crexptaux(f1,g2)
        res = [c1[0] * c2[0]]
        for i in range(len(r1)):
            res.append(r1[i] * r2[i])
        return res

    # TODO : rebuild process costly? 
    # Leaning towards not necessarily
    def coeffRestore(self,coefficients,op):
        curr = coefficients[-1]
        for i in range(1,len(coefficients)):
            curr = BR(coefficients[-i-1],op,curr )
        return curr


    def dump(self, indent=0):
        print("  " * indent + f"BR(basis={self.basis!r}, op={self.operator!r})")
        if isinstance(self.function, BR):
            # CORRECT: call dump on the *child* instance,
            # passing only the new indent
            self.function.dump(indent + 1)
        else:
            # leaf: show the constant
            leaf = self.function
            print("  " * (indent + 1) + f"→ leaf value = {leaf!r}")
    
    def __add__(self, target):
        if self.operator == '*':
            return CRsummation(self,target)
        
        # S3 proposition 1
        if isinstance(target,(int,float)):
            self.basis += target
            return self
        # S3 proposition 2
        elif self.puresum and target.puresum:
            return self.crsum(target)
        # S4.1
        elif isinstance(target, BR): 
            if target.operator == '+':
                self.basis += target.basis
                self.function += target.function
                return self
            else: 
                return CRsummation(self.function,target.function)
        else:
            raise NotImplemented

    def __radd__(self,target): 
        return self + target

    def __mul__(self, target):
        # constant case
        if isinstance(target, (int,float)):
            if self.operator == '+':
                self.basis *= target
                self.function *= target
                return self
            else:
                self.basis *= target
                return self
        elif isinstance(target, BR):
            if self.puresum and target.puresum:
                return self.crprod(target)
            elif self.purprod and target.pureprod:
                return self.crpureprod(target)
            elif self.operator == target.operator:              
                if self.operator == '*':
                    self.basis *= target.basis
                    self.function *= target.function
                    return self
                elif self.operator == '+':
                    self.basis *= target.basis
                    self.function = self * target.function + target * self.function + self.function * target.function
                    return self
            else:
                return CRmultiplication(self, target)
               

    def __rmul__(self, target):
        return self * target

    def __pow__(self, target):
        pass

    # not implemented
    def __rpow__(self,target):
        pass


