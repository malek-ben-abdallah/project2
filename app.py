import streamlit as st
import pandas as pd
from openai import OpenAI
import openai
import re
import traceback
import sys

def generate_code(user_input, df, chat_history, api_key1):
    client = OpenAI(api_key=api_key1)
    # ... (Existing generate_code function)

def extract_python_code(text):
    # ... (Existing extract_python_code function)

def main():
    st.title("Data Analysis Tool")
    api_key1 = st.text_input("Enter your OpenAI API key:", type="password")

    # Upload CSV file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset:")
        st.write(df.head())
        chat_history = []  # Initialize chat_history here

        # Create a placeholder for the query input and response area
        query_input_placeholder = st.empty()
        response_area_placeholder = st.empty()

        # Function to handle user queries
        def handle_user_query(query, chat_history):
            generated_text, generated_code, chat_history, error_message = generate_code(query, df, chat_history, api_key1)

            if generated_code:
                with response_area_placeholder:
                    st.markdown(generated_text)
                    plot_area = st.empty()

                    try:
                        exec(generated_code)
                        st.success("Code ran smoothly.")
                    except Exception as e:
                        st.error(f"Error executing the generated code: {e}")
                        st.code(traceback.format_exc())

            if error_message:
                with response_area_placeholder:
                    st.error(f"Errors occurred: {error_message}")

            return chat_history  # Return the updated chat_history

        # Initial query
        with query_input_placeholder:
            initial_query = st.text_input("Enter your query:")

        if initial_query:
            chat_history = handle_user_query(initial_query, chat_history)

        # Additional queries
        while True:
            with query_input_placeholder:
                additional_query = st.text_input("Ask another question (or leave blank to exit):")

            if additional_query:
                chat_history = handle_user_query(additional_query, chat_history)
            else:
                break

if __name__ == "__main__":
    main()
