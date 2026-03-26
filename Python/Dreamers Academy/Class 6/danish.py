from turtle import *
hideturtle()
color("red")
fillcolor("red")
begin_fill()
for x in range(2):
  forward(150)
  left(90)
  forward(80)
  left(90)

end_fill()

penup()
goto(0,35)
pendown()


color("white")
fillcolor("white")
begin_fill()
for x in range(2):
  forward(150)
  left(90)
  forward(15)
  left(90)

end_fill()


penup()
goto(34,0)
pendown()


color("white")
fillcolor("white")
begin_fill()
for x in range(2):
  forward(15)
  left(90)
  forward(80)
  left(90)

end_fill()
