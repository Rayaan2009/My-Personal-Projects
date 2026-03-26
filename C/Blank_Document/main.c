#include <stdio.h>

typedef enum {
    MONDAY = 1,
    TUESDAY,
    WEDNESDAY,
    THURSDAY,
    FRIDAY,
    SATURDAY,
    SUNDAY
} DayOfWeek;

const char* day_name(DayOfWeek day) {
    switch (day) {
        case MONDAY:   return "Monday";
        case TUESDAY:  return "Tuesday";
        case WEDNESDAY:return "Wednesday";
        case THURSDAY: return "Thursday";
        case FRIDAY:   return "Friday";
        case SATURDAY: return "Saturday";
        case SUNDAY:   return "Sunday";
        default:       return "Invalid day";
    }
}

void print_day_name(int day_number) {
    if (day_number < MONDAY || day_number > SUNDAY) {
        fprintf(stderr, "Error: Invalid day number. Please enter a number between 1 and 7.\n");
        return;
    }

    DayOfWeek day = (DayOfWeek) day_number;
    printf("%s\n", day_name(day));
}