import curses
from random import randint
curses.initscr()
window = curses.newwin(20,60)   # y, x
window.keypad(1)
curses.noecho()
curses.curs_set(0)
window.border(0)
window.nodelay(1)
snake = [ (4,10),(4,9),(4,8) ]
food = ( 10,20 )
score = 0 
 
ESC = 27
key = curses.KEY_RIGHT
 
window.addch(food[0],food[1],"#")
 
while key != ESC:
 
  window.timeout(150 -(len(snake)) //5 + len(snake)//5 % 120 )  # increase speed !
 
  prev_key = key
  event = window.getch()
 
  if event != -1:
    key = event
  else:
    key = prev_key
 
  if key not in [curses.KEY_RIGHT,curses.KEY_LEFT,curses.KEY_UP,curses.KEY_DOWN,ESC]:
    key = prev_key
 
  # Calculate the co-ordinates ! 
 
  y = snake[0][0]
  x = snake[0][1]
 
  if key == curses.KEY_DOWN:
    y = y + 1
 
  if key == curses.KEY_UP:
    y = y - 1
 
  if key == curses.KEY_RIGHT:
    x = x + 1
 
  if key == curses.KEY_LEFT:
    x = x - 1
 
  snake.insert(0, (y,x))
 
  # Check if the snake is hitting the wall ! 
 
  if y == 0:
    break
 
  if x == 0:
    break
 
  if y == 19:
    break
 
  if x == 59:
    break
 
  # Check if the snake is hitting itself 
 
  if snake[0] in snake[1:]:
    break
 
  # snake eat the food
 
  if snake[0] == food:
    score = score + 1
 
    food = ()
 
    while food == ():
 
      food = ( randint(1,19), randint(1,59) )
 
      if food in snake:
 
        food = ()
 
    window.addch(food[0],food[1],"#")
 
  else:
 
    #move snake 
    last = snake.pop()
 
    window.addch(last[0],last[1]," ")
 
  window.addch(snake[0][0],snake[0][1],"*")
 
 
curses.endwin()
 
print(f"Your score is {score} !")