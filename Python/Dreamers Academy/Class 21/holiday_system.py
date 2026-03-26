import datetime

x = datetime.datetime.now()
day_name=x.strftime("%A")
if(day_name=="Friday" or day_name=="Saturday"):
    print("holiday")
else:
    print("working day")