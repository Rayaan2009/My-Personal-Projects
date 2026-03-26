year=int(input("enter year:"))
if(year%4==0 and not year%100==0):
  print("leap year")
else:
  print("not leap year")