import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

genai_configured = False
model = None

if API_KEY and API_KEY != "your_api_key_here":
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        genai_configured = True
    except Exception as e:
        print(f"GenAI configuration failed: {e}")

from typing import Optional

def analyze_offer_with_genai(text: str) -> Optional[str]:
    """
    Analyzes the offer text using GenAI to provide a detailed explanation.
    Returns the explanation string, or None if GenAI is not configured.
    """
    if not genai_configured or model is None:
        return None
    try:
        prompt = f"""
        Analyze the following text which might be a job offer or scholarship offer. 
        Determine if it is likely a Genuine Offer or a Fake/Scam Offer, and explain your reasoning in 2 to 4 concise sentences. 
        Point out any red flags if it's a scam (like asking for money, false urgency, generic greetings, or guaranteed approval).
        
        Text:
        "{text}"
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"GenAI inference failed: {e}")
        return "Warning: AI analysis encountered an error."
