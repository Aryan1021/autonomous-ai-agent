from agent.utils import (
    generate_filename,
    ensure_output_directory,
    save_text_file,
)

print(generate_filename("proposal", "docx"))

ensure_output_directory()

path = save_text_file(
    "sample.txt",
    "Hello Autonomous AI Agent!"
)

print(path)