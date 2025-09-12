"""
Base Agent Class for AI-Powered Grant Proposal Assistant
"""

import google.generativeai as genai
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from datetime import datetime


class BaseAgent(ABC):
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize the base agent with Gemini Flash 2.0
        """
        # ⚠️ Hardcoded Google API Key (replace with your actual key)
        GOOGLE_API_KEY = "AIzaSyCF6MydBh6Kacv_14cNoZimz7A0oq6iPOs"

        # Configure Gemini API
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.agent_name = self.__class__.__name__
        self.memory_file = "memory/memory_store.json"

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file"""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_memory(self, memory: Dict[str, Any]) -> None:
        """Save memory to JSON file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)

    def _update_memory(self, topic: str, agent_output: Dict[str, Any]) -> None:
        """Update memory with agent output and rationale"""
        memory = self._load_memory()

        if topic not in memory:
            memory[topic] = {
                "versions": [],
                "agents_used": [],
                "created_at": datetime.now().isoformat()
            }

        # Add version tracking
        version_entry = {
            "version": len(memory[topic]["versions"]) + 1,
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "output": agent_output,
            "rationale": agent_output.get("rationale", "No rationale provided")
        }

        memory[topic]["versions"].append(version_entry)

        # Track which agents have been used
        if self.agent_name not in memory[topic]["agents_used"]:
            memory[topic]["agents_used"].append(self.agent_name)

        memory[topic]["last_updated"] = datetime.now().isoformat()

        self._save_memory(memory)

    def _get_topic_memory(self, topic: str) -> Dict[str, Any]:
        """Get memory for specific topic"""
        memory = self._load_memory()
        return memory.get(topic, {})

    def _generate_with_gemini(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate response using Gemini Flash 2.0"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                )
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    @abstractmethod
    def process(self, topic: str, goals: str, funding_agency: str, **kwargs) -> Dict[str, Any]:
        """
        Abstract method that each agent must implement
        """
        pass

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        return f"You are a {self.agent_name} specialized in grant proposal assistance."
