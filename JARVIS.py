import openai
from openai import OpenAI
import sys
import subprocess
import tempfile

def load_api_key(file_path='api.key'):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print("API key file not found.")
        sys.exit(1)

def initialize_openai_client(api_key):
    return OpenAI(api_key=api_key)

def query_gpt4(client, prompt):
    try:
        # Ensure the prompt always asks for a Python script
        response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": f"{prompt} in Python."}])
        message_content = response.choices[0].message.content
        # Extract only Python code, removing non-code text and ensuring no human language explanations are included
        if "```python" in message_content:
            code_block = message_content.split("```python")[-1].split("```")[0].strip()
        elif "```" in message_content:  # Fallback in case 'python' is not specified
            code_block = message_content.split("```")[-2].strip()
        else:
            code_block = message_content  # Direct code without markdown
        return code_block
    except Exception as e:
        print(f"Failed to query GPT-4: {str(e)}")
        return None

def run_script(code):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(code)
        temp_file.flush()
        try:
            result = subprocess.run(['python3', temp_file_name], capture_output=True, text=True, check=True)
            print("Script Output:\n", result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print("Script Error:\n", e.stderr)
            return False
        finally:
            temp_file.close()

def save_output(content):
    if content:
        run = input("Do you want to run the script first? (y/n): ")
        if run.lower() == 'y':
            success = run_script(content)
            if success:
                save = input("Script ran successfully. Do you want to save the output? (y/n): ")
            else:
                save = input("Script encountered an error. Do you still want to save the output? (y/n): ")
        else:
            save = input("Do you want to save the output? (y/n): ")
        if save.lower() == 'y':
            filename = input("Enter filename: ")
            with open(filename, 'w') as file:
                file.write(content)
            print(f"Output saved to {filename}")

def main():
    api_key = load_api_key()
    client = initialize_openai_client(api_key)
    while True:
        print("\n1. Query GPT-4\n2. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            prompt = input("Enter your prompt: ")
            output = query_gpt4(client, prompt)
            # Ensure only Python code is run/saved, with no human language explanations
            if output.strip().startswith("import") or output.strip().startswith("from"):
                save_output(output)
            else:
                print("Error: The output did not contain valid Python code.")
        elif choice == '2':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
