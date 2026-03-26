from turtle import *
hideturtle()
color("red")
fillcolor("red")
begin_fill()
for x in range(2):
  forward(150)
  left(90)
  forward(40)
  left(90)

end_fill()

penup()
goto(0,40)
pendown()


color("black")
fillcolor("black")
begin_fill()
for x in range(2):
  forward(150)
  left(90)
  forward(40)
  left(90)

end_fill()


penup()
goto(72,18)
pendown()

color("yellow")
fillcolor("yellow")
begin_fill()
circle(25)
end_fill()