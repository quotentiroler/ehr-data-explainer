"""
FastAPI application for EHR Data Explainer.

Transforms EHR data into simple, visual health explanations using:
- Neo4j knowledge graph for patient data relationships
- Claude AI for generating plain-language explanations
- Wan 2.2 for educational video generation
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from neo4j import GraphDatabase

from config import get_settings
from services.patient_service import PatientQueryService
from services.explanation_service import ExplanationService
from services.video_service import VideoGenerationService

settings = get_settings()

# Global service instances
driver = None
patient_service: PatientQueryService = None
explanation_service: ExplanationService = None
video_service: VideoGenerationService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    global driver, patient_service, explanation_service, video_service
    
    # Startup: Initialize services
    print("🚀 Starting EHR Data Explainer...")
    
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    
    # Verify Neo4j connection
    try:
        driver.verify_connectivity()
        print("✅ Connected to Neo4j")
    except Exception as e:
        print(f"⚠️ Neo4j connection failed: {e}")
    
    patient_service = PatientQueryService(driver)
    explanation_service = ExplanationService(settings.anthropic_api_key, settings.claude_model)
    video_service = VideoGenerationService(settings.hf_token)
    
    print("✅ All services initialized")
    
    yield
    
    # Shutdown: Cleanup
    print("👋 Shutting down...")
    if driver:
        driver.close()


app = FastAPI(
    title="EHR Data Explainer",
    description="Transform EHR data into visual health explanations",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for videos
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
videos_dir = Path(__file__).parent / "generated_videos"
videos_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/videos", StaticFiles(directory=str(videos_dir)), name="videos")


# ============== Request/Response Models ==============

class ExplainRequest(BaseModel):
    """Request model for health explanation generation."""
    patient_id: str
    reading_level: str = "6th grade"
    generate_video: bool = True


class ExplainResponse(BaseModel):
    """Response model for health explanation."""
    patient_name: str
    explanation: dict
    video_prompt: str | None = None
    video_url: str | None = None
    graph_data: dict


# ============== API Endpoints ==============

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    neo4j_status = "connected"
    try:
        driver.verify_connectivity()
    except:
        neo4j_status = "disconnected"
    
    return {
        "status": "healthy",
        "neo4j": neo4j_status,
        "version": "0.1.0"
    }


@app.get("/api/patients")
async def list_patients(limit: int = 50):
    """Get list of all patients for the selector UI."""
    try:
        patients = patient_service.get_all_patients(limit)
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    """Get detailed health summary for a specific patient."""
    try:
        summary = patient_service.get_patient_health_summary(patient_id)
        return summary.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Patient not found: {e}")


@app.get("/api/patients/{patient_id}/graph")
async def get_patient_graph(patient_id: str):
    """
    Get Cypher query for Neovis.js graph visualization.
    The frontend will execute this query directly against Neo4j.
    """
    cypher = f"""
    MATCH (p:Patient {{id: '{patient_id}'}})
    OPTIONAL MATCH (p)-[r1]-(connected)
    OPTIONAL MATCH (connected)-[r2]-(secondary)
    WHERE NOT secondary:Patient
    RETURN p, r1, connected, r2, secondary
    LIMIT 100
    """
    return {"cypher": cypher, "patient_id": patient_id}


@app.post("/api/explain", response_model=ExplainResponse)
async def explain_health(request: ExplainRequest):
    """
    Generate a personalized health explanation for a patient.
    
    This endpoint:
    1. Fetches patient data from Neo4j graph
    2. Generates plain-language explanation via Claude
    3. Optionally generates an educational video via Wan 2.2
    """
    # Get patient data from graph
    try:
        summary = patient_service.get_patient_health_summary(request.patient_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Patient not found: {e}")
    
    if not summary.conditions:
        raise HTTPException(status_code=400, detail="No conditions found for patient")
    
    # Generate explanation with Claude
    try:
        explanation = await explanation_service.generate_health_explanation(
            summary,
            request.reading_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {e}")
    
    video_prompt = None
    video_url = None
    
    if request.generate_video:
        # Generate video prompt
        try:
            video_prompt = await explanation_service.generate_video_prompt(summary, explanation)
        except Exception as e:
            print(f"Warning: Failed to generate video prompt: {e}")
        
        # Generate video with Wan 2.2
        if video_prompt:
            try:
                print(f"🎬 Starting video generation...")
                result = await video_service.generate_video(video_prompt, request.patient_id)
                video_url = f"/videos/{Path(result['video_path']).name}"
                print(f"✅ Video ready: {video_url}")
            except Exception as e:
                print(f"❌ Video generation failed: {e}")
                video_url = None
    
    return ExplainResponse(
        patient_name=summary.patient_name,
        explanation=explanation,
        video_prompt=video_prompt,
        video_url=video_url,
        graph_data={
            "conditions": summary.conditions,
            "medications": summary.medications,
            "body_systems": summary.body_systems_affected
        }
    )


@app.get("/api/body-systems")
async def get_body_systems():
    """Get all body systems in the knowledge graph."""
    query = """
    MATCH (bs:BodySystem)
    RETURN bs.name as name, bs.description as description
    ORDER BY bs.name
    """
    with driver.session() as session:
        results = session.run(query)
        return [dict(r) for r in results]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
