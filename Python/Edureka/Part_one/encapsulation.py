# parent
# __privatemember = _parent__privatemember


# Child
# __privatemember = _Child__privatemember

# no. 1

class A:
    def _int_(self):
        self.__Hi()

    def HelloWorld(self):
        print("HelloWorld")

    def __Hi(self):
        print("Welcome to Edureka!")

obj = A()
obj.HelloWorld()
obj._A__Hi()

# no. 2

class Base:
    def _single(self):
        print("Single underscore")

    def __double(self):
        print("Double underscore")

class Child(Base):
    def fun1(self):
        self._single()

    def fun2(self):
        self._Base__double()

obj = Child()
obj.fun1()
obj.fun2()