"""
Reviewer Simulation Agent for Grant Proposal Review and Feedback
"""

from .base import BaseAgent
from typing import Dict, Any, List
import json
import random


class ReviewerSimulationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.reviewer_types = [
            "Technical Expert",
            "Methodology Specialist",
            "Budget Analyst",
            "Impact Assessor",
            "Program Officer"
        ]

        self.review_criteria = {
            "significance": {
                "weight": 0.25,
                "factors": ["novelty", "potential_impact", "field_advancement"]
            },
            "approach": {
                "weight": 0.25,
                "factors": ["methodology", "feasibility", "timeline"]
            },
            "innovation": {
                "weight": 0.20,
                "factors": ["creativity", "risk_vs_reward", "paradigm_shift"]
            },
            "investigator": {
                "weight": 0.15,
                "factors": ["qualifications", "track_record", "team_expertise"]
            },
            "environment": {
                "weight": 0.15,
                "factors": ["institutional_support", "resources", "collaborations"]
            }
        }

    def get_system_prompt(self) -> str:
        return """You are an expert Grant Reviewer Simulation Agent. Your role is to provide comprehensive, 
        constructive feedback on grant proposals from multiple reviewer perspectives, simulating the actual 
        grant review process.

        You should evaluate proposals based on:
        - Scientific significance and innovation
        - Methodological rigor and feasibility
        - Budget appropriateness and justification
        - Team qualifications and institutional support
        - Potential impact and broader implications

        Provide detailed, actionable feedback that helps improve proposal quality while maintaining 
        the high standards of competitive funding review processes."""

    def process(self, topic: str, goals: str, funding_agency: str, **kwargs) -> Dict[str, Any]:
        """
        Simulate comprehensive grant proposal review
        """
        # Get all previous work on this topic
        topic_memory = self._get_topic_memory(topic)

        # Extract proposal components from memory
        outline_data = self._extract_component_data(topic_memory, "OutlineDesignerAgent")
        budget_data = self._extract_component_data(topic_memory, "BudgetEstimatorAgent")

        # Generate multiple reviewer perspectives
        reviews = []
        for reviewer_type in self.reviewer_types:
            review = self._simulate_single_reviewer(
                reviewer_type, topic, goals, funding_agency,
                outline_data, budget_data
            )
            reviews.append(review)

        # Generate overall assessment
        overall_assessment = self._generate_overall_assessment(reviews, topic_memory)

        # Create improvement recommendations
        recommendations = self._generate_improvement_recommendations(reviews)

        result = {
            "agent": self.agent_name,
            "individual_reviews": reviews,
            "overall_assessment": overall_assessment,
            "improvement_recommendations": recommendations,
            "scoring_summary": self._calculate_scoring_summary(reviews),
            "rationale": f"Simulated multi-perspective review of {topic} proposal for {funding_agency}. "
                         f"Evaluated based on standard review criteria with focus on {goals[:100]}...",
            "next_steps": self._suggest_next_steps(overall_assessment)
        }

        # Update memory
        self._update_memory(topic, result)

        return result

    def _simulate_single_reviewer(self, reviewer_type: str, topic: str, goals: str,
                                  funding_agency: str, outline_data: Dict, budget_data: Dict) -> Dict[str, Any]:
        """Simulate review from a single reviewer perspective"""

        prompt = f"""
        {self.get_system_prompt()}

        You are a {reviewer_type} reviewing a grant proposal for {funding_agency}.

        Proposal Summary:
        - Topic: {topic}
        - Goals: {goals}
        - Outline: {json.dumps(outline_data, indent=2)}
        - Budget: {json.dumps(budget_data, indent=2)}

        As a {reviewer_type}, provide a detailed review focusing on your area of expertise:

        1. STRENGTHS (3-5 key points)
        2. WEAKNESSES (3-5 key points)  
        3. SPECIFIC CONCERNS (detailed issues)
        4. SUGGESTIONS FOR IMPROVEMENT (actionable recommendations)
        5. SCORING (1-5 scale for each criterion: significance, approach, innovation, investigator, environment)
        6. OVERALL RECOMMENDATION (Fund, Revise & Resubmit, or Decline with reasoning)

        Focus on aspects most relevant to your reviewer type:
        - Technical Expert: methodology, feasibility, technical soundness
        - Methodology Specialist: research design, data analysis, validity
        - Budget Analyst: cost-effectiveness, budget justification, resource allocation
        - Impact Assessor: significance, broader impacts, societal benefits
        - Program Officer: alignment with agency priorities, strategic value

        Provide constructive, specific feedback that would help improve the proposal.
        """

        response = self._generate_with_gemini(prompt, max_tokens=2500)

        # Extract scoring
        scores = self._extract_scores_from_review(response)

        return {
            "reviewer_type": reviewer_type,
            "review_text": response,
            "scores": scores,
            "recommendation": self._extract_recommendation(response),
            "key_concerns": self._extract_key_concerns(response)
        }

    def _extract_component_data(self, topic_memory: Dict, agent_name: str) -> Dict[str, Any]:
        """Extract data from specific agent in memory"""
        versions = topic_memory.get('versions', [])
        for version in reversed(versions):  # Get most recent first
            if version.get('agent') == agent_name:
                return version.get('output', {})
        return {}

    def _extract_scores_from_review(self, review_text: str) -> Dict[str, float]:
        """Extract numerical scores from review text"""
        scores = {}
        for criterion in self.review_criteria.keys():
            # Look for scoring patterns in the text
            import re
            pattern = f"{criterion}.*?([1-5](?:\.\d)?)"
            match = re.search(pattern, review_text, re.IGNORECASE)
            if match:
                try:
                    scores[criterion] = float(match.group(1))
                except ValueError:
                    scores[criterion] = 3.0  # Default middle score
            else:
                scores[criterion] = 3.0  # Default if not found

        return scores

    def _extract_recommendation(self, review_text: str) -> str:
        """Extract overall recommendation from review"""
        text_lower = review_text.lower()
        if "fund" in text_lower and "decline" not in text_lower:
            return "Fund"
        elif "revise" in text_lower or "resubmit" in text_lower:
            return "Revise & Resubmit"
        elif "decline" in text_lower:
            return "Decline"
        else:
            return "Conditional"

    def _extract_key_concerns(self, review_text: str) -> List[str]:
        """Extract key concerns from review text"""
        concerns = []
        lines = review_text.split('\n')

        in_concerns_section = False
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['weakness', 'concern', 'issue', 'problem']):
                in_concerns_section = True
                continue
            elif in_concerns_section and line and not line.startswith('*'):
                concerns.append(line)
                if len(concerns) >= 5:  # Limit to top 5 concerns
                    break

        return concerns

    def _generate_overall_assessment(self, reviews: List[Dict], topic_memory: Dict) -> Dict[str, Any]:
        """Generate overall assessment from all reviews"""

        # Calculate weighted scores
        total_scores = {criterion: 0 for criterion in self.review_criteria.keys()}
        total_weight = 0

        for review in reviews:
            for criterion, score in review.get('scores', {}).items():
                weight = self.review_criteria.get(criterion, {}).get('weight', 0.2)
                total_scores[criterion] += score * weight
                total_weight += weight

        # Normalize scores
        avg_scores = {k: v / (len(reviews)) for k, v in total_scores.items()}
        overall_score = sum(avg_scores.values()) / len(avg_scores)

        # Determine consensus recommendation
        recommendations = [r.get('recommendation', 'Conditional') for r in reviews]
        consensus = max(set(recommendations), key=recommendations.count)

        return {
            "overall_score": round(overall_score, 2),
            "criterion_scores": {k: round(v, 2) for k, v in avg_scores.items()},
            "consensus_recommendation": consensus,
            "review_consensus": f"{recommendations.count(consensus)}/{len(reviews)} reviewers",
            "strengths_consensus": self._identify_common_themes(reviews, "strengths"),
            "concerns_consensus": self._identify_common_themes(reviews, "concerns")
        }

    def _identify_common_themes(self, reviews: List[Dict], theme_type: str) -> List[str]:
        """Identify common themes across reviews"""
        # This is a simplified implementation
        # In production, you'd use NLP techniques for better theme extraction
        all_text = " ".join([review.get('review_text', '') for review in reviews])

        common_themes = []
        if theme_type == "strengths":
            keywords = ["strong", "excellent", "innovative", "comprehensive", "well-designed"]
        else:  # concerns
            keywords = ["concern", "weakness", "unclear", "insufficient", "problematic"]

        for keyword in keywords:
            if all_text.lower().count(keyword) >= 2:  # Mentioned by at least 2 reviewers
                common_themes.append(f"Multiple reviewers noted {keyword} aspects")

        return common_themes[:5]

    def _generate_improvement_recommendations(self, reviews: List[Dict]) -> List[str]:
        """Generate prioritized improvement recommendations"""

        # Collect all suggestions from reviews
        all_suggestions = []
        for review in reviews:
            text = review.get('review_text', '')
            lines = text.split('\n')

            for line in lines:
                if any(keyword in line.lower() for keyword in ['suggest', 'recommend', 'should', 'consider']):
                    if len(line.strip()) > 20:  # Filter out short fragments
                        all_suggestions.append(line.strip())

        # Prioritize suggestions (simplified)
        prioritized = list(set(all_suggestions))[:10]  # Remove duplicates, limit to 10

        return prioritized

    def _calculate_scoring_summary(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive scoring summary"""

        # Collect all scores
        all_scores = {}
        for criterion in self.review_criteria.keys():
            scores = [review.get('scores', {}).get(criterion, 3.0) for review in reviews]
            all_scores[criterion] = {
                "average": round(sum(scores) / len(scores), 2),
                "range": f"{min(scores):.1f} - {max(scores):.1f}",
                "std_dev": round(self._calculate_std_dev(scores), 2)
            }

        # Overall statistics
        all_individual_scores = []
        for review in reviews:
            all_individual_scores.extend(review.get('scores', {}).values())

        return {
            "criterion_details": all_scores,
            "overall_average": round(sum(all_individual_scores) / len(all_individual_scores), 2),
            "score_consistency": "High" if max([s["std_dev"] for s in all_scores.values()]) < 0.5 else "Moderate",
            "funding_probability": self._estimate_funding_probability(all_scores)
        }

    def _calculate_std_dev(self, scores: List[float]) -> float:
        """Calculate standard deviation of scores"""
        if len(scores) <= 1:
            return 0.0

        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance ** 0.5

    def _estimate_funding_probability(self, all_scores: Dict) -> str:
        """Estimate funding probability based on scores"""
        avg_score = sum([s["average"] for s in all_scores.values()]) / len(all_scores)

        if avg_score >= 4.0:
            return "High (>70%)"
        elif avg_score >= 3.5:
            return "Moderate (40-70%)"
        elif avg_score >= 3.0:
            return "Low (10-40%)"
        else:
            return "Very Low (<10%)"

    def _suggest_next_steps(self, overall_assessment: Dict) -> List[str]:
        """Suggest next steps based on assessment"""

        next_steps = []
        recommendation = overall_assessment.get("consensus_recommendation", "Conditional")
        score = overall_assessment.get("overall_score", 3.0)

        if recommendation == "Fund" or score >= 4.0:
            next_steps.extend([
                "Prepare final proposal submission",
                "Gather required institutional commitments",
                "Finalize team member confirmations",
                "Complete budget verification"
            ])
        elif recommendation == "Revise & Resubmit" or score >= 3.0:
            next_steps.extend([
                "Address major reviewer concerns systematically",
                "Strengthen methodology section based on feedback",
                "Revise budget based on reviewer suggestions",
                "Consider additional pilot data or preliminary results",
                "Seek additional collaborators if recommended"
            ])
        else:
            next_steps.extend([
                "Major revision of project scope and approach needed",
                "Consider alternative funding sources",
                "Gather additional preliminary data",
                "Strengthen team qualifications",
                "Redesign methodology based on feedback"
            ])

        # Add general next steps
        next_steps.extend([
            "Schedule team meeting to discuss feedback",
            "Create revision timeline and task assignments",
            "Consider seeking additional external review"
        ])

        return next_steps

    def generate_panel_summary(self, topic: str) -> Dict[str, Any]:
        """Generate a comprehensive panel summary report"""

        topic_memory = self._get_topic_memory(topic)
        latest_review = None

        # Find the most recent review
        for version in reversed(topic_memory.get('versions', [])):
            if version.get('agent') == self.agent_name:
                latest_review = version.get('output', {})
                break

        if not latest_review:
            return {"error": "No reviews found for this topic"}

        prompt = f"""
        Generate a comprehensive panel summary report based on the following review data:

        Reviews: {json.dumps(latest_review.get('individual_reviews', []), indent=2)}
        Overall Assessment: {json.dumps(latest_review.get('overall_assessment', {}), indent=2)}

        Create a professional panel summary that includes:

        1. EXECUTIVE SUMMARY
           - Overall recommendation
           - Key strengths and weaknesses
           - Funding recommendation rationale

        2. DETAILED ASSESSMENT
           - Significance and Innovation
           - Approach and Methodology  
           - Team and Environment
           - Budget and Resources

        3. REVIEWER CONSENSUS
           - Areas of agreement
           - Areas of disagreement
           - Critical issues raised

        4. RECOMMENDATIONS FOR IMPROVEMENT
           - High priority changes
           - Moderate priority suggestions
           - Optional enhancements

        Format as a professional grant review panel summary.
        """

        response = self._generate_with_gemini(prompt, max_tokens=3000)

        result = {
            "agent": self.agent_name,
            "panel_summary": response,
            "summary_date": topic_memory.get('last_updated'),
            "rationale": f"Generated comprehensive panel summary for {topic}",
            "report_type": "Final Panel Review Summary"
        }

        self._update_memory(f"{topic}_panel_summary", result)
        return result