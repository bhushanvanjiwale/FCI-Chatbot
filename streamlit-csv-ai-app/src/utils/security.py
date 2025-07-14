def load_api_key():
    import json
    import os
    from utils.logger import app_logger

    # Try multiple possible locations for the config file
    possible_paths = [
        'config.json',  # Root level
        'src/config/settings.json',  # Original path
        '../config.json',  # One level up from src
        'D:/FCI/FCI Chatbot/streamlit-csv-ai-app/config.json'  # Absolute path
    ]
    
    config_file = None
    for path in possible_paths:
        if os.path.exists(path):
            config_file = path
            app_logger.info(f"Found config file at: {path}")
            break
    
    if not config_file:
        app_logger.error(f"Configuration file not found. Searched in: {possible_paths}")
        raise FileNotFoundError("Configuration file not found. Please ensure config.json exists.")

    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        app_logger.info("Configuration file loaded successfully")
    except Exception as e:
        app_logger.error(f"Error reading configuration file: {str(e)}")
        raise

    api_key = config.get('OPENAI_API_KEY')
    
    if not api_key:
        app_logger.error("API key not found in configuration file")
        raise ValueError("API key not found in the configuration file.")

    # Validate API key format
    if not validate_api_key_format(api_key):
        app_logger.error("Invalid API key format detected")
        raise ValueError("Invalid API key format. Please check your OpenAI API key.")

    app_logger.success("API key loaded successfully", show_in_ui=False)
    return api_key

def validate_api_key_format(api_key):
    """Validate the format of the API key"""
    if not isinstance(api_key, str) or len(api_key) == 0:
        return False
    
    # OpenAI API keys should start with 'sk-' and be at least 20 characters
    if not api_key.startswith('sk-'):
        return False
    
    if len(api_key) < 20:
        return False
    
    return True

def validate_api_key(api_key):
    from utils.logger import app_logger
    
    if not validate_api_key_format(api_key):
        app_logger.error("Invalid API key format")
        raise ValueError("Invalid API key. Please provide a valid OpenAI API key.")
    
    app_logger.info("API key validation passed")

def test_api_key(api_key):
    """Test if the API key actually works with OpenAI"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Make a simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        return False, str(e)