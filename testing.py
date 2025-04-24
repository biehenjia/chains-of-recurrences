import parsing

expr = "5*(x)^2+9*x+3"
ast = parsing.Parser(expr).parse()
print(ast.subexp)
print(ast.hierarchize())