# def name_func(arguments1,...):
#     statement1
#     statement2
#     .
#     ..

# no. 1

def add(x,y):
    sum=x+y
    print(sum)
    return sum
add(2,4)

# no. 2

def new_func(x):
    return(lambda y: x*y)
t = new_func(3)
print(t(5))