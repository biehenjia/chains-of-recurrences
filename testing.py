from mcr import *

exp = Expression(
    Summation(
        Exponentiate(Symbolic('x'),Numeric(2),),
        Summation(Symbolic('x'),Numeric(3))
        )
)

print(exp.hierarchize())