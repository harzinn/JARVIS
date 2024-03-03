import openai
from openai import OpenAI
import sys
import subprocess
import tempfile
import json  # Import json for proper serialization

def load_api_key(file_path='api.key'):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print("API key file not found.")
        sys.exit(1)

def initialize_openai_client(api_key):
    return OpenAI(api_key=api_key)

def query_gpt4(client, prompt, debug=False):
    try:
        response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": f"{prompt} in Python."}])
        message_content = response.choices[0].message.content
        if debug:
            # Convert response object to a serializable format
            debug_info = {"model": response.model, "created": response.created, "choices": [{"message": {"role": choice.message.role, "content": choice.message.content}} for choice in response.choices]}
            with open("debug_response.json", "w") as debug_file:
                json.dump(debug_info, debug_file, indent=4)
            print("Full response saved to debug_response.json")
        print(message_content)  # For immediate debugging
        # Extract only Python code, ensuring no human language explanations are included
        code_block = message_content.split("```python")[-1].split("```")[0].strip() if "```python" in message_content else message_content.split("```")[-2].strip() if "```" in message_content else message_content
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
            debug = input("Enable debug mode? (y/n): ").lower() == 'y'
            output = query_gpt4(client, prompt, debug=debug)
            # Check if the output actually contains Python code before proceeding
            if "def" in output or "import" in output or "print" in output:
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
