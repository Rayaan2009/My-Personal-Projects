#guessing game 
#computer will generate a random number and user has to guess the number
#user will get 3 chances for guessing the number

import random
a=random.randint(0,10)
print("you can guess 3 times")

for x in range(3):
  guess=int(input("enter your guess"))
  if(guess==a):
    print("correct guesss")
    break
  else:
    print("try again")

print(a)