from abc import *
print(help(ABC))

class Bank(ABC):
    def bank_name(slef):
        print("HDFC")

    def bank_loc(self):
        pass

class Bank_loc(Bank):
    def bank_loc(self):
        print("Bangalore")

obj = Bank_loc()
obj.bank_name()
obj.bank_loc()