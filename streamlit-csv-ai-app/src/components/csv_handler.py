import pandas as pd
import streamlit as st
from utils.logger import app_logger

def load_csv(uploaded_file):
    """
    Load CSV file from Streamlit file uploader
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pandas.DataFrame: Loaded CSV data
    """
    app_logger.info(f"Attempting to load CSV file: {uploaded_file.name}")
    app_logger.debug(f"File size: {uploaded_file.size} bytes")
    
    try:
        data = pd.read_csv(uploaded_file)
        app_logger.success(f"CSV file loaded successfully - Shape: {data.shape}")
        app_logger.debug(f"Columns: {list(data.columns)}")
        return data
    except Exception as e:
        app_logger.error(f"Error loading CSV file: {str(e)}")
        st.error(f"Error loading CSV file: {str(e)}")
        return None

def summarize_data(data):
    """
    Generate summary statistics for the DataFrame
    
    Args:
        data: pandas.DataFrame
        
    Returns:
        dict: Summary information about the data
    """
    app_logger.info("Generating data summary...")
    
    if data is None or data.empty:
        app_logger.warning("No data available for summary")
        return {"error": "No data available"}
    
    try:
        summary = {
            "shape": data.shape,
            "columns": list(data.columns),
            "data_types": data.dtypes.to_dict(),
            "missing_values": data.isnull().sum().to_dict(),
            "numeric_summary": data.describe().to_dict() if len(data.select_dtypes(include=['number']).columns) > 0 else "No numeric columns"
        }
        
        app_logger.success(f"Data summary generated - {data.shape[0]} rows, {data.shape[1]} columns")
        return summary
    except Exception as e:
        app_logger.error(f"Error generating data summary: {str(e)}")
        return {"error": f"Error generating summary: {str(e)}"}