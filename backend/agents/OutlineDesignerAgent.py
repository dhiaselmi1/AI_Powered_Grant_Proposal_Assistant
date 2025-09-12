"""
Outline Designer Agent for Grant Proposal Structure
"""

from .base import BaseAgent
from typing import Dict, Any
import json


class OutlineDesignerAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def get_system_prompt(self) -> str:
        return """You are an expert Grant Proposal Outline Designer. Your role is to create comprehensive, 
        well-structured outlines for grant proposals based on the research topic, goals, and funding agency requirements.

        You should consider:
        - Standard grant proposal sections
        - Funding agency specific requirements
        - Research methodology appropriate for the topic
        - Timeline and deliverables
        - Impact and evaluation metrics

        Provide detailed section descriptions and suggested content for each part of the proposal."""

    def process(self, topic: str, goals: str, funding_agency: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a comprehensive grant proposal outline
        """
        # Get previous memory for context
        topic_memory = self._get_topic_memory(topic)

        # Create detailed prompt
        prompt = f"""
        {self.get_system_prompt()}

        Create a detailed grant proposal outline for:

        Research Topic: {topic}
        Project Goals: {goals}
        Funding Agency: {funding_agency}

        Previous work on this topic: {json.dumps(topic_memory.get('versions', []), indent=2)}

        Please provide a comprehensive outline that includes:

        1. Executive Summary structure
        2. Problem Statement and Significance
        3. Literature Review approach
        4. Research Methodology
        5. Project Timeline and Milestones
        6. Budget Categories (high-level)
        7. Expected Outcomes and Impact
        8. Evaluation and Assessment Plan
        9. Sustainability and Future Plans
        10. Team Qualifications (structure)

        For each section, provide:
        - Purpose and key objectives
        - Suggested content and approach
        - Approximate length/word count
        - Critical elements to include
        - Common pitfalls to avoid

        Also provide specific recommendations based on the funding agency's typical preferences and requirements.

        Format your response as a structured JSON with clear sections and detailed descriptions.
        """

        # Generate response
        response = self._generate_with_gemini(prompt, max_tokens=3000)

        # Process and structure the output
        try:
            # Try to parse if it's already JSON
            if response.strip().startswith('{'):
                outline_data = json.loads(response)
            else:
                # Structure the response if it's not JSON
                outline_data = {
                    "outline_content": response,
                    "sections": self._extract_sections(response),
                    "agency_specific_notes": self._extract_agency_notes(response, funding_agency)
                }
        except json.JSONDecodeError:
            outline_data = {
                "outline_content": response,
                "sections": [],
                "parsing_note": "Response provided as text due to JSON parsing issues"
            }

        # Add metadata and rationale
        result = {
            "agent": self.agent_name,
            "outline": outline_data,
            "rationale": f"Created comprehensive outline for {topic} targeting {funding_agency}. "
                         f"Considered project goals: {goals[:100]}... "
                         f"and incorporated best practices for grant proposals.",
            "recommendations": [
                f"Tailor language and emphasis to {funding_agency} priorities",
                "Include specific, measurable outcomes",
                "Develop detailed timeline with realistic milestones",
                "Ensure budget aligns with proposed activities"
            ]
        }

        # Update memory
        self._update_memory(topic, result)

        return result

    def _extract_sections(self, response: str) -> list:
        """Extract main sections from the response"""
        sections = []
        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in
                   ['summary', 'statement', 'methodology', 'timeline', 'budget', 'outcomes']):
                if line.endswith(':') or any(char.isdigit() for char in line[:3]):
                    current_section = line
                    sections.append(current_section)

        return sections[:10]  # Return top 10 identified sections

    def _extract_agency_notes(self, response: str, agency: str) -> list:
        """Extract agency-specific recommendations"""
        notes = []
        lines = response.split('\n')

        for line in lines:
            if agency.lower() in line.lower() or any(
                    keyword in line.lower() for keyword in ['agency', 'funder', 'specific']):
                notes.append(line.strip())

        return notes[:5]  # Return top 5 agency-specific notes

    def refine_outline(self, topic: str, feedback: str) -> Dict[str, Any]:
        """Refine outline based on feedback"""
        topic_memory = self._get_topic_memory(topic)
        latest_version = topic_memory.get('versions', [])[-1] if topic_memory.get('versions') else {}

        prompt = f"""
        {self.get_system_prompt()}

        Refine the following grant proposal outline based on the feedback provided:

        Original Outline: {json.dumps(latest_version.get('output', {}), indent=2)}

        Feedback to Address: {feedback}

        Please provide an improved version that addresses the feedback while maintaining the overall structure and quality.
        """

        response = self._generate_with_gemini(prompt, max_tokens=3000)

        result = {
            "agent": self.agent_name,
            "refined_outline": response,
            "rationale": f"Refined outline based on feedback: {feedback[:100]}...",
            "changes_made": "Addressed specific feedback points while maintaining proposal structure"
        }

        self._update_memory(f"{topic}_refined", result)
        return result