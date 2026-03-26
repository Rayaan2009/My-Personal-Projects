user_name="Shakib"
password="Shakib123"

a=0
for x in range(3):
  u=input("enter username:")
  p=input("enter password:")
  if(u==user_name and p==password):
    print("login successful")
    break
  else:
    a=a+1
    if(a==3):
      print("no chance left")
    else:
      print("try again")