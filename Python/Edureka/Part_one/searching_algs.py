# Linear search
def lin_search(myarray, n, key):

    for x in range(0, n):
        if (myarray[x] == key):
            return x
    return -1

myarray = [12, 1, 34, 17]
key = 16
n = len(myarray)
matched = lin_search(myarray, n, key)
if(matched == -1):
    print("Key is not present")
else:
    print("Key is present in the given list at index", matched)

# Binary search

def bin_search(mylist, key):
    l = 0
    r = len(mylist) - 1
    matched = False
    while (l<=r and not matched):
        middle = (l + r)//2
        if mylist[middle] == key:
            matched = True
        else:
            if key < mylist[middle]:
                r = middle - 1
            else:
                l = middle + 1
    return matched
print(bin_search([2, 3, 56, 13, 1], 56))
print(bin_search([2, 3, 56, 13, 1], 26))