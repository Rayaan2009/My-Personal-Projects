def add_func(a,b):
  print(a+b)  
def minus_func(a,b):
  print(a-b)  
def mul_func(a,b):
  print(a*b)  
def div_func(a,b):
  print(a/b)  
def pow_func(a,b):
  print(pow(a,b))  
def max_func(a,b):
  print(max(a+b))
def min_func(a,b):
  print(min(a+b))  

print("Enter + for add")
print("Enter - for subtraction")
print("Enter * for multiplication")
print("Enter / for divison")
print("Enter p for power")
print("Enter max for maximum")
print("Enter min for minimum")


while True:
  
  a=int(input("enter first number:"))
  b=int(input("enter second number:"))
  c=input("enter your choice:")
  
  if(c=="+"):
    add_func(a,b)
  elif(c=="-"):
    minus_func(a,b)
  elif(c=="*"):
    mul_func(a,b)
  elif(c=="/"):
    div_func(a,b)
  elif(c=="p"):
    pow_func(a,b)
  elif(c=="max"):
    max_func(a,b)
  elif(c=="min"):
    min_func(a,b)

  x=input("do you want more calculation:")
  if(x=="no"):
    break