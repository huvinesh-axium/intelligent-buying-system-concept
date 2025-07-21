import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from openai import OpenAI

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.client = OpenAI(
            base_url="https://api.openai.com/v1",
            api_key=os.environ["OPENAI_API_KEY"],
        )
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def llm_call(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
