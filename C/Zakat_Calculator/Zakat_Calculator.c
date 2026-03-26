#include <stdio.h>

// Function to calculate Zakat
float calculate_zakat(float wealth, float nisab) {
    float zakat_percentage = 2.5 / 100;  // Zakat is 2.5% of wealth
    float zakat = 0;

    if (wealth >= nisab) {
        zakat = wealth * zakat_percentage;
    }

    return zakat;
}

int main() {
    printf("Welcome to the Zakat Calculator!\n");

    float wealth, nisab;
    printf("Enter your total wealth: ");
    scanf("%f", &wealth);

    nisab = 837;  // Set the nisab value for your region or use the default value

    float zakat_amount = calculate_zakat(wealth, nisab);
    printf("Your Zakat amount is: %.2f\n", zakat_amount);

    return 0;
}