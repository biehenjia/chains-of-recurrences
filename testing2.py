from parsing import *
import time 
expr = 'sin(x^2)'
ast = Parser(expr).parse()
print(ast.hierarchize())
br = ast.crmake(0,1)

br.dump()
res1 = []
res2 = []
p1 = time.perf_counter()
for i in range(100):
    res1.append(br(i))

p2 = time.perf_counter()

for i in range(100):
    res2.append(sin(i**2))
p3 = time.perf_counter()

print(p2-p1)
print(p3-p2)
