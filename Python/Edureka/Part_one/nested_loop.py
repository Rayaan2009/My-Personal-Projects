# no. 1

for x in range(1, 10):
    for y in range(x):
        print(x, end=" ")
    print()

# no. 2

a = [1, 2, 3, 4, 5]
while a:
    print(a.pop(-1))
    b = ["--------------------"]
    while b:
        print(b.pop(0))

# no. 3

def fib():
    f,s=0,1
    while True:
        yield f
        f,s=s, f+s
for x in fib():
    if x>50:
        break
    print(x, end=" ")