from turtle import *
hideturtle()
color("green")
fillcolor("green")
begin_fill()
for x in range(2):
  forward(150)
  left(90)
  forward(80)
  left(90)

end_fill()

penup()
goto(70,15)
pendown()

color("red")
fillcolor("red")
begin_fill()
circle(30)
end_fill()
