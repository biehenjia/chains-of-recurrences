import parsing

expr = "5*(x)^2+9*x+3"
ast = parsing.Parser(expr).parse()
print(ast.subexp)
print(ast.hierarchize())

expr1 = "(2^(x^3+3*x^2-3*x+1))/(2^(x^2-2*x+1))"
ast1 = parsing.Parser(expr1).parse()
print(ast1.hierarchize())

sampleBR = ast1.CRMAKE(1,1)

sampleBR(5)
