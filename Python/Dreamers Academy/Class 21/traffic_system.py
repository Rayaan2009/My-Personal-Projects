speed=int(input("enter vehicle speed:"))
if(speed>70):
  print("1000 taka fine")
elif(speed>=61 and speed<=70):
  print("200 taka fine")
else:
  print("Thank you, no fine")