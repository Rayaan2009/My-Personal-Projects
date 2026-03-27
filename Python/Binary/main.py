import argparse
from pathlib import Path


def string_to_binary(text: str, encoding: str = "utf-8") -> str:
    """Convert text into a space-separated binary string.

    The text is encoded to bytes first so the result is always made of
    8-bit groups, including for non-ASCII characters.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return " ".join(f"{byte:08b}" for byte in text.encode(encoding))


def binary_to_string(binary_text: str, encoding: str = "utf-8") -> str:
    """Convert a space-separated binary string back into text."""
    if not isinstance(binary_text, str):
        raise TypeError("binary_text must be a string")

    stripped_binary = binary_text.strip()
    if not stripped_binary:
        return ""

    parts = stripped_binary.split()
    invalid_parts = [part for part in parts if len(part) != 8 or any(bit not in "01" for bit in part)]
    if invalid_parts:
        raise ValueError("binary input must contain only 8-bit groups made of 0s and 1s")

    byte_values = bytes(int(part, 2) for part in parts)

    try:
        return byte_values.decode(encoding)
    except UnicodeDecodeError as error:
        raise ValueError(f"binary input is not valid {encoding} data") from error


def text_file_to_binary(input_path: str, output_path: str | None = None, encoding: str = "utf-8") -> str:
    """Convert a text file to its binary representation.

    If output_path is provided, the binary output is written to that file.
    The binary string is always returned.
    """
    source_path = Path(input_path)
    text = source_path.read_text(encoding=encoding)
    binary_text = string_to_binary(text, encoding=encoding)

    if output_path is not None:
        Path(output_path).write_text(binary_text, encoding="utf-8")

    return binary_text


def binary_file_to_text(input_path: str, output_path: str | None = None, encoding: str = "utf-8") -> str:
    """Convert a file containing binary text back into decoded text.

    If output_path is provided, the decoded text is written to that file.
    The decoded text is always returned.
    """
    source_path = Path(input_path)
    binary_text = source_path.read_text(encoding="utf-8")
    decoded_text = binary_to_string(binary_text, encoding=encoding)

    if output_path is not None:
        Path(output_path).write_text(decoded_text, encoding=encoding)

    return decoded_text


def display_menu() -> None:
    print("\nBinary Converter")
    print("1. String to binary")
    print("2. Binary to string")
    print("3. Text file to binary")
    print("4. Binary file to text")
    print("5. Exit")


def prompt_for_output_path() -> str | None:
    output_path = input("Enter an output file path or press Enter to skip saving: ").strip()
    return output_path or None


def handle_string_to_binary() -> None:
    user_input = input("Enter a string: ")
    binary_representation = string_to_binary(user_input)
    if binary_representation:
        print(f"Binary: {binary_representation}")
    else:
        print("Binary: (empty string)")


def handle_binary_to_string() -> None:
    binary_input = input("Enter space-separated 8-bit binary values: ")
    decoded_text = binary_to_string(binary_input)
    if decoded_text:
        print(f"Text: {decoded_text}")
    else:
        print("Text: (empty string)")


def handle_text_file_to_binary() -> None:
    input_path = input("Enter the path to a text file: ").strip()
    output_path = prompt_for_output_path()
    binary_text = text_file_to_binary(input_path, output_path)

    if output_path:
        print(f"Binary file saved to: {output_path}")
    else:
        print(f"Binary: {binary_text if binary_text else '(empty string)'}")


def handle_binary_file_to_text() -> None:
    input_path = input("Enter the path to a binary text file: ").strip()
    output_path = prompt_for_output_path()
    decoded_text = binary_file_to_text(input_path, output_path)

    if output_path:
        print(f"Text file saved to: {output_path}")
    else:
        print(f"Text: {decoded_text if decoded_text else '(empty string)'}")


def write_cli_output(output_text: str, output_path: str | None, encoding: str) -> None:
    if output_path is None:
        print(output_text if output_text else "(empty string)")
        return

    Path(output_path).write_text(output_text, encoding=encoding)
    print(f"Output saved to: {output_path}")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert text and files to binary and back.",
        epilog=(
            "Examples:\n"
            "  python main.py --encode \"Hello\"\n"
            "  python main.py --decode \"01001000 01100101 01101100 01101100 01101111\"\n"
            "  python main.py --file input.txt --output output.txt\n"
            "  python main.py --file binary.txt --mode decode --output text.txt"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--encode", metavar="TEXT", help="convert a text string to binary")
    group.add_argument("--decode", metavar="BINARY", help="convert a binary string to text")
    group.add_argument("--file", metavar="PATH", help="convert a file; defaults to encode mode")
    parser.add_argument(
        "--mode",
        choices=("encode", "decode"),
        default="encode",
        help="conversion mode to use with --file",
    )
    parser.add_argument("--output", metavar="PATH", help="write the result to a file")
    parser.add_argument("--encoding", default="utf-8", help="text encoding to use (default: utf-8)")
    return parser


def run_command_line(args: argparse.Namespace) -> bool:
    if args.encode is not None:
        binary_text = string_to_binary(args.encode, encoding=args.encoding)
        write_cli_output(binary_text, args.output, encoding="utf-8")
        return True

    if args.decode is not None:
        decoded_text = binary_to_string(args.decode, encoding=args.encoding)
        write_cli_output(decoded_text, args.output, encoding=args.encoding)
        return True

    if args.file is not None:
        if args.mode == "decode":
            decoded_text = binary_file_to_text(args.file, args.output, encoding=args.encoding)
            if args.output is None:
                print(decoded_text if decoded_text else "(empty string)")
            else:
                print(f"Output saved to: {args.output}")
        else:
            binary_text = text_file_to_binary(args.file, args.output, encoding=args.encoding)
            if args.output is None:
                print(binary_text if binary_text else "(empty string)")
            else:
                print(f"Output saved to: {args.output}")
        return True

    return False


def run_interactive_menu() -> None:
    while True:
        display_menu()

        try:
            choice = input("Choose an option (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return

        try:
            if choice == "1":
                handle_string_to_binary()
            elif choice == "2":
                handle_binary_to_string()
            elif choice == "3":
                handle_text_file_to_binary()
            elif choice == "4":
                handle_binary_file_to_text()
            elif choice == "5":
                print("Goodbye.")
                return
            else:
                print("Invalid option. Please choose 1, 2, 3, 4, or 5.")
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return
        except FileNotFoundError:
            print("File not found. Please check the path and try again.")
        except OSError as error:
            print(f"File error: {error}")
        except ValueError as error:
            print(f"Invalid input: {error}")


def main() -> int:
    parser = build_argument_parser()

    try:
        args = parser.parse_args()
        if run_command_line(args):
            return 0
        run_interactive_menu()
        return 0
    except FileNotFoundError:
        print("File not found. Please check the path and try again.")
        return 1
    except OSError as error:
        print(f"File error: {error}")
        return 1
    except ValueError as error:
        print(f"Invalid input: {error}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())