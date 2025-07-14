import logging
import streamlit as st
from datetime import datetime
import os

class AppLogger:
    def __init__(self, name="CSV_AI_App", log_file="app.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # File handler
        file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message, show_in_ui=False):
        self.logger.info(message)
        if show_in_ui:
            st.info(f"ℹ️ {message}")
    
    def success(self, message, show_in_ui=False):
        self.logger.info(f"SUCCESS: {message}")
        if show_in_ui:
            st.success(f"✅ {message}")
    
    def warning(self, message, show_in_ui=False):
        self.logger.warning(message)
        if show_in_ui:
            st.warning(f"⚠️ {message}")
    
    def error(self, message, show_in_ui=False):
        self.logger.error(message)
        if show_in_ui:
            st.error(f"❌ {message}")
    
    def debug(self, message, show_in_ui=False):
        self.logger.debug(message)
        if show_in_ui:
            st.write(f"🐛 DEBUG: {message}")

# Global logger instance
app_logger = AppLogger()
