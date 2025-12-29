import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from imports import *

class Client:
    def __init__(self, apiKey: str):
        self.apiKey = apiKey

    def generateContent(self, prompt: str, system_instruction: Optional[str] = None, model: str = "gemini-2.5-flash-lite") -> Optional[str]:
        """
        Sends a request to Gemini with exponential backoff retries.
        """
        base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        url = f"{base_url}?key={self.apiKey}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Exponential Backoff Implementation
        retries = 5
        for i in range(retries):
            try:
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
                
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