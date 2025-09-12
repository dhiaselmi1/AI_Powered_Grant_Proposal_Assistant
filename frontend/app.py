"""
Streamlit Frontend for AI-Powered Grant Proposal Assistant
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="AI-Powered Grant Proposal Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"  # Update for production

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #2E86AB;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
def make_api_request(endpoint, method="GET", data=None):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def display_agent_output(result, agent_name):
    """Display agent output in a formatted way"""
    if not result:
        return

    data = result.get('data', {})

    with st.container():
        st.markdown(f'<div class="agent-card">', unsafe_allow_html=True)
        st.subheader(f"🤖 {agent_name} Results")

        # Display rationale
        if 'rationale' in data:
            st.write("**Rationale:**")
            st.write(data['rationale'])

        # Display specific content based on agent type
        if agent_name == "Outline Designer":
            display_outline_results(data)
        elif agent_name == "Budget Estimator":
            display_budget_results(data)
        elif agent_name == "Reviewer Simulation":
            display_review_results(data)

        st.markdown('</div>', unsafe_allow_html=True)


def display_outline_results(data):
    """Display outline-specific results"""
    outline = data.get('outline', {})

    if 'outline_content' in outline:
        st.write("**Generated Outline:**")
        st.text_area("Outline Content", outline['outline_content'], height=300, disabled=True)

    if 'recommendations' in data:
        st.write("**Recommendations:**")
        for rec in data['recommendations']:
            st.write(f"• {rec}")


def display_budget_results(data):
    """Display budget-specific results"""
    if 'budget_summary' in data:
        summary = data['budget_summary']

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Cost", f"${summary.get('total_cost', 0):,.2f}")

        with col2:
            st.metric("Currency", summary.get('currency', 'USD'))

        # Display cost breakdown chart
        if 'cost_breakdown_chart' in data:
            breakdown = data['cost_breakdown_chart']
            if breakdown:
                fig = px.pie(
                    values=list(breakdown.values()),
                    names=list(breakdown.keys()),
                    title="Budget Breakdown by Category"
                )
                st.plotly_chart(fig)

    if 'funding_recommendations' in data:
        st.write("**Funding Recommendations:**")
        for rec in data['funding_recommendations']:
            st.write(f"• {rec}")


def display_review_results(data):
    """Display review-specific results"""
    if 'overall_assessment' in data:
        assessment = data['overall_assessment']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Overall Score", f"{assessment.get('overall_score', 0):.2f}/5.0")

        with col2:
            st.metric("Consensus", assessment.get('consensus_recommendation', 'N/A'))

        with col3:
            st.metric("Review Agreement", assessment.get('review_consensus', 'N/A'))

        # Display criterion scores
        if 'criterion_scores' in assessment:
            scores_df = pd.DataFrame.from_dict(
                assessment['criterion_scores'],
                orient='index',
                columns=['Score']
            )
            scores_df = scores_df.reset_index()
            scores_df.columns = ['Criterion', 'Score']

            fig = px.bar(
                scores_df,
                x='Criterion',
                y='Score',
                title="Review Scores by Criterion",
                color='Score',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(yaxis=dict(range=[0, 5]))
            st.plotly_chart(fig)

    if 'improvement_recommendations' in data:
        st.write("**Improvement Recommendations:**")
        for i, rec in enumerate(data['improvement_recommendations'][:5], 1):
            st.write(f"{i}. {rec}")


# Main application
def main():
    st.markdown('<h1 class="main-header">💰 AI-Powered Grant Proposal Assistant</h1>', unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Home", "📝 Create Proposal", "📊 Manage Projects", "🔍 Review Simulation", "⚙️ Settings"]
    )

    if page == "🏠 Home":
        show_home_page()
    elif page == "📝 Create Proposal":
        show_create_proposal_page()
    elif page == "📊 Manage Projects":
        show_manage_projects_page()
    elif page == "🔍 Review Simulation":
        show_review_simulation_page()
    elif page == "⚙️ Settings":
        show_settings_page()


def show_home_page():
    """Display home page"""
    st.markdown('<h2 class="section-header">Welcome to the Grant Proposal Assistant</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **🎯 What this tool does:**
        - Creates comprehensive grant proposal outlines
        - Generates detailed budget estimates
        - Simulates peer review feedback
        - Tracks proposal versions and improvements
        - Provides actionable recommendations
        """)

    with col2:
        st.success("""
        **🤖 AI Agents Available:**
        - **Outline Designer**: Structure and content planning
        - **Budget Estimator**: Financial planning and analysis
        - **Reviewer Simulation**: Multi-perspective feedback
        """)

    # API Status Check
    st.markdown('<h3 class="section-header">System Status</h3>', unsafe_allow_html=True)

    health_check = make_api_request("/health")
    if health_check:
        st.success(f"✅ API is healthy - {health_check.get('status', 'unknown')}")
        st.write(f"**Available Agents:** {', '.join(health_check.get('agents_available', []))}")
    else:
        st.error("❌ API is not responding. Please check the backend server.")

    # Recent Activity
    topics_response = make_api_request("/topics")
    if topics_response and topics_response.get('success'):
        topics = topics_response.get('topics', [])
        if topics:
            st.markdown('<h3 class="section-header">Recent Projects</h3>', unsafe_allow_html=True)
            for topic in topics[-5:]:  # Show last 5 topics
                with st.expander(f"📁 {topic}"):
                    summary_response = make_api_request(f"/topic-summary/{topic}")
                    if summary_response and summary_response.get('success'):
                        summary = summary_response['data']
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Versions:** {summary.get('versions', 0)}")
                        with col2:
                            st.write(f"**Agents Used:** {len(summary.get('agents_used', []))}")
                        with col3:
                            st.write(f"**Last Updated:** {summary.get('last_updated', 'N/A')[:10]}")


def show_create_proposal_page():
    """Display create proposal page"""
    st.markdown('<h2 class="section-header">Create New Grant Proposal</h2>', unsafe_allow_html=True)

    # Input form
    with st.form("proposal_form"):
        col1, col2 = st.columns(2)

        with col1:
            topic = st.text_input("Research Topic *", placeholder="e.g., AI-powered climate modeling")
            funding_agency = st.selectbox(
                "Funding Agency *",
                ["NSF", "NIH", "DOE", "NASA", "DARPA", "EU Horizon", "Other"]
            )
            duration = st.selectbox("Project Duration", ["1 year", "2 years", "3 years", "4 years", "5 years"])

        with col2:
            goals = st.text_area("Project Goals *", height=100, placeholder="Describe your main research objectives...")
            team_size = st.selectbox("Team Size", ["small (1-2 people)", "medium (3-5 people)", "large (6+ people)"])
            project_type = st.selectbox("Project Type", ["research", "development", "education", "infrastructure"])

        # Advanced options
        with st.expander("Advanced Options"):
            budget_target = st.number_input("Target Budget Amount ($)", min_value=0, value=0, step=1000)
            generate_complete = st.checkbox("Generate Complete Proposal (all components)", value=True)

        submitted = st.form_submit_button("Generate Proposal", use_container_width=True)

    if submitted:
        if not topic or not goals or not funding_agency:
            st.error("Please fill in all required fields marked with *")
            return

        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        if generate_complete:
            # Generate complete proposal
            status_text.text("Generating complete proposal...")

            request_data = {
                "topic": topic,
                "goals": goals,
                "funding_agency": funding_agency,
                "duration": duration,
                "team_size": team_size,
                "project_type": project_type
            }

            if budget_target > 0:
                request_data["budget_target"] = budget_target

            result = make_api_request("/generate-complete-proposal", "POST", request_data)
            progress_bar.progress(100)

            if result and result.get('success'):
                st.success("✅ Complete proposal generated successfully!")

                # Display results
                data = result['data']

                # Tabs for different components
                tab1, tab2, tab3 = st.tabs(["📋 Outline", "💰 Budget", "🔍 Review"])

                with tab1:
                    display_agent_output({'data': data['outline']}, "Outline Designer")

                with tab2:
                    display_agent_output({'data': data['budget']}, "Budget Estimator")

                with tab3:
                    display_agent_output({'data': data['simulated_review']}, "Reviewer Simulation")

            status_text.empty()

        else:
            # Generate individual components
            components = []
            if st.checkbox("Generate Outline", value=True):
                components.append(("outline", "Outline Designer"))
            if st.checkbox("Generate Budget", value=True):
                components.append(("budget", "Budget Estimator"))
            if st.checkbox("Simulate Review", value=True):
                components.append(("review", "Reviewer Simulation"))

            results = {}
            for i, (component, agent_name) in enumerate(components):
                progress_bar.progress((i + 1) / len(components))
                status_text.text(f"Generating {component}...")

                if component == "outline":
                    endpoint = "/generate-outline"
                    request_data = {"topic": topic, "goals": goals, "funding_agency": funding_agency}
                elif component == "budget":
                    endpoint = "/generate-budget"
                    request_data = {
                        "topic": topic, "goals": goals, "funding_agency": funding_agency,
                        "duration": duration, "team_size": team_size, "project_type": project_type
                    }
                elif component == "review":
                    endpoint = "/simulate-review"
                    request_data = {"topic": topic, "goals": goals, "funding_agency": funding_agency}

                result = make_api_request(endpoint, "POST", request_data)
                if result:
                    results[agent_name] = result

                time.sleep(0.5)  # Brief pause for better UX

            status_text.empty()

            # Display results
            for agent_name, result in results.items():
                display_agent_output(result, agent_name)


def show_manage_projects_page():
    """Display project management page"""
    st.markdown('<h2 class="section-header">Manage Projects</h2>', unsafe_allow_html=True)

    # Get all topics
    topics_response = make_api_request("/topics")
    if not topics_response or not topics_response.get('success'):
        st.warning("No projects found or unable to connect to API.")
        return

    topics = topics_response.get('topics', [])
    if not topics:
        st.info("No projects created yet. Go to 'Create Proposal' to get started!")
        return

    # Project selection
    selected_topic = st.selectbox("Select a project:", topics)

    if selected_topic:
        # Get project summary
        summary_response = make_api_request(f"/topic-summary/{selected_topic}")
        if summary_response and summary_response.get('success'):
            summary = summary_response['data']

            # Project overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Versions", summary.get('versions', 0))
            with col2:
                st.metric("Agents Used", len(summary.get('agents_used', [])))
            with col3:
                st.metric("Created", summary.get('created_at', 'N/A')[:10])
            with col4:
                st.metric("Last Updated", summary.get('last_updated', 'N/A')[:10])

            # Project actions
            st.markdown('<h3 class="section-header">Project Actions</h3>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📊 Generate Panel Summary"):
                    with st.spinner("Generating panel summary..."):
                        panel_result = make_api_request(f"/generate-panel-summary/{selected_topic}", "POST")
                        if panel_result and panel_result.get('success'):
                            st.success("Panel summary generated!")
                            data = panel_result['data']
                            with st.expander("Panel Summary Report", expanded=True):
                                st.text_area("Report", data.get('panel_summary', 'No content'), height=400,
                                             disabled=True)

            with col2:
                if st.button("🔄 Refine Components"):
                    st.session_state.show_refine = True

            with col3:
                if st.button("🗑️ Delete Project", type="secondary"):
                    if st.checkbox(f"Confirm deletion of '{selected_topic}'"):
                        delete_result = make_api_request(f"/topic/{selected_topic}", "DELETE")
                        if delete_result and delete_result.get('success'):
                            st.success(f"Project '{selected_topic}' deleted successfully!")
                            st.rerun()

            # Refinement interface
            if st.session_state.get('show_refine', False):
                st.markdown('<h3 class="section-header">Refine Components</h3>', unsafe_allow_html=True)

                with st.form("refine_form"):
                    agent_type = st.selectbox("Component to refine:", ["outline", "budget", "review"])
                    feedback = st.text_area("Feedback/Improvements needed:", height=150)

                    if st.form_submit_button("Apply Refinements"):
                        if feedback:
                            refine_data = {
                                "topic": selected_topic,
                                "feedback": feedback,
                                "agent_type": agent_type
                            }

                            refine_result = make_api_request("/refine", "POST", refine_data)
                            if refine_result and refine_result.get('success'):
                                st.success("Refinements applied successfully!")
                                display_agent_output(refine_result, f"Refined {agent_type.title()}")
                        else:
                            st.error("Please provide feedback for refinement.")

            # Version history
            st.markdown('<h3 class="section-header">Version History</h3>', unsafe_allow_html=True)

            if 'latest_version' in summary and summary['latest_version']:
                latest = summary['latest_version']

                with st.expander("Latest Version Details", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Version:** {latest.get('version', 'N/A')}")
                        st.write(f"**Agent:** {latest.get('agent', 'N/A')}")
                    with col2:
                        st.write(f"**Timestamp:** {latest.get('timestamp', 'N/A')}")
                        st.write(f"**Rationale:** {latest.get('rationale', 'N/A')[:100]}...")


def show_review_simulation_page():
    """Display review simulation page"""
    st.markdown('<h2 class="section-header">Advanced Review Simulation</h2>', unsafe_allow_html=True)

    st.info("""
    This page allows you to simulate detailed grant reviews with multiple reviewer perspectives.
    Upload or input your proposal details to get comprehensive feedback.
    """)

    # Input method selection
    input_method = st.radio("Choose input method:", ["Form Input", "Existing Project"])

    if input_method == "Form Input":
        with st.form("review_form"):
            col1, col2 = st.columns(2)

            with col1:
                topic = st.text_input("Research Topic")
                funding_agency = st.selectbox("Funding Agency", ["NSF", "NIH", "DOE", "NASA", "Other"])

            with col2:
                goals = st.text_area("Project Goals", height=150)

            # Additional review parameters
            st.subheader("Review Parameters")
            col3, col4 = st.columns(2)

            with col3:
                review_focus = st.multiselect(
                    "Focus Areas for Review:",
                    ["Technical Merit", "Innovation", "Budget Justification", "Team Qualifications", "Broader Impacts"]
                )

            with col4:
                reviewer_expertise = st.multiselect(
                    "Reviewer Expertise Areas:",
                    ["Computer Science", "Biology", "Physics", "Engineering", "Social Sciences", "Policy"]
                )

            if st.form_submit_button("Simulate Review"):
                if topic and goals and funding_agency:
                    with st.spinner("Simulating comprehensive review..."):
                        review_data = {
                            "topic": topic,
                            "goals": goals,
                            "funding_agency": funding_agency
                        }

                        result = make_api_request("/simulate-review", "POST", review_data)
                        if result and result.get('success'):
                            st.success("Review simulation completed!")
                            display_agent_output(result, "Reviewer Simulation")
                else:
                    st.error("Please fill in all required fields.")

    else:  # Existing Project
        topics_response = make_api_request("/topics")
        if topics_response and topics_response.get('success'):
            topics = topics_response.get('topics', [])
            if topics:
                selected_topic = st.selectbox("Select existing project:", topics)

                if st.button("Run Advanced Review"):
                    with st.spinner("Running advanced review simulation..."):
                        result = make_api_request(f"/generate-panel-summary/{selected_topic}", "POST")
                        if result and result.get('success'):
                            st.success("Advanced review completed!")
                            data = result['data']

                            # Display panel summary
                            st.markdown('<h3 class="section-header">Panel Review Summary</h3>', unsafe_allow_html=True)
                            with st.expander("Full Panel Report", expanded=True):
                                st.text_area("Report Content", data.get('panel_summary', ''), height=500, disabled=True)
            else:
                st.info("No existing projects found. Create a project first.")


def show_settings_page():
    """Display settings page"""
    st.markdown('<h2 class="section-header">Settings & Configuration</h2>', unsafe_allow_html=True)

    # API Configuration
    st.subheader("🔧 API Configuration")

    col1, col2 = st.columns(2)
    with col1:
        api_url = st.text_input("API Base URL", value=API_BASE_URL)
        st.caption("Update if running backend on different host/port")

    with col2:
        if st.button("Test API Connection"):
            test_result = make_api_request("/health")
            if test_result:
                st.success("✅ API connection successful!")
            else:
                st.error("❌ API connection failed!")

    # Model Configuration
    st.subheader("🤖 AI Model Settings")

    st.info("""
    **Current Model:** Gemini Flash 2.0

    The system uses Google's Gemini Flash 2.0 for all AI agents. Make sure your API key is properly configured in the backend environment.
    """)

    # Data Management
    st.subheader("💾 Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export All Projects"):
            topics_response = make_api_request("/topics")
            if topics_response and topics_response.get('success'):
                topics = topics_response.get('topics', [])
                export_data = {}

                for topic in topics:
                    summary_response = make_api_request(f"/topic-summary/{topic}")
                    if summary_response and summary_response.get('success'):
                        export_data[topic] = summary_response['data']

                if export_data:
                    st.download_button(
                        "Download Projects Data",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"grant_projects_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    st.success("Export prepared! Click download button above.")
                else:
                    st.warning("No project data to export.")

    with col2:
        st.file_uploader("Import Projects", type=['json'], help="Upload previously exported project data")

    # System Information
    st.subheader("ℹ️ System Information")

    system_info = {
        "Frontend": "Streamlit",
        "Backend": "FastAPI",
        "AI Model": "Gemini Flash 2.0",
        "Database": "JSON File Storage",
        "API Version": "1.0.0"
    }

    for key, value in system_info.items():
        st.write(f"**{key}:** {value}")

    # Clear session state
    if st.button("Clear Session Data", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session data cleared!")
        st.rerun()


# Initialize session state
if 'show_refine' not in st.session_state:
    st.session_state.show_refine = False

# Run the application
if __name__ == "__main__":
    main()