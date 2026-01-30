#!/usr/bin/env python3
"""
Sample Data Loader Script

Downloads Synthea sample data and loads it into Neo4j.
Run this after starting the Docker containers.

Usage:
    python scripts/load_sample_data.py
"""

import asyncio
import json
import os
import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from neo4j import GraphDatabase
from etl.fhir_to_neo4j import FHIRToNeo4jLoader

# Synthea sample data URL (small dataset)
SYNTHEA_SAMPLE_URL = "https://synthetichealth.github.io/synthea-sample-data/downloads/synthea_sample_data_fhir_r4_sep2019.zip"

# Local paths
DATA_DIR = Path(__file__).parent.parent / "data"
SAMPLE_ZIP = DATA_DIR / "synthea_sample.zip"
SAMPLE_DIR = DATA_DIR / "synthea_samples"


def download_synthea_data():
    """Download Synthea sample data if not present."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if SAMPLE_DIR.exists() and any(SAMPLE_DIR.glob("*.json")):
        print(f"✅ Sample data already exists at {SAMPLE_DIR}")
        return
    
    print(f"📥 Downloading Synthea sample data...")
    print(f"   URL: {SYNTHEA_SAMPLE_URL}")
    
    def progress_hook(count, block_size, total_size):
        percent = min(100, int(count * block_size * 100 / total_size))
        sys.stdout.write(f"\r   Progress: {percent}%")
        sys.stdout.flush()
    
    urlretrieve(SYNTHEA_SAMPLE_URL, SAMPLE_ZIP, progress_hook)
    print("\n✅ Download complete!")
    
    print("📦 Extracting data...")
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(SAMPLE_ZIP, 'r') as zip_ref:
        # Extract only FHIR bundle JSON files
        for file_info in zip_ref.filelist:
            if file_info.filename.endswith('.json') and 'fhir' in file_info.filename.lower():
                # Extract to flat directory
                file_info.filename = os.path.basename(file_info.filename)
                zip_ref.extract(file_info, SAMPLE_DIR)
    
    print(f"✅ Extracted to {SAMPLE_DIR}")
    
    # Clean up zip file
    SAMPLE_ZIP.unlink()


def create_sample_bundles():
    """Create sample FHIR bundles if Synthea download fails."""
    print("🔧 Creating sample FHIR bundles...")
    
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sample Patient 1: Diabetes with Hypertension
    bundle1 = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-001",
                    "name": [{"given": ["Maria"], "family": "Garcia"}],
                    "gender": "female",
                    "birthDate": "1965-03-15"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-001",
                    "subject": {"reference": "Patient/patient-001"},
                    "code": {
                        "coding": [{"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes mellitus type 2"}],
                        "text": "Type 2 Diabetes"
                    },
                    "clinicalStatus": {"coding": [{"code": "active"}]},
                    "onsetDateTime": "2015-06-20"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-002",
                    "subject": {"reference": "Patient/patient-001"},
                    "code": {
                        "coding": [{"system": "http://snomed.info/sct", "code": "38341003", "display": "Hypertensive disorder"}],
                        "text": "Essential Hypertension"
                    },
                    "clinicalStatus": {"coding": [{"code": "active"}]},
                    "onsetDateTime": "2018-01-10"
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "med-001",
                    "subject": {"reference": "Patient/patient-001"},
                    "status": "active",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975", "display": "Metformin 500 MG"}],
                        "text": "Metformin 500mg"
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "med-002",
                    "subject": {"reference": "Patient/patient-001"},
                    "status": "active",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "197884", "display": "Lisinopril 10 MG"}],
                        "text": "Lisinopril 10mg"
                    }
                }
            }
        ]
    }
    
    # Sample Patient 2: Heart Disease
    bundle2 = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-002",
                    "name": [{"given": ["James"], "family": "Wilson"}],
                    "gender": "male",
                    "birthDate": "1958-11-22"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-003",
                    "subject": {"reference": "Patient/patient-002"},
                    "code": {
                        "coding": [{"system": "http://snomed.info/sct", "code": "53741008", "display": "Coronary arteriosclerosis"}],
                        "text": "Coronary Artery Disease"
                    },
                    "clinicalStatus": {"coding": [{"code": "active"}]},
                    "onsetDateTime": "2019-04-15"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-004",
                    "subject": {"reference": "Patient/patient-002"},
                    "code": {
                        "coding": [{"system": "http://snomed.info/sct", "code": "13644009", "display": "High cholesterol"}],
                        "text": "Hypercholesterolemia"
                    },
                    "clinicalStatus": {"coding": [{"code": "active"}]},
                    "onsetDateTime": "2017-08-01"
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "med-003",
                    "subject": {"reference": "Patient/patient-002"},
                    "status": "active",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "617312", "display": "Atorvastatin 20 MG"}],
                        "text": "Atorvastatin 20mg"
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "med-004",
                    "subject": {"reference": "Patient/patient-002"},
                    "status": "active",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "308416", "display": "Aspirin 81 MG"}],
                        "text": "Aspirin 81mg"
                    }
                }
            }
        ]
    }
    
    # Sample Patient 3: Respiratory Issues
    bundle3 = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-003",
                    "name": [{"given": ["Sarah"], "family": "Johnson"}],
                    "gender": "female",
                    "birthDate": "1972-07-08"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-005",
                    "subject": {"reference": "Patient/patient-003"},
                    "code": {
                        "coding": [{"system": "http://snomed.info/sct", "code": "195967001", "display": "Asthma"}],
                        "text": "Asthma"
                    },
                    "clinicalStatus": {"coding": [{"code": "active"}]},
                    "onsetDateTime": "1990-05-12"
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "med-005",
                    "subject": {"reference": "Patient/patient-003"},
                    "status": "active",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "896188", "display": "Albuterol 90 MCG/ACT inhaler"}],
                        "text": "Albuterol Inhaler"
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "med-006",
                    "subject": {"reference": "Patient/patient-003"},
                    "status": "active",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "895994", "display": "Fluticasone propionate 250 MCG/ACT inhaler"}],
                        "text": "Fluticasone Inhaler"
                    }
                }
            }
        ]
    }
    
    # Write sample bundles
    for i, bundle in enumerate([bundle1, bundle2, bundle3], 1):
        filepath = SAMPLE_DIR / f"sample_patient_{i}.json"
        with open(filepath, 'w') as f:
            json.dump(bundle, f, indent=2)
        print(f"   Created {filepath.name}")
    
    print("✅ Sample bundles created!")


async def load_data_to_neo4j():
    """Load FHIR bundles into Neo4j."""
    # Get Neo4j connection details from environment or use defaults
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "healthgraph123")
    
    print(f"\n🔌 Connecting to Neo4j at {neo4j_uri}...")
    
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        driver.verify_connectivity()
        print("✅ Connected to Neo4j!")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print("\n💡 Make sure Neo4j is running:")
        print("   docker compose up -d neo4j")
        return
    
    # Create loader and load bundles
    loader = FHIRToNeo4jLoader(driver)
    
    # Find FHIR bundle files
    bundle_files = list(SAMPLE_DIR.glob("*.json"))
    if not bundle_files:
        print("❌ No FHIR bundle files found!")
        return
    
    print(f"\n📊 Found {len(bundle_files)} FHIR bundles to load")
    
    # Load each bundle
    loaded = 0
    for bundle_file in bundle_files[:10]:  # Limit to 10 for demo
        print(f"   Loading {bundle_file.name}...", end=" ")
        try:
            with open(bundle_file) as f:
                bundle = json.load(f)
            
            await loader.load_bundle(bundle)
            print("✅")
            loaded += 1
        except Exception as e:
            print(f"⚠️  Error: {e}")
    
    print(f"\n✅ Successfully loaded {loaded} bundles into Neo4j!")
    
    # Show summary
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Patient) WITH count(p) as patients
            MATCH (c:Condition) WITH patients, count(c) as conditions
            MATCH (m:Medication) WITH patients, conditions, count(m) as medications
            MATCH (bs:BodySystem) WITH patients, conditions, medications, count(bs) as systems
            RETURN patients, conditions, medications, systems
        """)
        record = result.single()
        if record:
            print(f"\n📈 Database Summary:")
            print(f"   👤 Patients: {record['patients']}")
            print(f"   🏥 Conditions: {record['conditions']}")
            print(f"   💊 Medications: {record['medications']}")
            print(f"   🫀 Body Systems: {record['systems']}")
    
    driver.close()


async def main():
    """Main entry point."""
    print("=" * 50)
    print("🏥 EHR Data Explainer - Data Loader")
    print("=" * 50)
    
    # Try to download Synthea data, fall back to sample bundles
    try:
        download_synthea_data()
    except Exception as e:
        print(f"⚠️  Could not download Synthea data: {e}")
        create_sample_bundles()
    
    # Load data into Neo4j
    await load_data_to_neo4j()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete! You can now:")
    print("   1. Open http://localhost:5173 for the frontend")
    print("   2. Open http://localhost:7474 for Neo4j Browser")
    print("   3. Access API at http://localhost:8000/docs")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
