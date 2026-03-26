def fizz_buzz(a):
  if(a%3==0 and a%5==0):
    print("FizzBuzz")
  elif(a%5==0):
    print("Buzz")
  elif(a%3==0):
    print("Fizz")
  else:
    print(a)

x=int(input("enter a number:"))
fizz_buzz(x)