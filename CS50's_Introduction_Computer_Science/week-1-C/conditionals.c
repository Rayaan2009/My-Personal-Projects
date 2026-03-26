#include <stdio.h>

int main(void)
{
    int x = 0;
    int y = 2;

    if (x < y)
    {
        printf("x is less than y\n");
    }

    else if (x > y)
    {
        printf("x is greater than y\n");
    }

    else
    {
        printf("x and y are equal!\n");
    }
}