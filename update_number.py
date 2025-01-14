#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime

# Change the current working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Function to read the current number from the file
def read_number():
    with open("number.txt", "r") as f:
        return int(f.read().strip())

# Function to write a new number to the file
def write_number(num):
    with open("number.txt", "w") as f:
        f.write(str(num))

# Function to generate a random commit message using a text generation model
def generate_random_commit_message():
    from transformers import pipeline

    generator = pipeline(
        "text-generation",
        model="openai-community/gpt2",
    )
    prompt = """
        Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject. Please keep it short. Here are some examples:

        - feat(auth): add user authentication module
        - fix(api): resolve null pointer exception in user endpoint
        - docs(readme): update installation instructions
        - chore(deps): upgrade lodash to version 4.17.21
        - refactor(utils): simplify date formatting logic

        Now, generate a new commit message:
    """
    generated = generator(
        prompt,
        max_new_tokens=50,
        num_return_sequences=1,
        temperature=0.9,  # Slightly higher for creativity
        top_k=50,  # Limits sampling to top 50 logits
        top_p=0.9,  # Nucleus sampling for diversity
        truncation=True,
    )
    text = generated[0]["generated_text"]

    if "- " in text:
        return text.rsplit("- ", 1)[-1].strip()
    else:
        raise ValueError(f"Unexpected generated text {text}")

# Function to commit changes to the Git repository
def git_commit():
    # Stage the changes
    subprocess.run(["git", "add", "number.txt"])
    # Create commit with current date or generated message
    if "FANCY_JOB_USE_LLM" in os.environ:
        commit_message = generate_random_commit_message()
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Update number: {date}"
    subprocess.run(["git", "commit", "-m", commit_message])

# Function to push the committed changes to GitHub
def git_push():
    result = subprocess.run(["git", "push", "https://github.com/theburak/fancy_job.git"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)

# Function to update the task scheduler with a random time
def update_task_scheduler_with_random_time():
    # Generate random hour (0-23) and minute (0-59)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)

    # Define the new task scheduler command
    new_task_command = f"schtasks /create /tn \"UpdateNumber\" /tr \"{os.path.join(script_dir, 'update_number.py')}\" /sc daily /st {random_hour:02d}:{random_minute:02d}"

    # Delete the existing task if it exists
    os.system("schtasks /delete /tn \"UpdateNumber\" /f")

    # Create the new task
    os.system(new_task_command)

    print(f"Task Scheduler updated to run at {random_hour:02d}:{random_minute:02d} daily.")

# Main function to execute the script logic
def main():
    try:
        current_number = read_number()
        new_number = current_number + 1
        write_number(new_number)
        git_commit()
        git_push()
        update_task_scheduler_with_random_time()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

# Entry point of the script
if __name__ == "__main__":
    main()
