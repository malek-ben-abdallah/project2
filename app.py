import streamlit as st
import pandas as pd
import openai
from openai import OpenAI
import re
import traceback
import sys

# Set up the OpenAI API key
def generate_code(user_input, df, chat_history, api_key1):
    client = OpenAI(api_key=api_key1)
    
    # Generate Python code to visualize or analyze the provided dataset based on the user's query.

    # Args:
    #   user_input (str): The user's query for visualizing or analyzing the data.
    #   df (pandas.DataFrame): The dataset to be used for generating the code.
    #   chat_history (list): A list of dictionaries containing the chat history between the user and the model.

    # Returns:
    #   str: The generated text based on the user's query and the provided dataset.
    #   str: The generated Python code based on the user's query and the provided dataset.
    #   list: The updated chat history.
    #   str: Any error message encountered during code execution.
    
    # Generate a description of the dataset
    dataset_description = f"This dataset contains {len(df.columns)} columns: {', '.join(df.columns)}."

    # The column names and data types
    column_info = pd.DataFrame({'column': df.columns, 'data_type': df.dtypes})

    # Get a few sample rows from the dataset
    sample_rows = df.head(5).to_dict(orient='records')

    prompt = f"""
When handling a user's query, let's think step by step:

1. Identify the key actions or tasks requested by the user.
2. Extract the relevant data entities or columns mentioned in the query.
3. Identify any filters, conditions, or constraints specified in the query.

User Query: {user_input}

Dataset Description:
{dataset_description}

Column Names and Data Types:
{column_info.to_markdown()}

Sample Rows:
{sample_rows}

[always output your chain-of-thought (reasoning and explanations) for the generated visualizations or analyses and what steps you did to get to this result.]

**debug**: The generated code will be sent back to the model for evaluation and debugging.
"""

    chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        seed=2024,
        messages=[
            {"role": "system", "content": "You are a helpful data analysis tool."},
            *chat_history,
            {"role": "user", "content": prompt},
        ],
    )

    try:
        generated_text = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": generated_text})

        # Extract the Python code from the generated text
        generated_code = extract_python_code(generated_text)

        # Send the generated code back to the model for debugging
        debug_prompt = f"""
Evaluate the following code for relevance to the user's query and check for errors:

User Query: {user_input}

Generated Code:
{generated_code}

If the code has errors, provide the corrected code along with an explanation of the errors and the corrections made.
"""
        debug_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            seed=2024,
            messages=[
                {"role": "system", "content": "You are a helpful data analysis tool."},
                *chat_history,
                {"role": "user", "content": debug_prompt},
            ],
        )
        debug_output = debug_response.choices[0].message.content

        if "Corrected Code:" in debug_output:
            generated_code = debug_output.split("Corrected Code:")[-1].strip()

        # Execute the generated code
        exec(generated_code)

        return generated_text, generated_code, chat_history, ""
    except Exception as e:
        error_message = str(e)
        return generated_text, generated_code, chat_history, error_message

def extract_python_code(text):
    # Extract Python code between "```python" and "```"
    pattern = r"```python(.*?)```"
    code_snippets = re.findall(pattern, text, re.DOTALL)
    # Join the code snippets into a single string
    extracted_code = "\n".join(code_snippets)
    return extracted_code.strip()

def main():
    # Title of the application
    st.title("Data Analysis Tool")

    # Get the user's OpenAI API key
    api_key1 = st.text_input("Enter your OpenAI API key:", type="password")

    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset:")
        st.write(df.head())
        chat_history = []

        user_input = st.text_input("What's your query?")

        if st.button("Submit"):
            generated_text, generated_code, chat_history, error_message = generate_code(user_input, df, chat_history, api_key1)

            if generated_code:
                st.markdown(generated_text)

                # Plot the visualization directly
                try:
                    exec(generated_code)
                    st.success("Code ran smoothly.")
                except Exception as e:
                    st.error(f"Error executing the generated code: {e}")
                    st.code(traceback.format_exc())

        # Display Chat History
        if st.button("Show Chat History"):
            st.subheader("Chat History")
            st.write(chat_history)

if __name__ == "__main__":
    main()
