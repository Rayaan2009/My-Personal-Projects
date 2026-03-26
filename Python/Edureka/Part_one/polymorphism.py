# no.1

class Apple:
    def type_of(self):
        print("Fruit")

class Potato:
    def type_of(self):
        print("Vegetable")

obj1 = Apple()
obj2 = Potato()

obj1.type_of()
obj2.type_of()

# no. 2

class Bird:
    def information(self):
        print("Birds are very pretty")

class Parrot(Bird):
    def information(self):
        print("Parrot can fly")

obj = Parrot()
obj.information()