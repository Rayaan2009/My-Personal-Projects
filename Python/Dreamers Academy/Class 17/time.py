import datetime

x = datetime.datetime.now()
print(x)

#day name
print(x.strftime("%A"))
print(x.strftime("%a"))
#day number
print(x.strftime("%d"))

#month name
print(x.strftime("%B"))
print(x.strftime("%b"))
#month number
print(x.strftime("%m"))

#year
print(x.strftime("%Y"))
print(x.strftime("%y"))

#hour
print(x.strftime("%H"))
print(x.strftime("%I"))

print(x.strftime("%p"))

#minute
print(x.strftime("%M"))
#second
print(x.strftime("%S"))
