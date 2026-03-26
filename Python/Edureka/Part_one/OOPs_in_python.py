## Class, objects, methods

# class syntax

# no. 1

    # class MyClass:
    #     statement1
    #     .
    #     .
    #     statement n

# no. 2

class NewClass:
    def NewFunc(self):
        return "Hello World!"
obj = NewClass()
print(obj.NewFunc())

# no. 3

class NewClass:
    def NewFunc(self):
        return "Hello World!"
    
    def MyFunc(self):
        return "Welcome to Edureka!"
    
obj = NewClass()
print(obj.NewFunc())

obj2 = NewClass()
print(obj.MyFunc())

# no. 4

class Calculating:
    def add(self, a, b):
        return a+b
    
    def sub(self, a, b):
        return a-b
    
    def product(self, a, b):
        return a*b
    
    def divide(self, a, b):
        return a/b
    
o1 = Calculating()
print(o1.add(4, 5))
print(o1.sub(5, 2))
print(o1.product(32, 5))
print(o1.divide(10, 2))

print("-----------------------------------------")

o2 = Calculating()
print(o2.add(4, 5))
print(o2.sub(5, 2))
print(o2.product(32, 5))
print(o2.divide(10, 2))

# no. 5

class PythonProg:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def newfunc(self):
        print("Hi, my name is " + self.name+ " and my age is "+ self.age)

p1 = PythonProg("Python", "31")
p1.newfunc()