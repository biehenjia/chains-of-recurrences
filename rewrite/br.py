

class BR:

    def __init__(self, basis = None, operator=None, function= None):
        self.basis,self.operator, self.simple = basis, operator, False
        self.puresum = operator == '+'
        self.pureprod = operator == '*'
        self.depth = 1
        self.cache = []

        if isinstance(function, BR):
            self.puresum = self.puresum and function.puresum
            self.pureprod = self.pureprod and function.pureprod
            self.simple = function.simple
            self.function = function 
            self.depth += function.depth
        else:
            if not callable(function):
                self.simple = True
            self.function = function
        
    def __call__(self,i):
        
        if not callable(self.function):
            c = self.function
            if self.operator == '+':
                return self.basis + i*c
            else:
                return self.basis * (c**i)
        
        operator = self.operator
        fxn = self.function
        cache = self.cache
        if not cache:
            cache.append(self.basis)
        prev = cache[-1]
        append = cache.append
        for j in range(len(cache), i+1):
            term = fxn(j-1)
            if operator == '+':
                prev = prev + term
            else:
                prev = prev * term
            append(prev)
        return prev
    
    def coefficients(self):
        coefficient = [self.basis]
        if isinstance(self.function, BR):
            coefficient.extend(self.function.coefficients())
        else:
            coefficient.append(self.function)
        self.coeffs = coefficient
        return coefficient
    
    def restore(self, coefficients, op):
        curr = coefficients[-1]
        for i in range(1,len(coefficients)):
            curr = BR(coefficients[-i-1],op, curr)
        return curr
    
    def crsum(self, target):
        c1 = self.coefficients()
        c2 = target.coefficients()

        res = []
        for i in range(min(len(c1),len(c2))):
            res.append(c1[i] + c2[i])
        for i in range(len(c1),len(c2)):
            res.append(c2[i])
        for i in range(len(c2),len(c1)):
            res.append(c1[i])
        
        return self.restore(res, '+')
    
    def crtimes(self, target):
        c1 = self.coefficients()
        c2 = target.coefficients()
        res = []
        for i in range(min(len(c1),len(c2))):
            res.append(c1[i] * c2[i])
        for i in range(len(c1),len(c2)):
            res.append(c2[i])
        for i in range(len(c2),len(c1)):
            res.append(c1[i])
        return self.restore(res,'*')
    
    def crprod(self, target):
        c1 = self.coefficients()
        c2 = target.coefficients()
        res = self.crprodaux(c1,c2)
        return self.restore(res,'+')
    
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

    def crexpt(self,target):
        c1 = self.coefficients()
        c2 = target.coefficients()
        res = self.crexptaux(c1,c2)
        return self.restore(res,'+')
    
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
    
    def __add__(self, target):
        pass 

class CRbinary(BR):

    def __init__(self, leftexp, rightexp, operator):
        super.__init__()
        self.leftexp = leftexp
        self.rightexp = rightexp
        self.procedure = operator

    def __call__(self, i):

        
    



