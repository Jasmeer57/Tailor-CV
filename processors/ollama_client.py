"""
Ollama Client Module
Handles communication with local Ollama LLM server
"""

import requests
from typing import List, Dict, Optional


class OllamaClient:
    """Client for interacting with local Ollama LLM"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"

    def check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(self.base_url, timeout=2)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []

    def generate(self, model: str, prompt: str, temperature: float = 0.7, 
                 system_prompt: str = None) -> Optional[str]:
        """
        Generate text using Ollama

        Args:
            model: Model name (e.g., 'llama3', 'mistral')
            prompt: User prompt
            temperature: Creativity level (0.0-1.0)
            system_prompt: Optional system prompt for context

        Returns:
            Generated text or None on error
        """
        try:
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }

            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Generation error: {e}")
            return None

    def stream_generate(self, model: str, prompt: str, temperature: float = 0.7,
                       system_prompt: str = None):
        """
        Stream text generation (for real-time output)

        Args:
            model: Model name
            prompt: User prompt
            temperature: Creativity level
            system_prompt: Optional system prompt

        Yields:
            Text chunks as they are generated
        """
        try:
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature
                }
            }

            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                stream=True,
                timeout=120
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if 'message' in data:
                            yield data['message'].get('content', '')

        except Exception as e:
            print(f"Streaming error: {e}")
            yield None


if __name__ == "__main__":
    # Test Ollama connection
    client = OllamaClient()

    print("Testing Ollama connection...")
    if client.check_connection():
        print("✅ Ollama is running")

        models = client.list_models()
        print(f"Available models: {models}")

        if models:
            test_response = client.generate(
                model=models[0],
                prompt="Say hello in one sentence.",
                temperature=0.7
            )
            print(f"Test response: {test_response}")
    else:
        print("❌ Ollama is not running")
