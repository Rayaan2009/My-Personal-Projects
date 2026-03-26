#include <conio.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

#define WIDTH 30
#define HEIGHT 20

// Snake data structures
int snakeX[100], snakeY[100];
int length;
int foodX, foodY;
bool gameOver;
enum Direction { STOP = 0, LEFT, RIGHT, UP, DOWN };
enum Direction dir;

// Function to initialize the game
void setup() {
  gameOver = false;
  dir = STOP;
  length = 1;
  snakeX[0] = WIDTH / 2;
  snakeY[0] = HEIGHT / 2;
  foodX = rand() % WIDTH;
  foodY = rand() % HEIGHT;
}

// Function to draw the game board
void drawBoard() {
  system("cls");
  for (int i = 0; i < WIDTH + 2; i++)
    printf("#");
  printf("\n");

  for (int i = 0; i < HEIGHT; i++) {
    for (int j = 0; j < WIDTH; j++) {
      if (j == 0)
        printf("#");
      if (i == snakeY[0] && j == snakeX[0])
        printf("O");
      else if (i == foodY && j == foodX)
        printf("F");
      else {
        bool print = false;
        for (int k = 1; k < length; k++) {
          if (i == snakeY[k] && j == snakeX[k]) {
            printf("o");
            print = true;
          }
        }
        if (!print)
          printf(" ");
      }

      if (j == WIDTH - 1)
        printf("#");
    }
    printf("\n");
  }

  for (int i = 0; i < WIDTH + 2; i++)
    printf("#");
  printf("\n");
}

// Function to take input from the player
void getInput() {
  if (_kbhit()) {
    switch (_getch()) {
    case 'a':
      dir = LEFT;
      break;
    case 'd':
      dir = RIGHT;
      break;
    case 'w':
      dir = UP;
      break;
    case 's':
      dir = DOWN;
      break;
    case 'x':
      gameOver = true;
      break;
    }
  }
}

// Function to update the game state
void update() {
  // Move the snake body
  for (int i = length - 1; i > 0; i--) {
    snakeX[i] = snakeX[i - 1];
    snakeY[i] = snakeY[i - 1];
  }

  // Move the snake head based on the direction
  switch (dir) {
  case LEFT:
    snakeX[0]--;
    break;
  case RIGHT:
    snakeX[0]++;
    break;
  case UP:
    snakeY[0]--;
    break;
  case DOWN:
    snakeY[0]++;
    break;
  }

  // Check for collisions with food
  if (snakeX[0] == foodX && snakeY[0] == foodY) {
    length++;
    foodX = rand() % WIDTH;
    foodY = rand() % HEIGHT;
  }

  // Check for collisions with the boundaries
  if (snakeX[0] < 0 || snakeX[0] >= WIDTH || snakeY[0] < 0 ||
      snakeY[0] >= HEIGHT)
    gameOver = true;

  // Check for collisions with itself
  for (int i = 1; i < length; i++) {
    if (snakeX[0] == snakeX[i] && snakeY[0] == snakeY[i])
      gameOver = true;
  }
}

int main() {
  setup();
  while (!gameOver) {
    drawBoard();
    getInput();
    update();
    Sleep(100); // Adjust the game speed here (in milliseconds)
  }
  printf("Game Over!\n");
  return 0;
}