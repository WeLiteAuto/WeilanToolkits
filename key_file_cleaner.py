import os
import logging
import sys
import time
if os.name == 'nt':  # Windows
    import msvcrt
else:  # macOS and Linux
    import tty
    import termios


# Setup basic configuration for logging
logging.basicConfig(filename='KeyFileCleaner.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def line_to_keep(line: str) -> bool:
    """
    Determine if a line should be kept.

    A line is kept if it does not start with the '$' character.

    Parameters
    ----------
    line : str
        The line to evaluate.

    Returns
    -------
    bool
        True if the line should be kept, False otherwise.

    Raises
    ------
    TypeError
        If line is None.
    """
    if line is None:
        raise TypeError("line is None")

    return not line.startswith('$')

  

def process_file(file_path: str) -> None:
    """
    Process a single .key file, removing unwanted lines.

    Parameters
    ----------
    file_path : str
        The path to the file to process.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If file_path is None or empty.
    FileNotFoundError
        If the file specified by file_path does not exist.
    UnicodeDecodeError
        If there is an error decoding the file.
    Exception
        If there is an unhandled exception when processing the file.
    """
    if file_path is None or file_path == '':
        raise ValueError("file_path is None or empty")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        # with open(file_path, 'r', encoding='utf-8') as file:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            count = len(lines)
        new_lines = [line for line in lines if line_to_keep(line)]
        count -= len(new_lines)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        # print(f"Processed file: {file_path}, removed {count} lines.")
        logging.info(f"Processed file: {file_path}, removed {count} lines.")
    except UnicodeDecodeError as e:
        logging.error(f"Error decoding {file_path}: {str(e)}")
    except Exception as e:
        logging.error(f"Unhandled exception processing {file_path}: {str(e)}")
        # raise


def remove_lines_in_files(directory: str, remove_d3p: bool) -> None:
    """
    Walk through the directory and process each .key file.

    For each file in the directory, check if it has an extension or start
    in file_extensions_to_remove. If so, remove the file.
    If the file is a .key file, process it.

    Parameters
    ----------
    directory : str
        The directory to search for files to process.

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If directory is None.
    FileNotFoundError
        If the directory specified by directory does not exist.
    """
    if directory is None:
        raise TypeError("directory is None")
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"directory {directory} is not a valid directory")

    file_extensions_to_remove = ['.ansa', '.hm', '.mvw', '.catpart', '.cfile']
    file_starts_to_remove = ["._", "ansa", ".lock", "d3d", "d3f", "lsrun", ".lock","mess", "d3h", 'lspost']
    if remove_d3p:
        file_starts_to_remove.append("d3p")
    files_removed = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file is None:
                raise Exception("file is None")
            file_path = os.path.join(root, file)
            if file.lower().endswith(tuple(file_extensions_to_remove)) or file.lower().startswith(tuple(file_starts_to_remove)):
                try:
                    os.remove(file_path)
                    files_removed += 1
                    logging.info(f"Removed file: {file_path}, {files_removed}")
                except Exception as e:
                    logging.error(f"Failed to remove {file_path}`: {str(e)}")
                    
            elif file.endswith(('.key', '.k')):
                try:
                    process_file(file_path)
                except Exception as e:
                    logging.error(f"Unhandled exception processing {file_path}: {str(e)}")
                    raise
    print("All .key files have been processed.")

def check_keyboard_interrupt():
    if os.name == 'nt':  # Windows
        if msvcrt.kbhit():
            msvcrt.getch()
            return True
    else:  # macOS and Linux
        try:
            # Save the terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                # Set the terminal to raw mode
                tty.setraw(sys.stdin.fileno())
                # Check if there's input waiting
                if sys.stdin.read(1):
                    return True
            finally:
                # Restore the terminal settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            pass
    return False

def wait_key():
    print("\nPress any key to exit...")
    if getattr(sys, 'frozen', False):
        while True:
            if msvcrt.kbhit():
                msvcrt.getch()
                break
            time.sleep(0.1)

def read_file(file_path: str) -> str:
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, try with error handling
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            logging.warning(f"File {file_path} contains unknown characters that were replaced")
            return file.read()
    except Exception as e:
        logging.error(f"Failed to read file {file_path}: {str(e)}")
        return ""

def write_file(file_path: str, content: str) -> None:
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        logging.error(f"Failed to write file {file_path}: {str(e)}")
 
def main() -> None:
    """
    The main entry point for the program.

    Asks the user for the directory to process and then calls remove_lines_in_files with that directory.
    Also checks for null pointer references, unhandled exceptions, and other potential bugs.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If the directory is None.
    UnicodeEncodeError
        If there is an error encoding the directory.
    """
    try:
        print("Welcome to the File Processing Tool")
        directory: str = input("Please enter the directory path to process (Enter for Current Directory): ").strip()
        d3p_remove = input("Remove d3plot files (y/n): ").strip().lower()

        # If the user did not enter anything, use the current directory
        if not directory:
            directory = os.getcwd()
        else:
            # Convert relative path to absolute path
            directory = os.path.abspath(directory)

        # Validate directory exists
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory does not exist: {directory}")
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # Process d3p_remove choice
        remove_d3p = d3p_remove.startswith('y')
        remove_lines_in_files(directory, remove_d3p)

    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"\nError: {str(e)}")
        logging.error(str(e))
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        logging.error(f"Unhandled exception: {str(e)}")
    finally:
        wait_key()


if __name__ == "__main__":
    main()