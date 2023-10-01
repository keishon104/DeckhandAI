# # TODO: Create demo ready code. 
# # Steps: 
# ✅   1.) Complete a simple Python code (Calculator)
# #   2.) Run DeckhandAI, with verbose mode enabled - Need to install a package called fire, it'll enable the code to become a CLI. 
# ✅   3.) Input target file into system
# ✅   4.) Deckhand determines the type of file [.py,.js,.ts]
# ✅   5.) Deckhand reads file content
# ✅   6.) Deckhand sends file contents to OpenAI with instructions to create a test file that tests all aspects of the code
# ✅   7.) OpenAI generates testfile based on input file
# #   8.) Deckhand ensures instructions from OpenAI are correct and according to specs. If not retry to get a correct result 
# ✅   9.) Deckhand creates a folder and file for the OpenAI results generated. 
# ✅   10.) Deckhand inputs generated code into file
# ✅   11.) Deckhand automatically runs file to determine if it passes tests. 
# Current Step --  12.) If code fails the test, the error code is resent to OpenAI to come up with code suggestions. If the code fails more than 3 times then terminate the program or ask for further context. 
# #   13.) New code is input in file. 
# #   14.) If code passes terminate the program. 


import os
import openai
import subprocess
from os.path import join, dirname
from dotenv import load_dotenv

# Constants and Configurations
dotenv_path = join(dirname(__file__), '.env.local')
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"

# Max number of Retries
MAX_RETRIES = 3

# Language mapping based on file extensions
LANGUAGE_MAPPING = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
}

# Execution commands based on language
EXECUTION_COMMANDS = {
    'Python': ['python'],
    'JavaScript': ['node'],
    'TypeScript': ['ts-node'],  # Assuming you have ts-node installed for direct execution
    # Add more commands as needed
}


def get_language_from_extension(file_path):
    """
    Determines the programming language based on the file extension.
    
    Args:
        file_path (str): Path to the source file.
    
    Returns:
        str: Programming language of the file.
    """
    _, file_extension = os.path.splitext(file_path)
    return LANGUAGE_MAPPING.get(file_extension, "Unknown")

# ... [other functions]


def read_python_file(file_path):
    """
     Reads the content of a python file provided by the user.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        lines: List of lines in the file.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return lines


def count_chars_in_file(file_path, original_file_path):
    """
    Creates a test file with the provided content in the same directory as the original file.
    
    Args:
        chat_result (str): Content for the test file.
        original_file_path (str): Path to the original file to determine the directory.
    
    Returns:
        int: Number of characters in the file.
    """
    directory = os.path.dirname(original_file_path)
    test_file_path = os.path.join(directory, "testfile.py")
    with open(test_file_path, 'r') as f:
        contents = f.read()
    return sum(len(s) for s in contents)




def create_test_file(chat_result, original_file_path):
    """
    Creates a test file with the provided content.
    
    Args:
        chat_result (str): Content for the test file.
    """
    directory = os.path.dirname(original_file_path)
    test_file_path = os.path.join(directory, "testfile.py")

    with open(test_file_path, "x") as f:
        f.write(chat_result)
    
    return test_file_path



def execute_file_based_on_language(file_path, language):
    """
    Executes a file based on its programming language.
    
    Args:
        file_path (str): Path to the file to execute.
        language (str): Programming language of the file.

     Returns:
        tuple: (bool, str) - Success status and error message (if any).
    """
    command = EXECUTION_COMMANDS.get(language)
    if not command:
        print(f"No execution command found for language: {language}")
        return False, f"No execution command for {language}"

    result = subprocess.run(command + [file_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors encountered:")
        print(result.stderr)
        return False, result.stderr
    return True, ""

# Revisions needed. 
def get_suggested_fix_from_openai(error_message):
    """
    Queries OpenAI API for a suggested fix based on the provided error message.
    
    Args:
        error_message (str): Error message from failed execution.
    
    Returns:
        str: Suggested code fix from OpenAI.
    """
    chat_completion = openai.ChatCompletion.create(
        model=MODEL_NAME, 
        messages=[{
            "role": "user", 
            "content": f"Suggest a fix for the following error in the code: {error_message}"
        }]
    )
    return chat_completion.choices[0].message.content


def get_file_content(lines):
    """
    Uses OpenAI API to generate a test file content for given lines of code.
    
    Args:
        lines (list): Lines of the source code.
    
    Returns:
        str: Generated test file content.
    """
    chat_completion = openai.ChatCompletion.create(
        model=MODEL_NAME, 
        messages=[{
            "role": "user", 
            "content": f"Generate a thorough unit test for the following code {lines}. The unit test should include the imports needed to test the original code's functions. There should be no comments or explainations, ONLY THE CODE."
        }]
    )
    return chat_completion.choices[0].message.content


def main():
    file_path = input("Enter the path of the coding file: ")
    language = get_language_from_extension(file_path)
    print(f"The source code is written in {language}.")

    lines = read_python_file(file_path)
    # number_of_chars = count_chars_in_file(file_path)
    number_of_tokens = sum(len(s) for s in lines)
    
    # print(f"Number of characters in the file: {number_of_chars}")
    # TODO: Install and integrate tik-token package to accurately determine how many tokens are in a file. 
    print(f"Number of tokens in the file: {round(number_of_tokens / 4, 1)}")
    
    test_content = get_file_content(lines)
    test_file_path = create_test_file(test_content, file_path)

    print("Test file generated successfully.")

    print("Executing test file... ")
    execute_file_based_on_language(test_file_path, language)


if __name__ == "__main__":
    main()
