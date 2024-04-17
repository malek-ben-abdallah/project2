import streamlit as st
import pandas as pd
import openai
import re
import traceback
import sys

# Set up OpenAI API key (replace with your actual key)

# Initialize the client

def main():
    st.title("Data Analysis Tool")

    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset:")
        st.write(df.head())

        # Get user query
        user_query = st.text_input("Enter your query:")

        if user_query:
            chat_history = []
            generated_text, generated_code, chat_history, error_message = generate_code(user_query, df, chat_history)

            if generated_code:
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

if __name__ == "__main__":
    main()
