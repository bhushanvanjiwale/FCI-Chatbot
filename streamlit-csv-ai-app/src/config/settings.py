import os
import json

class Settings:
    def __init__(self, config_file='D:\FCI\FCI Chatbot\streamlit-csv-ai-app\config.json'):
        self.config_file = config_file
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        
        with open(self.config_file, 'r') as file:
            return json.load(file)

    @property
    def openai_api_key(self):
        return self.settings.get('OPENAI_API_KEY')

    @property
    def other_setting(self):
        return self.settings.get('OTHER_SETTING', 'default_value')