marks=[10,20,40,100,60]
print(marks)
print(marks[0])
print(marks[3])
print(marks[-1])
print(marks[-2])


marks.append(75)
print(marks)
marks.insert(0,66)
print(marks)

marks.pop()
print(marks)
marks.pop(0)
print(marks)
marks.remove(40)
print(marks)

for x in marks:
  print(x)