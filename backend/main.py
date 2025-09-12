"""
FastAPI Backend for AI-Powered Grant Proposal Assistant
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime

# Import agents
from agents.base import BaseAgent
from agents.OutlineDesignerAgent import OutlineDesignerAgent
from agents.BudgetEstimatorAgent import BudgetEstimatorAgent
from agents.ReviewerSimulationAgent import ReviewerSimulationAgent

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Grant Proposal Assistant",
    description="Comprehensive grant proposal development with AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
outline_agent = OutlineDesignerAgent()
budget_agent = BudgetEstimatorAgent()
reviewer_agent = ReviewerSimulationAgent()


# Pydantic models for request/response
class ProposalRequest(BaseModel):
    topic: str
    goals: str
    funding_agency: str
    duration: Optional[str] = "3 years"
    team_size: Optional[str] = "medium (3-5 people)"
    project_type: Optional[str] = "research"
    budget_target: Optional[float] = None


class OutlineRequest(BaseModel):
    topic: str
    goals: str
    funding_agency: str


class BudgetRequest(BaseModel):
    topic: str
    goals: str
    funding_agency: str
    duration: Optional[str] = "3 years"
    team_size: Optional[str] = "medium (3-5 people)"
    project_type: Optional[str] = "research"


class ReviewRequest(BaseModel):
    topic: str
    goals: str
    funding_agency: str


class RefineRequest(BaseModel):
    topic: str
    feedback: str
    agent_type: str  # "outline", "budget", or "review"


class BudgetAdjustmentRequest(BaseModel):
    topic: str
    target_amount: float
    constraints: Optional[str] = ""


# Memory management
class MemoryManager:
    @staticmethod
    def get_all_topics() -> List[str]:
        """Get all topics from memory"""
        try:
            with open("memory/memory_store.json", 'r') as f:
                memory = json.load(f)
            return list(memory.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def get_topic_summary(topic: str) -> Dict[str, Any]:
        """Get summary of work done on a topic"""
        try:
            with open("memory/memory_store.json", 'r') as f:
                memory = json.load(f)

            if topic not in memory:
                return {"error": "Topic not found"}

            topic_data = memory[topic]
            return {
                "topic": topic,
                "created_at": topic_data.get("created_at"),
                "last_updated": topic_data.get("last_updated"),
                "versions": len(topic_data.get("versions", [])),
                "agents_used": topic_data.get("agents_used", []),
                "latest_version": topic_data.get("versions", [])[-1] if topic_data.get("versions") else None
            }
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "Memory store not found"}


memory_manager = MemoryManager()


# API Routes

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI-Powered Grant Proposal Assistant API",
        "version": "1.0.0",
        "endpoints": [
            "/generate-outline",
            "/generate-budget",
            "/simulate-review",
            "/generate-complete-proposal",
            "/topics",
            "/topic-summary/{topic}",
            "/refine",
            "/adjust-budget"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_available": ["outline", "budget", "reviewer"]
    }


@app.post("/generate-outline")
async def generate_outline(request: OutlineRequest):
    """Generate grant proposal outline"""
    try:
        result = outline_agent.process(
            topic=request.topic,
            goals=request.goals,
            funding_agency=request.funding_agency
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating outline: {str(e)}")


@app.post("/generate-budget")
async def generate_budget(request: BudgetRequest):
    """Generate grant proposal budget"""
    try:
        result = budget_agent.process(
            topic=request.topic,
            goals=request.goals,
            funding_agency=request.funding_agency,
            duration=request.duration,
            team_size=request.team_size,
            project_type=request.project_type
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating budget: {str(e)}")


@app.post("/simulate-review")
async def simulate_review(request: ReviewRequest):
    """Simulate grant proposal review"""
    try:
        result = reviewer_agent.process(
            topic=request.topic,
            goals=request.goals,
            funding_agency=request.funding_agency
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating review: {str(e)}")


@app.post("/generate-complete-proposal")
async def generate_complete_proposal(request: ProposalRequest, background_tasks: BackgroundTasks):
    """Generate complete grant proposal with all components"""
    try:
        # Step 1: Generate outline
        outline_result = outline_agent.process(
            topic=request.topic,
            goals=request.goals,
            funding_agency=request.funding_agency
        )

        # Step 2: Generate budget
        budget_result = budget_agent.process(
            topic=request.topic,
            goals=request.goals,
            funding_agency=request.funding_agency,
            duration=request.duration,
            team_size=request.team_size,
            project_type=request.project_type
        )

        # Step 3: Simulate review
        review_result = reviewer_agent.process(
            topic=request.topic,
            goals=request.goals,
            funding_agency=request.funding_agency
        )

        # Compile complete proposal
        complete_proposal = {
            "topic": request.topic,
            "goals": request.goals,
            "funding_agency": request.funding_agency,
            "outline": outline_result,
            "budget": budget_result,
            "simulated_review": review_result,
            "generation_timestamp": datetime.now().isoformat(),
            "completion_status": "complete"
        }

        return {
            "success": True,
            "data": complete_proposal,
            "message": "Complete proposal generated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating complete proposal: {str(e)}")


@app.get("/topics")
async def get_all_topics():
    """Get list of all topics in memory"""
    try:
        topics = memory_manager.get_all_topics()
        return {
            "success": True,
            "topics": topics,
            "count": len(topics),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving topics: {str(e)}")


@app.get("/topic-summary/{topic}")
async def get_topic_summary(topic: str):
    """Get summary of work done on a specific topic"""
    try:
        summary = memory_manager.get_topic_summary(topic)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])

        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving topic summary: {str(e)}")


@app.post("/refine")
async def refine_component(request: RefineRequest):
    """Refine a specific component based on feedback"""
    try:
        if request.agent_type == "outline":
            result = outline_agent.refine_outline(request.topic, request.feedback)
        elif request.agent_type == "budget":
            # Budget refinement would need to be implemented in the agent
            result = {"message": "Budget refinement not yet implemented"}
        elif request.agent_type == "review":
            result = {"message": "Review refinement not applicable - generate new review instead"}
        else:
            raise HTTPException(status_code=400, detail="Invalid agent_type. Use 'outline', 'budget', or 'review'")

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refining component: {str(e)}")


@app.post("/adjust-budget")
async def adjust_budget(request: BudgetAdjustmentRequest):
    """Adjust budget to meet target amount"""
    try:
        result = budget_agent.adjust_budget(
            topic=request.topic,
            target_amount=request.target_amount,
            constraints=request.constraints
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adjusting budget: {str(e)}")


@app.post("/generate-panel-summary/{topic}")
async def generate_panel_summary(topic: str):
    """Generate comprehensive panel summary report"""
    try:
        result = reviewer_agent.generate_panel_summary(topic)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating panel summary: {str(e)}")


@app.delete("/topic/{topic}")
async def delete_topic(topic: str):
    """Delete a topic from memory"""
    try:
        with open("memory/memory_store.json", 'r') as f:
            memory = json.load(f)

        if topic not in memory:
            raise HTTPException(status_code=404, detail="Topic not found")

        del memory[topic]

        with open("memory/memory_store.json", 'w') as f:
            json.dump(memory, f, indent=2)

        return {
            "success": True,
            "message": f"Topic '{topic}' deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting topic: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)