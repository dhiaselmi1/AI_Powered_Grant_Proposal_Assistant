# AI-Powered Grant Proposal Assistant 💰

A comprehensive AI-powered system that assists researchers and nonprofits in drafting grant proposals using specialized AI agents powered by Google's Gemini Flash 2.0.

## 🌟 Features

- **📋 Outline Designer Agent**: Creates comprehensive, well-structured grant proposal outlines
- **💰 Budget Estimator Agent**: Generates realistic budget estimates with detailed justifications
- **🔍 Reviewer Simulation Agent**: Provides multi-perspective review feedback to improve proposals
- **📊 Version Tracking**: Maintains complete history of proposal iterations and rationale
- **🎯 Agency-Specific Guidance**: Tailors recommendations based on funding agency requirements
- **📈 Interactive Dashboard**: User-friendly Streamlit interface for proposal management

## 🏗️ Architecture

```
Grant-Proposal-Assistant/
├── backend/
│   ├── agents/
│   │   ├── base.py                     # Base agent class
│   │   ├── OutlineDesignerAgent.py     # Proposal structure agent
│   │   ├── BudgetEstimatorAgent.py     # Financial planning agent
│   │   └── ReviewerSimulationAgent.py  # Review simulation agent
│   ├── main.py                         # FastAPI server
│   └── memory/
│       └── memory_store.json           # Project data storage
├── frontend/
│   └── app.py                          # Streamlit interface
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google AI API Key (for Gemini Flash 2.0)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Grant-Proposal-Assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key_here"
   ```
   
   Or create a `.env` file:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

### Running the Application

1. **Start the FastAPI backend:**
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Streamlit frontend:**
   ```bash
   cd frontend
   streamlit run app.py
   ```
   The web interface will open at `http://localhost:8501`

## 📖 Usage Guide

### Creating a New Grant Proposal

1. **Navigate to "Create Proposal"** in the sidebar
2. **Fill in the proposal details:**
   - Research Topic
   - Project Goals
   - Funding Agency
   - Duration and Team Size
   - Project Type

3. **Choose generation options:**
   - Generate complete proposal (recommended)
   - Or select individual components

4. **Review the generated components:**
   - **Outline**: Comprehensive structure and content recommendations
   - **Budget**: Detailed financial breakdown with justifications
   - **Review**: Multi-perspective feedback and scoring

### Managing Existing Projects

1. **Go to "Manage Projects"** to view all created proposals
2. **Select a project** to view its history and details
3. **Available actions:**
   - Generate panel summary reports
   - Refine components based on feedback
   - View version history
   - Delete projects

### Advanced Review Simulation

1. **Use the "Review Simulation"** page for detailed feedback
2. **Input proposal details** or select existing projects
3. **Get comprehensive feedback** from multiple reviewer perspectives:
   - Technical Expert
   - Methodology Specialist
   - Budget Analyst
   - Impact Assessor
   - Program Officer

## 🤖 AI Agents Overview

### Outline Designer Agent
- Creates structured proposal outlines
- Provides section-by-section guidance
- Considers funding agency requirements
- Suggests content and approach for each section

### Budget Estimator Agent
- Generates realistic budget estimates
- Provides detailed cost breakdowns
- Considers personnel, equipment, travel, and indirect costs
- Offers funding strategy recommendations

### Reviewer Simulation Agent
- Simulates multiple reviewer perspectives
- Provides detailed feedback and scoring
- Identifies strengths and weaknesses
- Generates improvement recommendations
- Creates comprehensive panel summary reports

## 🔧 API Endpoints

### Core Endpoints
- `POST /generate-outline` - Generate proposal outline
- `POST /generate-budget` - Generate budget estimate
- `POST /simulate-review` - Simulate proposal review
- `POST /generate-complete-proposal` - Generate all components

### Management Endpoints
- `GET /topics` - List all projects
- `GET /topic-summary/{topic}` - Get project details
- `POST /refine` - Refine proposal components
- `POST /adjust-budget` - Adjust budget to target amount
- `DELETE /topic/{topic}` - Delete project

### Utility Endpoints
- `GET /health` - API health check
- `POST /generate-panel-summary/{topic}` - Generate review summary

## 💾 Data Storage

The system uses JSON file storage for simplicity and portability:

- **Location**: `backend/memory/memory_store.json`
- **Structure**: Hierarchical storage by topic with version tracking
- **Features**: Complete audit trail of all changes and agent interactions

### Data Structure Example
```json
{
  "AI-powered climate modeling": {
    "versions": [
      {
        "version": 1,
        "agent": "OutlineDesignerAgent",
        "timestamp": "2024-01-15T10:30:00",
        "output": {...},
        "rationale": "Created comprehensive outline..."
      }
    ],
    "agents_used": ["OutlineDesignerAgent", "BudgetEstimatorAgent"],
    "created_at": "2024-01-15T10:30:00",
    "last_updated": "2024-01-15T11:45:00"
  }
}
```

## 🎨 Frontend Features

### Home Dashboard
- System status and health checks
- Recent project overview
- Quick navigation to key features

### Proposal Creation
- Interactive form-based input
- Real-time progress tracking
- Tabbed results display
- Component-specific visualizations

### Project Management
- Project listing and selection
- Version history tracking
- Refinement capabilities
- Export/import functionality

### Review Simulation
- Multiple input methods
- Advanced review parameters
- Detailed feedback presentation
- Panel summary generation

## ⚙️ Configuration

### Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key_here  # Required
API_BASE_URL=http://localhost:8000       # Optional, for frontend
```

### Customization Options

1. **Add new funding agencies** in the frontend selectboxes
2. **Modify agent prompts** in the respective agent files
3. **Adjust review criteria** in `ReviewerSimulationAgent.py`
4. **Customize budget categories** in `BudgetEstimatorAgent.py`

## 🔒 Security Considerations

- API keys are handled through environment variables
- No sensitive data is logged
- All data remains local (JSON file storage)
- CORS is configured for development (restrict for production)

## 🚀 Production Deployment

### Backend Deployment
```bash
# Using uvicorn with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment
```bash
# Configure for production
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Recommended Production Setup
- Use a proper database (PostgreSQL, MongoDB)
- Implement user authentication
- Add rate limiting and monitoring
- Use environment-specific configurations
- Deploy with Docker containers

## 📊 Performance Considerations

- **Response Times**: Typical 5-15 seconds per agent (depends on Gemini API)
- **Concurrent Users**: Limited by Gemini API quotas
- **Storage**: JSON files suitable for moderate usage (consider database for scale)
- **Memory**: Low memory footprint for backend processes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling for API calls
- Write tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check if backend server is running
   - Verify API_BASE_URL in frontend
   - Ensure firewall allows connections

2. **Gemini API Errors**
   - Verify GOOGLE_API_KEY is set correctly
   - Check API quotas and billing
   - Review Gemini API documentation

3. **Memory Storage Issues**
   - Check write permissions on memory/ directory
   - Ensure sufficient disk space
   - Validate JSON file integrity

### Getting Help
- Check the API documentation at `http://localhost:8000/docs`
- Review logs in the backend console
- Use the health check endpoint for diagnostics

## 🔮 Future Enhancements

- [ ] User authentication and multi-tenancy
- [ ] Integration with institutional grant databases
- [ ] Advanced NLP for automatic content extraction
- [ ] Collaborative editing features
- [ ] Integration with LaTeX for PDF generation
- [ ] Machine learning for success prediction
- [ ] Advanced visualization and analytics
- [ ] Mobile-responsive design improvements

---

**Made with ❤️ for the research community**
