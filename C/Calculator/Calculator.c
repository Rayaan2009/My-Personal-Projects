#include <stdio.h>

int add(int x, int y) {
    return x + y;
}

int subtract(int x, int y) {
    return x - y;
}

int multiply(int x, int y) {
    return x * y;
}

float divide(int x, int y) {
    if (y == 0) {
        printf("Cannot divide by zero\n");
        return 0.0;
    }
    return (float) x / y;
}

int main() {
    int choice, num1, num2;

    printf("1. Add\n");
    printf("2. Subtract\n");
    printf("3. Multiply\n");
    printf("4. Divide\n");
    printf("Select operation: ");
    scanf("%d", &choice);

    printf("Enter first number: ");
    scanf("%d", &num1);

    printf("Enter second number: ");
    scanf("%d", &num2);

    switch (choice) {
        case 1:
            printf("Result: %d\n", add(num1, num2));
            break;
        case 2:
            printf("Result: %d\n", subtract(num1, num2));
            break;
        case 3:
            printf("Result: %d\n", multiply(num1, num2));
            break;
        case 4:
            printf("Result: %.3f\n", divide(num1, num2));
            break;
        default:
            printf("Invalid choice\n");
    }

    return 0;
}