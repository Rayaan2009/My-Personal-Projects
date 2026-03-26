username=input("enter username")
while True:
  password=input("enter password")
  if(password.islower()):
    print("atleast one charecter should be in upper case")
  elif(password.isupper()):
    print("atleast one charecter should be in lower case")
  elif(password.isalpha()):
    print("atleast one digit or special charecter")
  elif(password.isdigit()):
    print("atleast one charecter")
  else:
    print("successful password")
    break