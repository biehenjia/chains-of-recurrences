from parsing import *
import time

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


expr = 'x+2*x+4+x'
ast = Parser(expr).parse()
mapping = {'x':0}
ast.contextualize(mapping)
#print(ast.hierarchize())
a = time.perf_counter()
br = ast.crmake(0,1)
b = time.perf_counter()
print(b-a)
br.dump()
IT = 10**6
res1 = []
res2 = []
start = time.perf_counter()
for i in range(IT):
    res1.append(br(i))
end = time.perf_counter()
e1 = end - start

for x in range (IT):
    mapping['x' ] = x
    res2.append(ast.evaluate())
end1 = time.perf_counter()
e2 = end1- end
print('TIME (S)')
print('CR: ',e1,'NAIVE: ', e2)
print(res1[-1],res2[-1])

print(time.perf_counter()-start)


