# 🏥 EHR Data Explainer

> Transform complex EHR data into visual health explanations using Neo4j, Claude AI, and Wan 2.2 video generation.

![Architecture](https://img.shields.io/badge/Architecture-Neo4j%20%2B%20Claude%20%2B%20Wan%202.2-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11%2B-yellow)
![React](https://img.shields.io/badge/React-18-61dafb)

## 🎯 What This Does

This hackathon project helps patients understand their health by:

1. **Loading FHIR data** into a Neo4j graph database
2. **Visualizing connections** between conditions, medications, and body systems
3. **Generating explanations** using Claude AI in plain language
4. **Creating educational videos** with Wan 2.2 text-to-video AI

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Anthropic API key (for Claude)
- Hugging Face API key (for Wan 2.2, optional)

### 1. Clone and Configure

```bash
git clone <your-repo-url>
cd fhir-health-explainer

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
```

### 2. Start Services

```bash
# Start all services
docker compose up -d

# Wait for Neo4j to be ready (about 30 seconds)
docker compose logs -f neo4j
```

### 3. Load Sample Data

```bash
# Install Python dependencies locally (for running the loader)
pip install neo4j

# Run the data loader
python scripts/load_sample_data.py
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Neo4j Browser** | http://localhost:7474 |

## 📁 Project Structure

```
fhir-health-explainer/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints
│   ├── config.py              # Configuration
│   ├── services/
│   │   ├── patient_service.py     # Neo4j queries
│   │   ├── explanation_service.py # Claude integration
│   │   └── video_service.py       # Wan 2.2 integration
│   └── etl/
│       ├── fhir_to_neo4j.py   # FHIR loader
│       └── body_systems.py    # Medical mappings
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.tsx            # Main application
│   │   └── components/
│   │       ├── PatientSelector.tsx
│   │       ├── PatientGraph.tsx    # Neo4j visualization
│   │       ├── ExplanationDisplay.tsx
│   │       └── VideoPlayer.tsx
│   └── ...
│
├── scripts/
│   └── load_sample_data.py    # Data loader script
│
├── docker-compose.yml         # Container orchestration
└── IMPLEMENTATION_GUIDE.md    # Detailed technical guide
```

## 🔧 Development Setup

### Backend (Python)

```bash
cd backend
pip install -e .

# Run with auto-reload
uvicorn main:app --reload
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/patients` | GET | List all patients |
| `/api/patients/{id}` | GET | Get patient health summary |
| `/api/explain` | POST | Generate AI explanation & video |
| `/health` | GET | Health check |

### Example: Generate Explanation

```bash
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "patient-001", "reading_level": "6th grade"}'
```

## 🧠 AI Integration

### Claude for Health Explanations

The system uses Claude to:
- Summarize conditions in plain language
- Explain how medications work
- Describe connections between body systems
- Generate video prompts for visualization

### Wan 2.2 for Video Generation

Educational videos are generated showing:
- Body system animations
- Condition visualizations
- Medication mechanisms

## 📊 Neo4j Graph Model

```
(Patient)-[:HAS_CONDITION]->(Condition)-[:AFFECTS]->(BodySystem)
(Patient)-[:TAKES_MEDICATION]->(Medication)-[:TREATS]->(Condition)
(Medication)-[:TARGETS]->(BodySystem)
```

### Sample Cypher Queries

```cypher
// Find all conditions affecting a body system
MATCH (c:Condition)-[:AFFECTS]->(bs:BodySystem {name: 'Cardiovascular'})
RETURN c.display, bs.name

// Get patient health network
MATCH (p:Patient {id: 'patient-001'})
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m)
RETURN p, c, m
```

## 🎨 Customization

### Adding Body System Mappings

Edit `backend/etl/body_systems.py`:

```python
CONDITION_TO_BODY_SYSTEM = {
    "E11": "Endocrine",  # Type 2 Diabetes
    "I10": "Cardiovascular",  # Hypertension
    # Add more mappings...
}
```

### Adjusting Claude Prompts

Edit `backend/services/explanation_service.py` to customize the explanation style.

## 🐛 Troubleshooting

### Neo4j Connection Failed
```bash
# Check if Neo4j is running
docker compose ps neo4j

# View Neo4j logs
docker compose logs neo4j
```

### API Key Issues
```bash
# Verify environment variables are set
docker compose exec backend env | grep API_KEY
```

### Frontend Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration in backend/main.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Synthea](https://synthetichealth.github.io/synthea/) for synthetic patient data
- [neovis.js](https://github.com/neo4j-contrib/neovis.js) for graph visualization
- [Anthropic Claude](https://anthropic.com) for AI explanations
- [Wan 2.2](https://huggingface.co/Wan-AI) for video generation

---

Built with ❤️ for the healthcare AI hackathon
