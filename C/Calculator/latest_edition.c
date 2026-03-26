#include <stdio.h>

switch (choice) {
    case 1:
        printf("Enter first number: ");
        scanf("%d", &num1);
        printf("Enter second number: ");
        scanf("%d", &num2);
        printf("Result: %d\n", add(num1, num2));
        break;
    case 2:
        printf("Enter first number: ");
        scanf("%d", &num1);
        printf("Enter second number: ");
        scanf("%d", &num2);
        printf("Result: %d\n", subtract(num1, num2));
        break;
    case 3:
        printf("Enter first number: ");
        scanf("%d", &num1);
        printf("Enter second number: ");
        scanf("%d", &num2);
        printf("Result: %d\n", multiply(num1, num2));
        break;
    case 4:
        printf("Enter first number: ");
        scanf("%d", &num1);
        printf("Enter second number: ");
        scanf("%d", &num2);
        printf("Result: %.2f\n", divide(num1, num2));
        break;
    default:
        printf("Invalid choice\n");
        break;
}