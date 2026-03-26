// Main Code from CS50

///#include <cs50.h>
// #include <stdio.h>

// int maine(void)
// {
//     int x = get_int("What's x? ");
//     int y = get_int("What's y? ");

//     if (x < y)
//     {
//         printf("x is less than y\n");
//     }
//     else if (x > y)
//     {
//         printf("x is greater than y\n");
//     }
//     else
//     {
//         printf("x is equal to y\n");
//     }
// }

// --------------------------------------------------

#include <stdio.h>

int main(void)
{
    int x, y;
    printf("What's x? ");
    scanf("%d", &x);
    printf("What's y? ");
    scanf("%d", &y);

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
        printf("x is equal to y\n");
    }

    return 0;
}
