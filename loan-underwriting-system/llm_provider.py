import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain.schema import HumanMessage, SystemMessage
import json

load_dotenv()

class LLMProvider:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        
        if self.provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            genai.configure(api_key=api_key)
            
            # Use the new Gemini model names
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",  
                temperature=0.7,
                google_api_key=api_key,
                convert_system_message_to_human=True  
            )
        elif self.provider == "ollama":
            self.llm = Ollama(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "gemma3:12b")
            )
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from LLM"""
        try:
            if self.provider == "gemini":
                # Combine system prompt with user prompt for Gemini
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                else:
                    full_prompt = prompt
                
                messages = [HumanMessage(content=full_prompt)]
                response = await self.llm.ainvoke(messages)
                return response.content
            else:
                # For Ollama
                if system_prompt:
                    prompt = f"{system_prompt}\n\n{prompt}"
                response = await self.llm.ainvoke(prompt)
                return response
        except Exception as e:
            print(f"LLM Error: {str(e)}")
            # Provide a fallback response
            return self._get_fallback_response(prompt, str(e))
    
    async def analyze_json(self, data: Dict, analysis_prompt: str) -> str:
        """Analyze JSON data with LLM"""
        prompt = f"{analysis_prompt}\n\nData:\n{json.dumps(data, indent=2)}"
        return await self.generate(prompt)
    
    def _get_fallback_response(self, prompt: str, error: str) -> str:
        """Provide fallback response when LLM fails"""
        if "loan" in prompt.lower() and "documents" in prompt.lower():
            # Fallback for document requirement analysis
            return """Based on the loan application:
- For loans above ₹10 lakhs: GST, ITR, and Bank Statement required
- For loans ₹5-10 lakhs: ITR and Bank Statement required  
- For loans below ₹5 lakhs: ITR required
Additional documents may be needed based on business type."""
        
        elif "decision" in prompt.lower() or "risk" in prompt.lower():
            # Fallback for loan decision
            return """Unable to make automated decision due to LLM error. 
Manual review required. Please evaluate:
- Income to loan ratio
- Business stability
- Tax compliance
- Credit history"""
        
        else:
            return f"Analysis unavailable due to error: {error}. Manual review required."