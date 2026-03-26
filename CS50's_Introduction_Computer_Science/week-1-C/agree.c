// Main Code from CS50

// #include <cs50.h>
// #include <stdio.h>

// int main(void)
// {
//     char c = get_char("Do you agree? ");

//     if (c == 'y' || c == 'Y')
//     {
//         printf("Agreed.\n");
//     }
//     else if (c == 'n' || c == 'N')
//     {
//         printf("Not agreed.\n");
//     }

//     return 0;
// }

// ------------------------------------------------------

#include <stdio.h>

int main(void)
{
    char c;
    printf("Do you agree? ");
    scanf(" %c", &c);

    if (c == 'y' || c == 'Y')
    {
        printf("Agreed.\n");
    }
    else if (c == 'n' || c == 'N')
    {
        printf("Not agreed.\n");
    }

    return 0;
}
