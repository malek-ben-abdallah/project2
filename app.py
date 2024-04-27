#### working code ###

import streamlit as st
import pandas as pd
import openai
from openai import OpenAI
import re
import traceback
import sys


# Set up the OpenAI API key ( each user will have to replace it with their actual key in order to use the application)
# Initialize the client

def generate_code(user_input, df, chat_history, api_key1):
    client= OpenAI(api_key=api_key1)
    
    
    #openai.api_key = api_key1

    
    #Generate Python code to visualize or analyze the provided dataset based on the user's query.

    #Args:
    
        #user_input (str): The user's query for visualizing or analyzing the data.
        
        #df (pandas.DataFrame): The dataset to be used for generating the code.
        
        #chat_history (list): A list of dictionaries containing the chat history between the user and the model.

    #Returns:
    
        #str: The generated text based on the user's query and the provided dataset.
    
        #str: The generated Python code based on the user's query and the provided dataset.
        
        #list: The updated chat history.
        
        #str: Any error message encountered during code execution.
    
    # Generate a description of the dataset
    dataset_description = f"This dataset contains {len(df.columns)} columns: {', '.join(df.columns)}."

    # The column names and data types
    column_info = pd.DataFrame({'column': df.columns, 'data_type': df.dtypes})

    # Get a few sample rows from the dataset
    sample_rows = df.head(5).to_dict(orient='records')

    # Examples of visualizations (you can add a few examples here)
    # ...

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


[always output your chain-of-thought (reasoning and explanations) for the generated visualizations or analyses and what steps you did to get to this result.]

**debug**: The generated code will be sent back to the model for an evaluation of its relevance to the user's query, along with code error checking and debugging. If the code provides errors, the model will check what the error is and correct the code, providing a working and relevant version.

If the user's request is ambiguous or if you need more information to generate an appropriate visualization, or the error cannot be solved by the model, feel free to respond back to the user by asking clarifying questions.
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



########### Main Function ##############

import uuid  # Import the uuid module to generate unique identifiers
def main():

    # the Title of Our Application 
    st.title("Data Analysis Tool")

    # Get the User OpenAI key
    api_key1 = st.text_input("Enter your OpenAI API key:", type="password")

    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset:")
        st.write(df.head())
        chat_history = []
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        ## Create a session for the user to ask multiple questions 
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []



        

        
        user_input = st.text_input("What's your query?")



        if st.button("Submit"):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            generated_text, generated_code, chat_history, error_message = generate_code(user_input, df, st.session_state.chat_history, api_key1)

            if generated_code:
                st.session_state.chat_history.append({"role": "assistant", "content": generated_text})

                # Print the code in the response output ## we can delete them later if we want 
                st.markdown(generated_text)
                # st.code(generated_code, language="python")

                # Plot the visualization directly 
                plot_area = st.empty()
                plot_area.pyplot(exec(generated_code))   

                try:
                    exec(generated_code)
                    st.success("Code ran smoothly.")  # if the code run smoothly 
                except Exception as e:
                    st.error(f"Error executing the generated code: {e}")
                    st.code(traceback.format_exc())

        ## Create a session for the user to ask multiple questions 

  
        ### in this part, we can see the chat history between the user and the model 
        st.subheader('Queries')

        for message in st.session_state.messages:



            with st.container():
                if message["role"] == "user":
                    st.write(f"**Your Query:** {message['content']}")
                elif message["role"] == "assistant":
                    generated_text= message['content']
                    #st.write(f"Assistant: {message['content']}")
                    st.write("**Answer:** ")
                    plot_area = st.empty()
                    plot_area.pyplot(exec(extract_python_code(generated_text)))

    st.subheader('Queries2')
  
    ### Display Chat History
    if st.button("Show Chat History"):
        st.subheader("Chat History")
        st.write(st.session_state.chat_history)  
    
if __name__ == "__main__":
    main()
