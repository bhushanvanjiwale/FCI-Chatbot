import streamlit as st
from utils.logger import app_logger

def handle_api_error(error):
    message = f"An error occurred while communicating with the API: {str(error)}. Please try again later."
    app_logger.error(f"API Error: {str(error)}")
    st.error(message)
    return message

def handle_invalid_prompt(prompt):
    message = f"The prompt provided is invalid: '{prompt}'. Please ensure it is clear and specific."
    app_logger.warning(f"Invalid prompt: {prompt}")
    st.error(message)
    return message

def handle_execution_error(error):
    message = f"An error occurred during code execution: {str(error)}. Please check your input and try again."
    app_logger.error(f"Execution Error: {str(error)}")
    st.error(message)
    return message

def handle_file_error(error):
    message = f"An error occurred while processing the file: {str(error)}. Please ensure the file is in the correct format."
    app_logger.error(f"File Error: {str(error)}")
    st.error(message)
    return message

def handle_error(error):
    message = f"An error occurred: {str(error)}. Please try again."
    app_logger.error(f"General Error: {str(error)}")
    st.error(message)
    return message