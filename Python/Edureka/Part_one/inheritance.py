# no. 1

class Parent():
    def first(self):
        print("First Function")

class Child(Parent):
    def second(self):
        print("Second Function")

obj = Child()
obj.first()
obj.second()

# no. 2

class Parent1():
    def first(self):
        print("First Function")

class Parent2():
    def third(self):
        print("Multiple Inheritance")

class Child1(Parent1, Parent2):
    def second(self):
        print("Second Function")

obj = Child()
obj.first()
obj.second()
obj.third()

# no. 3

class Parent():
    def first(self):
        print("First Function")

class Child(Parent):
    def second(self):
        print("Second Function")

class Child2(Child):
    def func(self):
        print("Multilevel Inheritance")

obj = Child2()
obj.first()
obj.second()
obj.func()

# no. 4

class Parent():
    def first(self):
        print("First Function")

class Child(Parent):
    def second(self):
        print("Second Function")

class Child2(Parent):
    def func(self):
        print("Hierarchical Inheritance")

obj = Child()
obj.first()
obj.second()

obj1 = Child()
obj1.first()
obj1.func()

# no. 5

class Parent():
    def first(self):
        print("First Function")

class Child(Parent):
    def second(self):
        print("Second Function")

class Child2(Parent):
    def func(self):
        print("Hierarchical Inheritance")

class Child3(Child, Parent):
    def func2(self):
        print("Hybrid")

obj1 = Child3()
obj1.first()
obj1.func2()

# no. 6

class Parent():
    def first(self):
        print("First Function")

class Child(Parent):
    def second(self):
        super().first()
        print("Second Function")