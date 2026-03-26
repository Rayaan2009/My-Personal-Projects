from turtle import *
hideturtle()
h=int(input("enter height:"))
w=int(input("enter width:"))
c=input("enter color:")
color(c)
fillcolor(c)
begin_fill()
for x in range(2):
  forward(h)
  left(90)
  forward(w)
  left(90)
end_fill()