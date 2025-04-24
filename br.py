from math import comb, log, exp

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


    def pureprod(self,target):
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
    
    # convolutional alternative to crprod
    # TODO: Proof of correctness; should just be constructive proof
    def crprod(self, target):
        # TODO: safety check from outer scope or return False something like that yea
        if not (self.puresum and target.puresum):
            raise ValueError('NOT PURESUM!!!')
        
        c1 = self.coefficients()
        c2 = target.coefficients()
        k,l = len(c1)-1, len(c2)-1

        res = [0] * (k+l+1)
        # see proof
        for i in range(k+l+1):
            total = 0
            for j in range(max(0, i-l), min(i, k)+1):
                # to use math.comb or not to use math.comb that is the question
                total += comb(i, j) * c1[j] * c2[i-j]
            res[i] = total
        return self.coeffRestore(res,'+')
    

    # TODO: convolutional alternative to crexpt
    # switch to logarithmic form to perform crprod
    def crexpt(self,target): 
        if not (self.pureprod and target.pureprod):
            raise ValueError('NOT PUREPROD!!')
        
        # potential modularization with crprod
        c1 = self.coefficients() # base
        c2 = target.coefficients() # exponent
        k,l = len(c1)-1, len(c2)-1
        bases = [log(c) for c in c1]
        res = [0] * (k+1+l)

        for i in range(k+l+1):
            total = 0 
            for j in range(max(0, i-l), min(i, k)+1):
                # to use math.comb or not to use math.comb that is the question
                total += comb(i, j) * bases[j] * c2[i-j]
            res[i] = total
        bases = [exp(c) for c in bases]
        return self.coeffRestore(bases, '*')
    
    # TODO : rebuild process costly? 
    # Leaning towards not necessarily
    def coeffRestore(self,coefficients,op):
        function = lambda x : coefficients[-1]
        curr = function
        for i in range(1,len(coefficients)):
            curr = BR(coefficients[-i-1],op,curr )
        return curr

    def __repr__(self):
        pass
    
    

        
    
    





