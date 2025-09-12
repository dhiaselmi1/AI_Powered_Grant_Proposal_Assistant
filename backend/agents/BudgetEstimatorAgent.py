"""
Budget Estimator Agent for Grant Proposal Financial Planning
"""

from .base import BaseAgent
from typing import Dict, Any, List
import json
import re


class BudgetEstimatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.budget_categories = {
            "personnel": ["salaries", "benefits", "consultants", "students"],
            "equipment": ["instruments", "computers", "software", "materials"],
            "travel": ["conferences", "fieldwork", "collaborations"],
            "supplies": ["lab supplies", "consumables", "books"],
            "indirect": ["overhead", "administrative", "facilities"],
            "other": ["publication", "dissemination", "training"]
        }

    def get_system_prompt(self) -> str:
        return """You are an expert Budget Estimator for grant proposals. Your role is to create realistic, 
        well-justified budget estimates based on research projects, timelines, and funding agency guidelines.

        You should consider:
        - Personnel costs (salaries, benefits, effort percentages)
        - Equipment and supplies needed
        - Travel requirements
        - Indirect costs and overhead rates
        - Funding agency specific limitations
        - Industry-standard rates and costs
        - Multi-year budget projections

        Provide detailed budget breakdowns with clear justifications for each line item."""

    def process(self, topic: str, goals: str, funding_agency: str, **kwargs) -> Dict[str, Any]:
        """
        Generate comprehensive budget estimate for grant proposal
        """
        # Extract additional parameters
        duration = kwargs.get('duration', '3 years')
        team_size = kwargs.get('team_size', 'medium (3-5 people)')
        project_type = kwargs.get('project_type', 'research')

        # Get context from previous agents
        topic_memory = self._get_topic_memory(topic)

        prompt = f"""
        {self.get_system_prompt()}

        Create a detailed budget estimate for:

        Research Topic: {topic}
        Project Goals: {goals}
        Funding Agency: {funding_agency}
        Project Duration: {duration}
        Team Size: {team_size}
        Project Type: {project_type}

        Previous proposal work: {json.dumps(topic_memory.get('versions', []), indent=2)}

        Please provide a comprehensive budget that includes:

        1. PERSONNEL COSTS
           - Principal Investigator (effort %, salary, benefits)
           - Co-Investigators and research staff
           - Graduate students and postdocs
           - Administrative support

        2. EQUIPMENT AND SUPPLIES
           - Major equipment (>$5,000)
           - Minor equipment and supplies
           - Software licenses
           - Computing resources

        3. TRAVEL
           - Conference presentations
           - Fieldwork or data collection
           - Collaboration visits
           - Training workshops

        4. OTHER DIRECT COSTS
           - Publication fees
           - Participant incentives
           - Communication and dissemination
           - Subcontracts or consultants

        5. INDIRECT COSTS
           - Overhead rate (typical for institution type)
           - Facilities and administrative costs

        For each category, provide:
        - Line item descriptions
        - Quantity and unit costs
        - Year-by-year breakdown
        - Justification for each major expense
        - Total costs per category

        Consider {funding_agency} specific guidelines and typical funding levels.

        Format as a detailed budget table with clear totals and explanations.
        """

        response = self._generate_with_gemini(prompt, max_tokens=4000)

        # Process and structure the budget
        budget_data = self._parse_budget_response(response)

        # Calculate totals and validate
        budget_summary = self._calculate_budget_summary(budget_data)

        result = {
            "agent": self.agent_name,
            "budget_details": budget_data,
            "budget_summary": budget_summary,
            "funding_recommendations": self._generate_funding_recommendations(funding_agency, budget_summary),
            "rationale": f"Generated comprehensive budget for {duration} {project_type} project on {topic}. "
                         f"Considered team size ({team_size}) and {funding_agency} guidelines. "
                         f"Total estimated cost: ${budget_summary.get('total_cost', 'TBD')}",
            "cost_breakdown_chart": self._create_cost_breakdown(budget_summary)
        }

        # Update memory
        self._update_memory(topic, result)

        return result

    def _parse_budget_response(self, response: str) -> Dict[str, Any]:
        """Parse the budget response into structured data"""
        budget_data = {
            "personnel": [],
            "equipment": [],
            "travel": [],
            "supplies": [],
            "indirect": [],
            "other": []
        }

        # Extract dollar amounts
        dollar_amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', response)

        # Simple parsing - in production, this would be more sophisticated
        lines = response.split('\n')
        current_category = None

        for line in lines:
            line = line.strip()
            if any(cat in line.lower() for cat in self.budget_categories.keys()):
                for cat in self.budget_categories.keys():
                    if cat in line.lower():
                        current_category = cat
                        break

            # Extract line items with costs
            if '$' in line and current_category:
                budget_data[current_category].append(line)

        return budget_data

    def _calculate_budget_summary(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate budget summary and totals"""
        summary = {}
        total_cost = 0

        for category, items in budget_data.items():
            category_total = 0
            # Extract dollar amounts from each item
            for item in items:
                amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', item)
                for amount in amounts:
                    try:
                        value = float(amount.replace('$', '').replace(',', ''))
                        category_total += value
                    except ValueError:
                        continue

            summary[f"{category}_total"] = category_total
            total_cost += category_total

        summary['total_cost'] = total_cost
        summary['currency'] = 'USD'

        return summary

    def _generate_funding_recommendations(self, agency: str, budget_summary: Dict[str, Any]) -> List[str]:
        """Generate funding strategy recommendations"""
        recommendations = []
        total = budget_summary.get('total_cost', 0)

        if total > 1000000:
            recommendations.append(f"Consider multi-year or collaborative approach for large budget (${total:,.2f})")

        recommendations.extend([
            f"Align budget categories with {agency} priorities",
            "Include detailed cost-share information if required",
            "Consider equipment sharing to reduce costs",
            "Plan for potential budget cuts (10-15% contingency)"
        ])

        return recommendations

    def _create_cost_breakdown(self, budget_summary: Dict[str, Any]) -> Dict[str, float]:
        """Create cost breakdown for visualization"""
        breakdown = {}
        total = budget_summary.get('total_cost', 1)

        for key, value in budget_summary.items():
            if key.endswith('_total') and isinstance(value, (int, float)):
                category = key.replace('_total', '').title()
                percentage = (value / total * 100) if total > 0 else 0
                breakdown[category] = round(percentage, 2)

        return breakdown

    def adjust_budget(self, topic: str, target_amount: float, constraints: str = "") -> Dict[str, Any]:
        """Adjust budget to meet target funding amount"""
        topic_memory = self._get_topic_memory(topic)
        latest_budget = topic_memory.get('versions', [])[-1] if topic_memory.get('versions') else {}

        prompt = f"""
        Adjust the following budget to meet a target amount of ${target_amount:,.2f}:

        Original Budget: {json.dumps(latest_budget.get('output', {}), indent=2)}

        Constraints: {constraints}

        Provide specific recommendations for:
        1. Which categories to reduce/increase
        2. How to maintain project quality
        3. Alternative funding sources
        4. Phased implementation options
        """

        response = self._generate_with_gemini(prompt, max_tokens=2000)

        result = {
            "agent": self.agent_name,
            "adjusted_budget": response,
            "target_amount": target_amount,
            "rationale": f"Adjusted budget to meet ${target_amount:,.2f} target with constraints: {constraints}",
            "adjustment_strategy": "Cost optimization while maintaining project integrity"
        }

        self._update_memory(f"{topic}_adjusted", result)
        return result