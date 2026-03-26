def string_to_binary(string: str) -> str:
    """
    Convert a string to its binary representation.

    Args:
        string (str): The input string.

    Returns:
        str: The binary representation of the input string.
    """
    return ' '.join(format(ord(char), '08b') for char in string)

def main():
    user_input = input("Enter a string: ")
    binary_representation = string_to_binary(user_input)
    print(f"The binary representation of '{user_input}' is {binary_representation}")

if __name__ == "__main__":
    main()