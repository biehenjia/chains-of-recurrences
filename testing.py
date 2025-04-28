from parsing import *
# expr = "5*(x)^2+9*x+3"
# ast = parsing.Parser(expr).parse()
# print(ast.subexp)
# print(ast.hierarchize())

# expr1 = "(2^(x^3+3*x^2-3*x+1))/(2^(x^2-2*x+1))"
# ast1 = parsing.Parser(expr1).parse()
# print(ast1.hierarchize())


# expr2 = "x^2"
# ast2 = parsing.Parser(expr2).parse()
# print(ast2.hierarchize())

# br = parsing.mcr.CRMAKE(ast2,0,1)
# br.dump()

# for i in range(8):
#     print(br(i))

expr = "x"
ast = Parser(expr).parse()


br1 = BR(0,'+',1)
br2 = BR(0,'+',1)
br3 = br1 * br2
br3 *= br3
br3.dump()
print(br3.puresum)
for i in range(5):
    a = br1(i) * br2(i)
    print(br1(i),br2(i),a,br3(i))





