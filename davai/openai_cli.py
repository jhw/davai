import logging
import os
import sys
from davai.base_cli import BaseCLI
from openai import OpenAI

# Setup logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s")

# Check if the API key is set in environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logging.error("API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
    sys.exit(1)

# Create the OpenAI client
Client = OpenAI(api_key=api_key)

def call_openai_api(request_text,
                    client=Client,
                    model_name="gpt-4o",
                    max_tokens=2000,
                    temperature=0.7):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request_text}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    # Check if a root directory is provided as a command line argument
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "src"  # Default value if no argument is provided

    # Initialize the CLI with "OpenAI" prompt, call_openai_api function, and root directory
    cli = BaseCLI("OpenAI", call_openai_api, root=root_dir)

    # Start the command loop
    cli.cmdloop()
