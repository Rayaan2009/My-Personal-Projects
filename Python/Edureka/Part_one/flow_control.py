# no. 1

# syntax
# if (test expression):
#     # statments when the condition is met
# elif (test expression):
#     # statments when the elif condition is met
# else:
#     final statments

# no. 2

x = 11
if x % 3== 0:
    print("x is divisible by 3")
elif x % 5 == 0:
    print("x is divisible by 5")
else:
    print("x is not divisible by 3 or 5")

# no. 3

a = 10
if a>1:
    for x in range(2, a):
        if(a%x) == 0:
            print("Not prime")
            break
    else:
        print("Prime")

else:
    print(" value of a <= 1")

# shorthand if and else

# no. 4

b = 5
c = 7
if b < c: print("b is less than b")

# no. 5

print("b is less than c") if b < c else print("b is greater than b")