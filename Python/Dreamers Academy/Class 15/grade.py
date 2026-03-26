mark=int(input("enter mark:"))
if(mark>=80 and mark<=100):
  print("you get A+")
elif(mark>=70 and mark<80):
  print("you get A")
elif(mark>=60 and mark<70):
  print("you get A-")
elif(mark>=50 and mark<60):
  print("you get B")
else:
  print("Fail")