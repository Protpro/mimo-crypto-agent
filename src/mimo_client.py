"""
MiMo API Client - Xiaomi MiMo-V2.5-Pro Integration
Provides async/sync access to MiMo's reasoning capabilities.
"""

import os
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


@dataclass
class MiMoConfig:
    """MiMo API configuration."""
    api_key: str = ""
    base_url: str = "https://api.xiaomimimo.com/v1"
    model: str = "MiMo-V2.5-Pro"
    max_tokens: int = 4096
    temperature: float = 0.7

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("MIMO_API_KEY", "")


class MiMoClient:
    """
    Client for Xiaomi MiMo API.
    
    Uses OpenAI-compatible interface for seamless integration.
    MiMo-V2.5-Pro excels at reasoning, analysis, and code generation.
    """
    
    def __init__(self, config: Optional[MiMoConfig] = None):
        self.config = config or MiMoConfig()
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Send chat completion request to MiMo.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model override (default: MiMo-V2.5-Pro)
            temperature: Temperature override
            max_tokens: Max tokens override
            json_mode: Enable JSON output mode
            
        Returns:
            Assistant's response as string
        """
        kwargs = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def analyze(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Simple analysis interface.
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            
        Returns:
            Analysis result as string
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        return self.chat(messages)
    
    def analyze_json(self, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze and return structured JSON response.
        
        Args:
            prompt: User prompt (should request JSON output)
            system: Optional system prompt
            
        Returns:
            Parsed JSON response
        """
        response = self.analyze(prompt, system, json_mode=True)
        return json.loads(response)
