import os
import chainlit as cl
import pandas as pd
from openai import OpenAI

# Set your OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Global variable to store the loaded CSV data
csv_data = None

@cl.on_chat_start
async def on_chat_start():
    """Greet the user when the chat starts."""
    await cl.Message(content="Welcome! You can upload a CSV file or chat with me.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle user messages and process uploaded files."""
    global csv_data

    if message.elements:
        for file in message.elements:
            if file.mime == "text/csv":
                # Load the CSV into a pandas DataFrame
                csv_data = pd.read_csv(file.path)

                # If a query is present with the file upload, process it
                if message.content:
                    response = await process_query(message.content)
                    await cl.Message(content=response).send()
                    return

                # No query, no response
                return

    # Handle queries after the file has been uploaded
    if message.content:
        if csv_data is not None:
            response = await process_query(message.content)
        else:
            response = await handle_chitchat(message.content)
        await cl.Message(content=response).send()

async def process_query(user_message):
    """Process a query related to the CSV data."""
    try:
        # Prompt to OpenAI for code generation
        prompt = (
            f"You are a Python data assistant. Write Python code to analyze a pandas DataFrame named 'csv_data' based on the following user query:\n\n"
            f"User query: {user_message}\n\n"
            "The code should assign the result to a variable named 'result'. Do not use print()."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        # Extract the generated code
        generated_code = response.choices[0].message.content

        # Execute the code and return the result
        execution_result = execute_code(generated_code)
        return f"Query Result:\n{execution_result}\n\nGenerated Code:\n```python\n{generated_code}\n```"

    except Exception as e:
        return f"Error: {str(e)}"

async def handle_chitchat(user_message):
    """Handle general chit-chat."""
    try:
        # Prompt OpenAI to handle chit-chat
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if required
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,  # Higher temperature for more creative responses
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def execute_code(code):
    """Safely execute the generated Python code and return the result."""
    global csv_data
    try:
        local_vars = {}
        exec(code, {'csv_data': csv_data}, local_vars)  # Execute with the CSV context
        return local_vars.get("result", "No result found in the code execution.")
    except Exception as e:
        return f"Execution Error: {str(e)}"

