## Merge sort

def msort(my_list, left, right):
    if right - left > 1:
        middle = (left + right)//2
        msort(my_list, left , middle)
        msort(my_list, middle, right)
        mlist(my_list, left, middle, right)

def mlist(mylist, left, middle, right):
    leftlist = mylist[left:middle]
    rightlist = mylist[middle:right]
    k = left
    i = 0
    j = 0
    while (left + i <middle and middle + j < right):
        if (leftlist[i] <= rightlist[j]):
            mylist[k] = leftlist[i]
            i = i + 1
        else:
            mylist[k] = rightlist[j]
            j = j + 1
        k = k + 1
    if left + i < middle:
        while k < right:
            mylist[k] = leftlist[i]
            i = i + 1
            k = k + 1

    else:
        while k < right:
            mylist[k] = rightlist[j]
            j = j + 1
            k = k + 1

try:
    mylist = input('Enter the list values to be stored (space separated): ').split()
except EOFError:
    mylist = []

if mylist:
    mylist = [int(x) for x in mylist]
else:
    mylist = [5, 1, 9, 3, 7]  # fallback for non-interactive runs

msort(mylist, 0, len(mylist))
print('The sorted list is: ')
print(mylist)

## Bubble sort

def bs(a):
    b=len(a)-1
    for x in range(b):
        for y in range(b):
            if a[y]>a[y+1]:
                a[y],a[y+1]=a[y+1],a[y]
    return a

## Insertion Sort

def isort(a):
    for x in range(1, len(a)):
        k = a[x]     #element present at index number 1
        j = x-1
        while j >=0 and k < a[j]:     # comparing elements with the next until the last item
            a[j+1] = a[j]
            j -= 1
        a[j+1] = k

a = [24, 56, 1, 60, 17]
isort(a)
print(a)

## Selction Sort

def selsort(myarray, r):
    for x in range(r):
        minimum = x        #first element is assumed to be the minimum 
        for y in range(x + 1, r):
            if myarray[y] < myarray[minimum]:        # comparing mimimum with the next element
                minimum = y
        (myarray[x], myarray[minimum]) = (myarray[minimum], myarray[x])  #swap element if required
mylist = [34, 23, 1, 67, 4]
r = len(mylist)
selsort(mylist, r)
print(mylist)

# Shell Sort

def shsort(myarray, n):
    g = n // 2      # dividing the number of elements by 2 to find the gap
    while g > 0:
        for x in range(g, n):
            y = myarray[x]
            z = x
            while z >= g and myarray[z - g] > y:
                myarray[z] = myarray[z - g]
                z -= g
            myarray[z] = y
        g //= 2
mylist = [23, 12, 1, 17, 45, 2, 13]
length = len(mylist)
shsort(mylist, length)
print(mylist)
