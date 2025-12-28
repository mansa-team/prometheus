import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.imports import *

class Client:
    def __init__(self, apiKey: str):
        self.apiKey = apiKey

    def generateContent(self, prompt: str, system_instruction: Optional[str] = None, model: Optional[str] = None,) -> Optional[str]:
        """
        Sends a request to Gemini with exponential backoff retries.
        """
        baseUrl = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        url = f"{self.baseUrl}?key={self.apiKey}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Exponential Backoff Implementation (Rule: 1s, 2s, 4s, 8s, 16s)
        retries = 5
        for i in range(retries):
            try:
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    # Extract text safely from the candidates list
                    return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
                
                # If rate limited (429) or server error (5xx), wait and retry
                if response.status_code in [429, 500, 502, 503, 504]:
                    wait_time = 2 ** i
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Error {response.status_code}: {response.text}")
                    break
                    
            except requests.exceptions.RequestException as e:
                wait_time = 2 ** i
                time.sleep(wait_time)
                
        print("Maximum retries reached. Could not complete the request.")
        return None