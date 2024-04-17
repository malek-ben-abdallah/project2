import streamlit as st
import pandas as pd
from openai import OpenAI
import openai
import re
import traceback

def generate_code(user_input, df, api_key1):
    client = OpenAI(api_key=api_key1)
    
    # Generate a description of the dataset
    dataset_description = f"This dataset contains {len(df.columns)} columns: {', '.join(df.columns)}."

    # The column names and data types
    column_info = pd.DataFrame({'column': df.columns, 'data_type': df.dtypes})

    # Get a few sample rows from the dataset
    sample_rows = df.head(5).to_dict(orient='records')

    prompt = f"""
When handling a user's query, Let's think step by step: follow these steps if necessary to generate appropriate visualizations or analyses:

1. Identify the key actions or tasks requested by the user, such as "visualize", "analyze", "give", "compare", "show", "find", "calculate", "sort" etc. These actions can be verbs or phrases that indicate the desired operation or analysis the user wants to perform.

2. Extract the relevant data entities or columns mentioned in the query, such as column names, aggregations (e.g., "average", "sum"). These entities represent the variables or features of interest.

3. Identify any filters, conditions, or constraints specified in the query, such as "top", "across different", "where", "greater than", etc. These filters help narrow down or subset the data based on certain criteria.

Based on the identified actions, data entities, filters extracted from the user query:

   a. Generate the necessary code to perform the required operations or calculations on the provided dataset if there is any.
   b. Determine the appropriate visualizations or analyses using the appropriate libraries (e.g., pandas, matplotlib, seaborn) and generate the code.

If the user query is long or contains multiple actions, break them into sub-query steps as explained above and combine the results or visualizations into a cohesive output, such as a single figure with multiple subplots, a report-like structure, or an interactive dashboard.

Provide context and explanations for each step or sub-query, highlighting any insights, patterns, or findings observed in the data based on the visualizations or analyses.

User Query: {user_input}

[Generate code and visualizations based on the user's query and the dataset provided following the instructions above. Refer to the chat history for context if needed. Do not create a dataset, assume the dataset is always provided by the user. it name is "df" so use it directly]

Dataset Description:
{dataset_description}

Column Names and Data Types:
{column_info.to_markdown()}

Sample Rows:
{sample_rows}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        seed=2024,
        messages=[
            {"role": "system", "content": "You are a helpful data analysis tool."},
            {"role": "user", "content": user_input},
            {"role": "user", "content": prompt},
        ],
    )

    try:
        generated_text = response.choices[0].message.content

        # Extract the Python code from the generated text
        generated_code = extract_python_code(generated_text)

        return generated_text, generated_code, ""
    except Exception as e:
        error_message = str(e)
        return generated_text, "", error_message

def extract_python_code(text):
    # Extract Python code between "```python" and "```"
    pattern = r"```python(.*?)```"
    code_snippets = re.findall(pattern, text, re.DOTALL)
    # Join the code snippets into a single string
    extracted_code = "\n".join(code_snippets)
    return extracted_code.strip()

def main():
    st.title("Data Analysis Tool")
    api_key1 = st.text_input("Enter your OpenAI API key:", type="password")

    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset:")
        st.write(df.head())

        questions = []
        responses = []
        errors = []

        while True:
            user_query = st.text_input("Enter your query:")

            if user_query:
                generated_text, generated_code, error_message = generate_code(user_query, df, api_key1)

                if generated_code:
                    questions.append(user_query)
                    responses.append(generated_text)
                    errors.append(error_message)

                    st.markdown(generated_text)
                    st.code(generated_code, language="python")
                    if error_message:
                        st.error(f"Errors occurred: {error_message}")
                    else:
                        try:
                            exec(generated_code)
                            st.success("Code ran smoothly.")
                        except Exception as e:
                            st.error(f"Error executing the generated code: {e}")
                            st.code(traceback.format_exc())

            if st.button("Ask Another Question"):
                continue
            else:
                break

        if questions:
            st.markdown("## Chat History")
            for i in range(len(questions)):
                st.subheader(f"Question: {questions[i]}")
                st.markdown(f"Response: {responses[i]}")
                if errors[i]:
                    st.error(f"Errors occurred: {errors[i]}")

if __name__ == "__main__":
    main()
