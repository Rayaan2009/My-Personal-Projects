a=[1,2,7,10,11,17,1,2]
b=[]

for x in a:
  if(x not in b):
    b.append(x)

print(b)