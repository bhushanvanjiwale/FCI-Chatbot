import requests
import json
from openai import OpenAI
from utils.security import load_api_key
from utils.logger import app_logger

class ModelManager:
    def __init__(self):
        self.openai_client = None
        self.ollama_url = "http://localhost:11434/api/generate"
        self.current_model = "openai"
        
    def initialize_openai(self):
        try:
            api_key = load_api_key()
            self.openai_client = OpenAI(api_key=api_key)
            return True
        except Exception as e:
            app_logger.error(f"Failed to initialize OpenAI: {str(e)}", show_in_ui=False)
            return False
    
    def test_ollama_connection(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt, model_type="openai"):
        if model_type == "openai":
            return self._generate_openai_response(prompt)
        elif model_type == "ollama":
            return self._generate_ollama_response(prompt)
    
    def _generate_openai_response(self, prompt):
        try:
            if not self.openai_client:
                if not self.initialize_openai():
                    return None
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            app_logger.error(f"OpenAI API error: {str(e)}", show_in_ui=False)
            return None
    
    def _generate_ollama_response(self, prompt):
        try:
            payload = {
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return None
        except Exception as e:
            app_logger.error(f"Ollama API error: {str(e)}", show_in_ui=False)
            return None
