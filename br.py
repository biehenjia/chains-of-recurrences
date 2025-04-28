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
                self.function = lambda x : function
                self.simple = True
            else:
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
            term = self.function(i - 1)
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
            coefficient.append(self.function(0))
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
        function = lambda x : coefficients[-1]
        curr = function
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
            leaf = self.function(0)
            print("  " * (indent + 1) + f"→ leaf value = {leaf!r}")
    
    def __add__(self, target):
        pass
    def __mul__(self, target):
        pass

