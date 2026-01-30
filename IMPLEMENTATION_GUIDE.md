# 🏥 EHR Data Explainer - Implementation Guide

> **Transform complex EHR data into simple, visual explanations using Neo4j knowledge graphs, Claude AI, and Wan 2.2 video generation.**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack & Dependencies](#tech-stack--dependencies)
4. [Phase 1: Data Foundation](#phase-1-data-foundation)
5. [Phase 2: Intelligence Layer](#phase-2-intelligence-layer)
6. [Phase 3: Visual Generation](#phase-3-visual-generation)
7. [Phase 4: Demo UI](#phase-4-demo-ui)
8. [Project Structure](#project-structure)
9. [Environment Setup](#environment-setup)
10. [API Keys & Services](#api-keys--services)
11. [Sample Data & Testing](#sample-data--testing)
12. [Deployment](#deployment)

---

## Project Overview

### The Problem
Health literacy is a critical issue. Patients receive complex diagnoses and prescriptions but often don't understand:
- What's happening inside their body
- Why they need specific medications
- How their conditions relate to each other

### The Solution
A pipeline that:
1. **Ingests** FHIR patient data (conditions, medications, observations)
2. **Maps** data to a knowledge graph showing body systems and relationships
3. **Generates** plain-language explanations via Claude
4. **Creates** personalized educational videos via Wan 2.2

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EHR Data Explainer                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │   FHIR      │     │   Neo4j     │     │   Claude    │                  │
│   │  Data Load  │────▶│  Knowledge  │────▶│   AI        │                  │
│   │  (Synthea)  │     │    Graph    │     │ Explanations│                  │
│   └─────────────┘     └─────────────┘     └──────┬──────┘                  │
│                              │                    │                         │
│                              │                    ▼                         │
│   ┌─────────────┐     ┌──────┴──────┐     ┌─────────────┐                  │
│   │   React     │◀────│   FastAPI   │◀────│   Wan 2.2   │                  │
│   │    + Neovis │     │   Backend   │     │   Video Gen │                  │
│   └─────────────┘     └─────────────┘     └─────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow
```
Patient FHIR Bundle → Parse Conditions/Meds → Neo4j Graph → Claude Prompt
                                                                  ↓
                                           Video ← Wan 2.2 ← Video Prompt
```

---

## Tech Stack & Dependencies

### Backend (Python 3.11+)
```toml
# pyproject.toml
[project]
name = "ehr-health-explainer"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "neo4j>=5.17.0",
    "fhir.resources>=7.1.0",
    "fhirpy>=2.0.0",
    "anthropic>=0.18.0",
    "httpx>=0.26.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "requests>=2.31.0",
    "aiofiles>=23.2.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.1.0",
    "ruff>=0.2.0",
]
```

### Frontend (Node.js 20+)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "neovis.js": "^2.1.0",
    "axios": "^1.6.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### External Services
| Service | Purpose | Free Tier |
|---------|---------|-----------|
| **Neo4j AuraDB** | Knowledge graph database | Free tier available |
| **Anthropic Claude** | Explanation generation | Pay-per-use API |
| **Claude for Healthcare** | FHIR skill + ICD-10 + CMS connectors | Enterprise/Teams |
| **Hugging Face** | Wan 2.2 video model | Free inference API |
| **Synthea** | Sample FHIR patient data | Open source |

### 🆕 Claude for Healthcare (January 2026)

Anthropic just announced **Claude for Healthcare** with HIPAA-ready features:

| Connector/Skill | What It Does | Use Case |
|-----------------|--------------|----------|
| **FHIR Development Skill** | Native FHIR resource handling | Parse/generate FHIR bundles |
| **ICD-10 Connector** | Lookup diagnosis/procedure codes | Map conditions to body systems |
| **CMS Coverage Database** | Medicare coverage determinations | Prior auth, appeals |
| **NPI Registry** | Provider verification | Validate patient data sources |
| **PubMed Connector** | 35M+ biomedical papers | Evidence-based explanations |
| **HealthEx/Function** | Personal health data access | Patient lab results |
| **Apple/Android Health** | Fitness & health metrics | Comprehensive health view |

> ⚡ **Hackathon Advantage**: Using Claude's native FHIR skill means less custom code and more reliable FHIR parsing!

---

## Phase 1: Data Foundation

### 1.1 Generate Sample FHIR Data with Synthea

```bash
# Option A: Download pre-generated Synthea data
curl -L -o synthea_sample.zip \
  "https://syntheticmass.mitre.org/downloads/2023/synthea_sample_data_fhir_latest.zip"
unzip synthea_sample.zip -d data/fhir/

# Option B: Generate custom data (requires Java)
git clone https://github.com/synthetichealth/synthea.git
cd synthea
./run_synthea -p 50 Massachusetts  # Generate 50 patients
```

### 1.2 Neo4j Graph Schema

```cypher
// Node Types
(:Patient {id, name, birthDate, gender})
(:Condition {code, display, system, onsetDate})
(:Medication {code, display, system})
(:BodySystem {name, description})  // Heart, Pancreas, Brain, etc.
(:Explanation {text, readingLevel})

// Relationships
(Patient)-[:HAS_CONDITION]->(Condition)
(Patient)-[:TAKES_MEDICATION]->(Medication)
(Condition)-[:AFFECTS]->(BodySystem)
(Medication)-[:TREATS]->(Condition)
(Medication)-[:TARGETS]->(BodySystem)
(Condition)-[:RELATED_TO]->(Condition)  // Comorbidities
```

### 1.3 FHIR to Neo4j ETL Script

```python
# backend/etl/fhir_to_neo4j.py
from neo4j import GraphDatabase
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient
from fhir.resources.condition import Condition
from fhir.resources.medicationrequest import MedicationRequest
import json
from pathlib import Path

class FHIRToNeo4jLoader:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def load_patient_bundle(self, bundle_path: Path):
        """Load a FHIR Bundle into Neo4j"""
        with open(bundle_path) as f:
            bundle_data = json.load(f)
        
        bundle = Bundle.parse_obj(bundle_data)
        
        with self.driver.session() as session:
            for entry in bundle.entry:
                resource = entry.resource
                
                if resource.resource_type == "Patient":
                    self._create_patient(session, resource)
                elif resource.resource_type == "Condition":
                    self._create_condition(session, resource)
                elif resource.resource_type == "MedicationRequest":
                    self._create_medication(session, resource)
    
    def _create_patient(self, session, patient: Patient):
        query = """
        MERGE (p:Patient {id: $id})
        SET p.name = $name,
            p.birthDate = $birthDate,
            p.gender = $gender
        """
        name = f"{patient.name[0].given[0]} {patient.name[0].family}" if patient.name else "Unknown"
        session.run(query, 
            id=patient.id,
            name=name,
            birthDate=str(patient.birthDate) if patient.birthDate else None,
            gender=patient.gender
        )
    
    def _create_condition(self, session, condition: Condition):
        query = """
        MATCH (p:Patient {id: $patient_id})
        MERGE (c:Condition {code: $code})
        SET c.display = $display,
            c.system = $system
        MERGE (p)-[:HAS_CONDITION {onsetDate: $onset}]->(c)
        """
        coding = condition.code.coding[0] if condition.code.coding else None
        patient_ref = condition.subject.reference.split("/")[-1] if condition.subject else None
        
        if coding and patient_ref:
            session.run(query,
                patient_id=patient_ref,
                code=coding.code,
                display=coding.display,
                system=coding.system,
                onset=str(condition.onsetDateTime) if condition.onsetDateTime else None
            )
    
    def _create_medication(self, session, med_request: MedicationRequest):
        query = """
        MATCH (p:Patient {id: $patient_id})
        MERGE (m:Medication {code: $code})
        SET m.display = $display
        MERGE (p)-[:TAKES_MEDICATION]->(m)
        """
        coding = med_request.medicationCodeableConcept.coding[0] if med_request.medicationCodeableConcept else None
        patient_ref = med_request.subject.reference.split("/")[-1] if med_request.subject else None
        
        if coding and patient_ref:
            session.run(query,
                patient_id=patient_ref,
                code=coding.code,
                display=coding.display
            )
```

### 1.4 Medical Knowledge Base (Body System Mappings)

```python
# backend/knowledge/body_systems.py
"""
Maps medical conditions and medications to body systems.
This enables the graph to connect clinical data to anatomical visualizations.
"""

CONDITION_TO_BODY_SYSTEM = {
    # Cardiovascular
    "I48": {"system": "Heart", "subsystem": "Electrical System"},  # Atrial Fibrillation
    "I10": {"system": "Heart", "subsystem": "Blood Vessels"},      # Hypertension
    "I25": {"system": "Heart", "subsystem": "Coronary Arteries"},  # Coronary Heart Disease
    "I50": {"system": "Heart", "subsystem": "Muscle"},             # Heart Failure
    
    # Metabolic
    "E11": {"system": "Pancreas", "subsystem": "Insulin Production"},  # Type 2 Diabetes
    "E10": {"system": "Pancreas", "subsystem": "Insulin Production"},  # Type 1 Diabetes
    "E78": {"system": "Liver", "subsystem": "Cholesterol"},            # Hyperlipidemia
    
    # Respiratory
    "J45": {"system": "Lungs", "subsystem": "Airways"},           # Asthma
    "J44": {"system": "Lungs", "subsystem": "Airways"},           # COPD
    
    # Neurological
    "G40": {"system": "Brain", "subsystem": "Electrical Activity"},  # Epilepsy
    "G20": {"system": "Brain", "subsystem": "Motor Control"},        # Parkinson's
    "G30": {"system": "Brain", "subsystem": "Memory"},               # Alzheimer's
    
    # Complications (links conditions)
    "H36": {"system": "Eyes", "subsystem": "Blood Vessels"},      # Diabetic Retinopathy
    "N18": {"system": "Kidneys", "subsystem": "Filtering"},       # Chronic Kidney Disease
}

MEDICATION_TO_TARGET = {
    # Blood Thinners
    "B01AA03": {"target": "Blood", "action": "Prevents clotting"},      # Warfarin
    "B01AF01": {"target": "Blood", "action": "Prevents clotting"},      # Rivaroxaban
    
    # Diabetes Medications
    "A10BA02": {"target": "Liver/Muscles", "action": "Reduces glucose"},  # Metformin
    "A10AB01": {"target": "Body Cells", "action": "Enables glucose use"}, # Insulin
    
    # Heart Medications
    "C07AB02": {"target": "Heart", "action": "Slows heart rate"},        # Metoprolol
    "C09AA02": {"target": "Blood Vessels", "action": "Relaxes vessels"}, # Enalapril
    "C03CA01": {"target": "Kidneys", "action": "Removes excess fluid"},  # Furosemide
}

def get_body_system_for_condition(icd_code: str) -> dict:
    """Look up body system for an ICD-10 code prefix"""
    # Try exact match first, then prefix
    if icd_code in CONDITION_TO_BODY_SYSTEM:
        return CONDITION_TO_BODY_SYSTEM[icd_code]
    
    # Try first 3 characters (category level)
    prefix = icd_code[:3]
    return CONDITION_TO_BODY_SYSTEM.get(prefix, {"system": "Unknown", "subsystem": "Unknown"})
```

### 1.5 Load Body System Mappings into Neo4j

```cypher
// Create Body System nodes
CREATE (heart:BodySystem {name: 'Heart', description: 'Pumps blood throughout your body'})
CREATE (pancreas:BodySystem {name: 'Pancreas', description: 'Produces insulin to control blood sugar'})
CREATE (lungs:BodySystem {name: 'Lungs', description: 'Brings oxygen into your body'})
CREATE (brain:BodySystem {name: 'Brain', description: 'Controls all body functions'})
CREATE (kidneys:BodySystem {name: 'Kidneys', description: 'Filters waste from your blood'})
CREATE (liver:BodySystem {name: 'Liver', description: 'Processes nutrients and removes toxins'})
CREATE (eyes:BodySystem {name: 'Eyes', description: 'Enable vision'})
CREATE (blood:BodySystem {name: 'Blood', description: 'Carries oxygen and nutrients'});

// Link common conditions to body systems
MATCH (c:Condition), (b:BodySystem)
WHERE c.code STARTS WITH 'I48' AND b.name = 'Heart'
MERGE (c)-[:AFFECTS {subsystem: 'Electrical System'}]->(b);

MATCH (c:Condition), (b:BodySystem)
WHERE c.code STARTS WITH 'E11' AND b.name = 'Pancreas'
MERGE (c)-[:AFFECTS {subsystem: 'Insulin Production'}]->(b);

// Link medications to what they treat
MATCH (m:Medication {code: 'B01AA03'}), (c:Condition)
WHERE c.code STARTS WITH 'I48'
MERGE (m)-[:TREATS]->(c);
```

---

## Phase 2: Intelligence Layer

### 2.1 Patient Query Service

```python
# backend/services/patient_service.py
from neo4j import GraphDatabase
from typing import Optional
from pydantic import BaseModel

class PatientHealthSummary(BaseModel):
    patient_id: str
    patient_name: str
    conditions: list[dict]
    medications: list[dict]
    body_systems_affected: list[dict]
    condition_relationships: list[dict]

class PatientQueryService:
    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver
    
    def get_patient_health_summary(self, patient_id: str) -> PatientHealthSummary:
        """Get comprehensive health summary for explanation generation"""
        query = """
        MATCH (p:Patient {id: $patient_id})
        OPTIONAL MATCH (p)-[hc:HAS_CONDITION]->(c:Condition)
        OPTIONAL MATCH (c)-[:AFFECTS]->(bs:BodySystem)
        OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
        OPTIONAL MATCH (m)-[:TREATS]->(tc:Condition)
        OPTIONAL MATCH (c)-[:RELATED_TO]->(rc:Condition)
        
        RETURN p.name as patient_name,
               collect(DISTINCT {
                   code: c.code, 
                   display: c.display, 
                   onset: hc.onsetDate
               }) as conditions,
               collect(DISTINCT {
                   code: m.code, 
                   display: m.display,
                   treats: tc.display
               }) as medications,
               collect(DISTINCT {
                   system: bs.name,
                   description: bs.description
               }) as body_systems,
               collect(DISTINCT {
                   condition: c.display,
                   related_to: rc.display
               }) as relationships
        """
        
        with self.driver.session() as session:
            result = session.run(query, patient_id=patient_id).single()
            
            return PatientHealthSummary(
                patient_id=patient_id,
                patient_name=result["patient_name"],
                conditions=[c for c in result["conditions"] if c["code"]],
                medications=[m for m in result["medications"] if m["code"]],
                body_systems_affected=[bs for bs in result["body_systems"] if bs["system"]],
                condition_relationships=[r for r in result["relationships"] if r["related_to"]]
            )
    
    def get_all_patients(self, limit: int = 50) -> list[dict]:
        """Get list of all patients for selector UI"""
        query = """
        MATCH (p:Patient)
        OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
        RETURN p.id as id, 
               p.name as name, 
               p.gender as gender,
               count(c) as condition_count
        ORDER BY p.name
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            results = session.run(query, limit=limit)
            return [dict(r) for r in results]
```

### 2.2 Claude Explanation Generator (with Healthcare Connectors)

> 🆕 **New in January 2026**: Claude for Healthcare includes native ICD-10 lookup, 
> FHIR development skills, and PubMed access. This dramatically improves medical accuracy!

```python
# backend/services/explanation_service.py
import anthropic
from typing import Optional
from .patient_service import PatientHealthSummary

class ExplanationService:
    """
    Generates patient-friendly health explanations using Claude.
    
    With Claude for Healthcare (Enterprise/Teams), you get:
    - Native FHIR parsing and generation
    - ICD-10 code lookup for accurate condition mapping
    - PubMed integration for evidence-based explanations
    - CMS coverage database for treatment context
    """
    
    def __init__(self, api_key: str, use_healthcare_features: bool = False):
        self.client = anthropic.Anthropic(api_key=api_key)
        # Use Claude Opus 4.5 for best medical reasoning
        self.model = "claude-opus-4-20250514"  # Or claude-sonnet-4-20250514
        self.use_healthcare_features = use_healthcare_features
    
    async def generate_health_explanation(
        self, 
        summary: PatientHealthSummary,
        reading_level: str = "6th grade"
    ) -> dict:
        """Generate patient-friendly explanation of their health"""
        
        prompt = f"""You are a caring health educator explaining a patient's health situation 
in simple, reassuring terms. Use analogies and everyday language.

Patient: {summary.patient_name}

Their health conditions:
{self._format_conditions(summary.conditions)}

Their medications:
{self._format_medications(summary.medications)}

Body systems affected:
{self._format_body_systems(summary.body_systems_affected)}

How conditions relate to each other:
{self._format_relationships(summary.condition_relationships)}

Please create a warm, educational explanation at a {reading_level} reading level that:
1. Explains what's happening in their body (use simple anatomical terms)
2. Why each medication helps
3. How their conditions connect to each other
4. Reassuring tone - focus on what IS working and how treatment helps

IMPORTANT: You have access to the ICD-10 connector - use it to verify condition codes 
and get accurate clinical descriptions. You also have PubMed access for evidence-based 
explanations when relevant.

Format the response as JSON:
{{
    "greeting": "A warm opening addressing the patient",
    "body_explanation": "What's happening inside their body",
    "medication_explanation": "How their medications help",
    "connections": "How their conditions relate",
    "encouragement": "Positive, supportive closing message",
    "key_takeaways": ["3-4 simple bullet points to remember"]
}}
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON from response
        import json
        response_text = message.content[0].text
        return json.loads(response_text)
    
    async def generate_video_prompt(
        self, 
        summary: PatientHealthSummary,
        explanation: dict
    ) -> str:
        """Generate a detailed prompt for Wan 2.2 video generation"""
        
        prompt = f"""You are creating a prompt for an AI video generator to create a 
medical educational animation. The video should be calming, clear, and scientifically accurate 
while remaining accessible.

Patient's conditions: {[c['display'] for c in summary.conditions]}
Body systems involved: {[bs['system'] for bs in summary.body_systems_affected]}
Explanation context: {explanation['body_explanation']}

Create a detailed video generation prompt that describes:
1. The visual style (soft, medical illustration aesthetic, reassuring colors)
2. The anatomical elements to show (organs, systems, etc.)
3. The animation sequence (what happens, in what order)
4. The mood/tone (calming, educational)

Keep it under 200 words. Focus on ONE key concept from their health situation.
Do NOT include any text overlays or narration - just visual description.

Example format:
"Soft medical animation showing [organ/system]. [Color palette]. [What happens in the animation]. 
[How it illustrates the health concept]. Gentle, reassuring visual style suitable for patient education."
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def _format_conditions(self, conditions: list[dict]) -> str:
        return "\n".join([f"- {c['display']} (code: {c['code']})" for c in conditions])
    
    def _format_medications(self, medications: list[dict]) -> str:
        return "\n".join([f"- {m['display']} (treats: {m.get('treats', 'condition')})" for m in medications])
    
    def _format_body_systems(self, systems: list[dict]) -> str:
        return "\n".join([f"- {s['system']}: {s['description']}" for s in systems])
    
    def _format_relationships(self, relationships: list[dict]) -> str:
        if not relationships:
            return "No known direct relationships between conditions"
        return "\n".join([f"- {r['condition']} → {r['related_to']}" for r in relationships])
```

---

## Phase 3: Visual Generation

### 3.1 Wan 2.2 Video Service (Hugging Face Inference)

```python
# backend/services/video_service.py
import httpx
import asyncio
from pathlib import Path
import base64
from typing import Optional
import aiofiles

class VideoGenerationService:
    """
    Generates medical educational videos using Wan 2.2 model.
    
    Model options on Hugging Face:
    - Wan-AI/Wan2.2-T2V-A14B-Diffusers (Text-to-Video, 14B params)
    - Wan-AI/Wan2.2-TI2V-5B-Diffusers (Text+Image-to-Video, 5B params)
    
    For hackathon demo, we use the Hugging Face Inference API.
    For production, consider running locally with diffusers or using fal.ai.
    """
    
    def __init__(self, hf_token: str):
        self.hf_token = hf_token
        self.api_url = "https://api-inference.huggingface.co/models/Wan-AI/Wan2.2-T2V-A14B-Diffusers"
        self.headers = {"Authorization": f"Bearer {hf_token}"}
        self.output_dir = Path("generated_videos")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_video(
        self, 
        prompt: str,
        patient_id: str,
        num_frames: int = 49,  # ~2 seconds at 24fps
        height: int = 480,
        width: int = 832,
    ) -> dict:
        """
        Generate a video from a text prompt using Wan 2.2.
        
        Returns dict with:
        - video_path: Path to saved video
        - video_base64: Base64 encoded video for API response
        - generation_time: Time taken in seconds
        """
        import time
        start_time = time.time()
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_frames": num_frames,
                "height": height,
                "width": width,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
            }
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            # HF Inference API may need model warm-up
            for attempt in range(3):
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 503:
                    # Model loading, wait and retry
                    await asyncio.sleep(20)
                    continue
                    
                response.raise_for_status()
                break
            
            video_bytes = response.content
        
        # Save video
        video_filename = f"{patient_id}_{int(time.time())}.mp4"
        video_path = self.output_dir / video_filename
        
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(video_bytes)
        
        generation_time = time.time() - start_time
        
        return {
            "video_path": str(video_path),
            "video_base64": base64.b64encode(video_bytes).decode(),
            "generation_time": generation_time,
            "prompt_used": prompt
        }
    
    async def generate_with_reference_image(
        self,
        prompt: str,
        reference_image_path: Path,
        patient_id: str
    ) -> dict:
        """
        Generate video using image-to-video model for more control.
        Useful when we have medical diagram reference images.
        """
        # Use the image-to-video variant
        i2v_url = "https://api-inference.huggingface.co/models/Wan-AI/Wan2.2-I2V-A14B-Diffusers"
        
        async with aiofiles.open(reference_image_path, "rb") as f:
            image_bytes = await f.read()
        
        payload = {
            "inputs": {
                "prompt": prompt,
                "image": base64.b64encode(image_bytes).decode()
            },
            "parameters": {
                "num_frames": 49,
                "num_inference_steps": 30,
            }
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                i2v_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            video_bytes = response.content
        
        video_filename = f"{patient_id}_i2v_{int(time.time())}.mp4"
        video_path = self.output_dir / video_filename
        
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(video_bytes)
        
        return {
            "video_path": str(video_path),
            "video_base64": base64.b64encode(video_bytes).decode()
        }


# Alternative: Local generation with diffusers (requires GPU)
class LocalVideoGenerator:
    """
    For local generation with better control.
    Requires: pip install diffusers torch transformers accelerate
    Requires: NVIDIA GPU with ~24GB VRAM for 14B model
    """
    
    def __init__(self):
        self.pipe = None
    
    def load_model(self):
        from diffusers import WanPipeline
        import torch
        
        self.pipe = WanPipeline.from_pretrained(
            "Wan-AI/Wan2.2-T2V-A14B-Diffusers",
            torch_dtype=torch.float16
        )
        self.pipe.to("cuda")
        # Enable memory optimizations
        self.pipe.enable_model_cpu_offload()
    
    def generate(self, prompt: str, output_path: Path):
        from diffusers.utils import export_to_video
        
        if not self.pipe:
            self.load_model()
        
        video_frames = self.pipe(
            prompt=prompt,
            num_frames=49,
            height=480,
            width=832,
            num_inference_steps=30,
            guidance_scale=7.5
        ).frames[0]
        
        export_to_video(video_frames, output_path, fps=24)
        return output_path
```

### 3.2 Pre-generated Video Templates (Fallback)

For demo reliability, pre-generate videos for common conditions:

```python
# backend/services/video_templates.py
"""
Pre-generated video templates for common conditions.
Use when real-time generation isn't feasible or as fallback.
"""

VIDEO_TEMPLATES = {
    "atrial_fibrillation": {
        "video_url": "/static/videos/heart_afib.mp4",
        "description": "Heart with irregular electrical signals",
        "conditions": ["I48", "Atrial fibrillation", "AFib"]
    },
    "type2_diabetes": {
        "video_url": "/static/videos/pancreas_insulin.mp4",
        "description": "Pancreas and insulin regulation",
        "conditions": ["E11", "Type 2 diabetes", "T2DM"]
    },
    "hypertension": {
        "video_url": "/static/videos/blood_pressure.mp4",
        "description": "Blood vessels and pressure",
        "conditions": ["I10", "Hypertension", "High blood pressure"]
    },
    "heart_general": {
        "video_url": "/static/videos/heart_pumping.mp4",
        "description": "General heart function",
        "conditions": []  # Default for heart conditions
    },
    "medication_general": {
        "video_url": "/static/videos/medication_body.mp4",
        "description": "How medications work in the body",
        "conditions": []
    }
}

def get_template_for_condition(condition_code: str) -> dict | None:
    """Find best matching pre-generated video template"""
    for template_key, template in VIDEO_TEMPLATES.items():
        if condition_code in template["conditions"]:
            return template
    
    # Fallback to category
    if condition_code.startswith("I"):
        return VIDEO_TEMPLATES.get("heart_general")
    if condition_code.startswith("E1"):
        return VIDEO_TEMPLATES.get("type2_diabetes")
    
    return VIDEO_TEMPLATES.get("medication_general")
```

---

## Phase 4: Demo UI

### 4.1 FastAPI Backend

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os

from .services.patient_service import PatientQueryService
from .services.explanation_service import ExplanationService
from .services.video_service import VideoGenerationService
from neo4j import GraphDatabase

# Configuration
class Settings:
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    hf_token: str = os.getenv("HF_TOKEN", "")

settings = Settings()

# Service instances
driver = None
patient_service = None
explanation_service = None
video_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global driver, patient_service, explanation_service, video_service
    
    # Startup
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    patient_service = PatientQueryService(driver)
    explanation_service = ExplanationService(settings.anthropic_api_key)
    video_service = VideoGenerationService(settings.hf_token)
    
    yield
    
    # Shutdown
    driver.close()

app = FastAPI(
    title="EHR Data Explainer",
    description="Transform EHR data into visual health explanations",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/videos", StaticFiles(directory="generated_videos"), name="videos")

# Request/Response Models
class ExplainRequest(BaseModel):
    patient_id: str
    reading_level: str = "6th grade"
    generate_video: bool = True

class ExplainResponse(BaseModel):
    patient_name: str
    explanation: dict
    video_prompt: str | None
    video_url: str | None
    graph_data: dict

# Endpoints
@app.get("/api/patients")
async def list_patients(limit: int = 50):
    """Get list of all patients for selector UI"""
    return patient_service.get_all_patients(limit)

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    """Get patient health summary"""
    summary = patient_service.get_patient_health_summary(patient_id)
    return summary.dict()

@app.get("/api/patients/{patient_id}/graph")
async def get_patient_graph(patient_id: str):
    """Get graph data for Neovis.js visualization"""
    query = """
    MATCH path = (p:Patient {id: $patient_id})-[*1..2]-(connected)
    RETURN path
    """
    # Return Cypher query for Neovis.js to execute
    return {"cypher": query, "patient_id": patient_id}

@app.post("/api/explain", response_model=ExplainResponse)
async def explain_health(request: ExplainRequest):
    """Generate health explanation and optional video"""
    
    # Get patient data from graph
    summary = patient_service.get_patient_health_summary(request.patient_id)
    
    if not summary.conditions:
        raise HTTPException(404, "No conditions found for patient")
    
    # Generate explanation with Claude
    explanation = await explanation_service.generate_health_explanation(
        summary, 
        request.reading_level
    )
    
    video_prompt = None
    video_url = None
    
    if request.generate_video:
        # Generate video prompt
        video_prompt = await explanation_service.generate_video_prompt(
            summary, 
            explanation
        )
        
        # Generate video (or use template for demo)
        try:
            result = await video_service.generate_video(
                video_prompt,
                request.patient_id
            )
            video_url = f"/videos/{Path(result['video_path']).name}"
        except Exception as e:
            # Fallback to template
            from .services.video_templates import get_template_for_condition
            template = get_template_for_condition(summary.conditions[0]["code"])
            if template:
                video_url = template["video_url"]
    
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 4.2 React Frontend with Neovis.js

```tsx
// frontend/src/App.tsx
import { useState } from 'react'
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query'
import NeoVis from 'neovis.js'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

interface Patient {
  id: string
  name: string
  gender: string
  condition_count: number
}

interface Explanation {
  greeting: string
  body_explanation: string
  medication_explanation: string
  connections: string
  encouragement: string
  key_takeaways: string[]
}

interface ExplainResponse {
  patient_name: string
  explanation: Explanation
  video_prompt: string | null
  video_url: string | null
  graph_data: {
    conditions: any[]
    medications: any[]
    body_systems: any[]
  }
}

// Patient Selector Component
function PatientSelector({ onSelect }: { onSelect: (id: string) => void }) {
  const { data: patients, isLoading } = useQuery({
    queryKey: ['patients'],
    queryFn: () => axios.get<Patient[]>(`${API_BASE}/patients`).then(r => r.data)
  })

  if (isLoading) return <div className="animate-pulse">Loading patients...</div>

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold mb-3">Select a Patient</h2>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {patients?.map(patient => (
          <button
            key={patient.id}
            onClick={() => onSelect(patient.id)}
            className="w-full text-left p-3 rounded hover:bg-blue-50 transition flex justify-between"
          >
            <span>{patient.name}</span>
            <span className="text-gray-500 text-sm">
              {patient.condition_count} conditions
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

// Graph Visualization Component
function PatientGraph({ patientId }: { patientId: string }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || !patientId) return

    const config = {
      containerId: containerRef.current.id,
      neo4j: {
        serverUrl: import.meta.env.VITE_NEO4J_URL || 'bolt://localhost:7687',
        serverUser: import.meta.env.VITE_NEO4J_USER || 'neo4j',
        serverPassword: import.meta.env.VITE_NEO4J_PASSWORD || 'password',
      },
      labels: {
        Patient: {
          label: 'name',
          color: '#4F46E5',
          size: 30
        },
        Condition: {
          label: 'display',
          color: '#EF4444',
          size: 20
        },
        Medication: {
          label: 'display',
          color: '#10B981',
          size: 20
        },
        BodySystem: {
          label: 'name',
          color: '#F59E0B',
          size: 25
        }
      },
      relationships: {
        HAS_CONDITION: { color: '#EF4444' },
        TAKES_MEDICATION: { color: '#10B981' },
        AFFECTS: { color: '#F59E0B' },
        TREATS: { color: '#6366F1', dashes: true }
      },
      initialCypher: `
        MATCH (p:Patient {id: '${patientId}'})-[r]-(connected)
        OPTIONAL MATCH (connected)-[r2]-(secondary)
        WHERE NOT secondary:Patient
        RETURN p, r, connected, r2, secondary
        LIMIT 50
      `
    }

    const viz = new NeoVis(config)
    viz.render()

    return () => viz.clearNetwork()
  }, [patientId])

  return (
    <div 
      id="graph-container" 
      ref={containerRef}
      className="w-full h-96 border rounded-lg bg-gray-50"
    />
  )
}

// Explanation Display Component
function ExplanationDisplay({ explanation }: { explanation: Explanation }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-4">
      <p className="text-lg text-blue-600 font-medium">{explanation.greeting}</p>
      
      <div>
        <h3 className="font-semibold text-gray-700 mb-2">🫀 What's Happening in Your Body</h3>
        <p className="text-gray-600">{explanation.body_explanation}</p>
      </div>
      
      <div>
        <h3 className="font-semibold text-gray-700 mb-2">💊 How Your Medications Help</h3>
        <p className="text-gray-600">{explanation.medication_explanation}</p>
      </div>
      
      <div>
        <h3 className="font-semibold text-gray-700 mb-2">🔗 How Things Connect</h3>
        <p className="text-gray-600">{explanation.connections}</p>
      </div>
      
      <div className="bg-green-50 p-4 rounded-lg">
        <p className="text-green-700">{explanation.encouragement}</p>
      </div>
      
      <div>
        <h3 className="font-semibold text-gray-700 mb-2">📝 Key Takeaways</h3>
        <ul className="list-disc list-inside text-gray-600 space-y-1">
          {explanation.key_takeaways.map((point, i) => (
            <li key={i}>{point}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

// Video Player Component
function VideoPlayer({ videoUrl }: { videoUrl: string }) {
  return (
    <div className="bg-black rounded-lg overflow-hidden">
      <video 
        controls 
        autoPlay 
        loop
        className="w-full"
        src={`http://localhost:8000${videoUrl}`}
      >
        Your browser does not support video playback.
      </video>
    </div>
  )
}

// Main App Component
function HealthExplainer() {
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  
  const explainMutation = useMutation({
    mutationFn: (patientId: string) => 
      axios.post<ExplainResponse>(`${API_BASE}/explain`, {
        patient_id: patientId,
        reading_level: '6th grade',
        generate_video: true
      }).then(r => r.data)
  })

  const handleExplain = () => {
    if (selectedPatientId) {
      explainMutation.mutate(selectedPatientId)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            🏥 Health Explainer
          </h1>
          <p className="text-gray-600 mt-2">
            Understanding your health, simply explained
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Patient Selection */}
          <div className="space-y-4">
            <PatientSelector onSelect={setSelectedPatientId} />
            
            {selectedPatientId && (
              <button
                onClick={handleExplain}
                disabled={explainMutation.isPending}
                className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg 
                         hover:bg-blue-700 transition disabled:opacity-50"
              >
                {explainMutation.isPending ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="animate-spin">⏳</span> Generating...
                  </span>
                ) : (
                  '✨ Explain My Health'
                )}
              </button>
            )}
          </div>

          {/* Middle Column - Graph */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Health Connections</h2>
            {selectedPatientId ? (
              <PatientGraph patientId={selectedPatientId} />
            ) : (
              <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg border">
                <p className="text-gray-500">Select a patient to view their health graph</p>
              </div>
            )}
          </div>

          {/* Right Column - Video & Explanation */}
          <div className="space-y-4">
            {explainMutation.data?.video_url && (
              <VideoPlayer videoUrl={explainMutation.data.video_url} />
            )}
            
            {explainMutation.data?.explanation && (
              <ExplanationDisplay explanation={explainMutation.data.explanation} />
            )}
            
            {!explainMutation.data && (
              <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
                <p>Click "Explain My Health" to generate a personalized explanation</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// App Entry
const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <HealthExplainer />
    </QueryClientProvider>
  )
}
```

---

## Project Structure

```
ehr-health-explainer/
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Settings/configuration
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── fhir_to_neo4j.py      # FHIR data loader
│   │   └── seed_knowledge.py      # Body system mappings
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── body_systems.py        # Medical knowledge base
│   │   └── condition_mappings.py  # ICD → Body system
│   ├── services/
│   │   ├── __init__.py
│   │   ├── patient_service.py     # Neo4j queries
│   │   ├── explanation_service.py # Claude integration
│   │   ├── video_service.py       # Wan 2.2 integration
│   │   └── video_templates.py     # Pre-generated fallbacks
│   └── tests/
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── PatientSelector.tsx
│   │   │   ├── PatientGraph.tsx
│   │   │   ├── ExplanationDisplay.tsx
│   │   │   └── VideoPlayer.tsx
│   │   └── hooks/
│   │       └── usePatientData.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── data/
│   ├── fhir/                      # Synthea FHIR bundles
│   └── knowledge/                 # Medical knowledge CSVs
├── static/
│   └── videos/                    # Pre-generated template videos
├── generated_videos/              # Runtime generated videos
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Environment Setup

### .env.example
```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
# Or for Neo4j AuraDB: neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Hugging Face (for Wan 2.2)
HF_TOKEN=hf_...

# Frontend (Vite)
VITE_NEO4J_URL=bolt://localhost:7687
VITE_NEO4J_USER=neo4j
VITE_NEO4J_PASSWORD=your-password
VITE_API_URL=http://localhost:8000
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.17.0
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
    env_file:
      - .env
    depends_on:
      - neo4j
    volumes:
      - ./generated_videos:/app/generated_videos
      - ./static:/app/static

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  neo4j_data:
```

---

## API Keys & Services

### Neo4j AuraDB (Free Tier)
1. Go to https://neo4j.com/cloud/aura-free/
2. Create free instance
3. Save connection URI and credentials
4. Use `neo4j+s://` URI scheme

### Anthropic Claude API
1. Go to https://console.anthropic.com/
2. Create API key
3. Add credits (pay-per-use)
4. **Recommended model**: `claude-opus-4-20250514` (best medical reasoning)
5. Alternative: `claude-sonnet-4-20250514` (faster, cheaper)

### 🆕 Claude for Healthcare (Enterprise/Teams)
For full healthcare capabilities:
1. Contact Anthropic sales for Enterprise/Teams plan
2. Enable **Claude for Healthcare** package
3. Get access to:
   - **FHIR Development Skill** - Native FHIR resource handling
   - **ICD-10 Connector** - Diagnosis/procedure code lookup
   - **CMS Coverage Database** - Medicare policy access
   - **PubMed Connector** - 35M+ biomedical papers
4. HIPAA-ready environment included

> 💡 For hackathon: Standard API works great! Healthcare connectors add extra accuracy.

### Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Create access token with `read` scope
3. For Wan 2.2, you may need to accept model terms at:
   - https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers

---

## Sample Data & Testing

### Quick Test: Load Sample Patient
```python
# scripts/load_sample_data.py
from backend.etl.fhir_to_neo4j import FHIRToNeo4jLoader
from pathlib import Path

loader = FHIRToNeo4jLoader(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Load Synthea sample bundles
data_dir = Path("data/fhir")
for bundle_file in data_dir.glob("*.json"):
    print(f"Loading {bundle_file.name}...")
    loader.load_patient_bundle(bundle_file)

loader.close()
print("Done!")
```

### Test API Endpoints
```bash
# List patients
curl http://localhost:8000/api/patients

# Get patient summary
curl http://localhost:8000/api/patients/PATIENT_ID

# Generate explanation
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "PATIENT_ID", "generate_video": false}'
```

---

## Deployment

### Demo Day Checklist
- [ ] Pre-load 5-10 diverse patient records
- [ ] Pre-generate video templates for common conditions
- [ ] Test full flow: Patient → Graph → Explanation → Video
- [ ] Have fallback if video generation is slow
- [ ] Prepare 2-3 "golden path" patients that showcase features

### Production Considerations
- Use Neo4j AuraDB Professional for production
- Consider fal.ai or Replicate for faster video generation
- Add authentication/authorization
- Implement caching for explanations
- Add rate limiting for AI API calls

---

## Hackathon Tips

### Demo Strategy
1. **Start with a patient story**: "Meet Maria, a 58-year-old with Type 2 Diabetes..."
2. **Show the graph**: Visualize the relationships
3. **Generate explanation**: Show Claude creating simple language
4. **Play the video**: The visual "aha" moment
5. **Highlight the impact**: Health literacy statistics

### If Video Generation is Slow
- Use pre-generated templates
- Show the video prompt and explain what would be generated
- Have a "gallery" of pre-made videos for different conditions

### Judges Love
- Live data from the graph database
- The FHIR → Graph → AI → Video pipeline
- Clear patient impact story
- Using multiple sponsor technologies well
- **🆕 Claude for Healthcare integration** (just announced Jan 2026!)
- Native FHIR skill + ICD-10 connector = cutting-edge tech

---

## Resources & References

### GitHub Repositories
- [synthetichealth/synthea](https://github.com/synthetichealth/synthea) - Patient data generator
- [neo4j-contrib/neovis.js](https://github.com/neo4j-contrib/neovis.js) - Graph visualization
- [asanmateu/medgraph-ai](https://github.com/asanmateu/medgraph-ai) - Healthcare RAG reference
- [gptechday/openai-academy-kg-recipe](https://github.com/gptechday/openai-academy-kg-recipe) - Synthea + Neo4j recipe

### Wan 2.2 Models
- [Wan-AI/Wan2.2-T2V-A14B-Diffusers](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers) - Text-to-Video
- [Wan-AI/Wan2.2-I2V-A14B-Diffusers](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B-Diffusers) - Image-to-Video

### Documentation
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Claude for Healthcare](https://www.anthropic.com/news/advancing-claude-in-healthcare) - New Jan 2026!
- [Claude Healthcare Tutorial Guides](https://docs.anthropic.com/healthcare/tutorials)
- [Claude FHIR Development Skill](https://docs.anthropic.com/healthcare/fhir-skill)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index)

### Claude for Healthcare Benchmarks (Jan 2026)
| Benchmark | Claude Opus 4.5 | Notes |
|-----------|-----------------|-------|
| MedCalc | State-of-art | Medical calculations with Python |
| MedAgentBench | State-of-art | Medical agent tasks (Stanford) |
| Honesty Evals | Improved | Reduced factual hallucinations |

### Life Sciences Connectors (Also Available)
| Connector | Purpose |
|-----------|---------|
| **ClinicalTrials.gov** | Clinical trial registry data |
| **bioRxiv/medRxiv** | Latest preprints |
| **ChEMBL** | Drug & compound database |
| **Open Targets** | Drug target identification |
| **Medidata** | Clinical trial operations |

---

**Good luck at the hackathon! 🚀**
