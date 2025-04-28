import br

class Expression:
    def __init__(self, subexp = None, environment = None):
        self.environment = {} if environment is None else environment
        self.subexp = subexp
    
    def evaluate(self):
        if self.subexp is None:
            return 0
        return self.subexp.evaluate()
    
    def contextualize(self, mapping):
        self.enironment =mapping
        if self.subexp is None:
            return
        self.subexp.contextualize(mapping)
    
    def __repr__(self): 
        return f"Exp({repr(self.subexp)})"
    
    def hierarchize(self, prefix = '', terminal = True):
        sublabel = ""
        if self.subexp is not None:
            sublabel += '\n' +self.subexp.hierarchize(prefix + ("    " if terminal else "│   "),True)
        return f"{prefix + ('└── ' if terminal else '├── ')}{self.label()}{sublabel}"
    
    def label(self):
        return self.__class__.__name__
    
    def crmake(self, x0, h):
        return self.subexp.crmake(x0,h)


class Atomic(Expression):
    def __init__(self):
        super().__init__()
    

class Symbolic(Atomic):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def evaluate(self): 
        if not self.name in self.environment:
            print(f'{self.name} undefined')
        return self.environment.get(self.name, 0)

    