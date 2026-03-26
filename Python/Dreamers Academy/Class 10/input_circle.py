from turtle import *
hideturtle()
r=int(input("enter radius for circle:"))
c=input("enter color for circle:")
color(c)
fillcolor(c)
begin_fill()
circle(r)
end_fill()