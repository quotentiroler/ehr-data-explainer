"""
FHIR to Neo4j ETL Loader.

Loads FHIR R4 resources (Patient, Condition, MedicationRequest) into Neo4j
and creates relationships with body systems knowledge graph.
"""
import json
from pathlib import Path
from typing import Optional

from neo4j import GraphDatabase
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient
from fhir.resources.condition import Condition
from fhir.resources.medicationrequest import MedicationRequest

from .body_systems import CONDITION_TO_BODY_SYSTEM, MEDICATION_TO_TARGET


class FHIRToNeo4jLoader:
    """
    Loads FHIR resources into Neo4j knowledge graph.
    
    Creates nodes for:
    - Patient
    - Condition
    - Medication
    - BodySystem (from knowledge base)
    
    And relationships:
    - (Patient)-[:HAS_CONDITION]->(Condition)
    - (Patient)-[:TAKES_MEDICATION]->(Medication)
    - (Condition)-[:AFFECTS]->(BodySystem)
    - (Medication)-[:TREATS]->(Condition)
    - (Medication)-[:TARGETS]->(BodySystem)
    """
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._init_constraints()
    
    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()
    
    def _init_constraints(self):
        """Create uniqueness constraints for node IDs."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Condition) REQUIRE c.code IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Medication) REQUIRE m.code IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (bs:BodySystem) REQUIRE bs.name IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    print(f"Constraint may already exist: {e}")
    
    def load_bundle_file(self, bundle_path: Path) -> dict:
        """
        Load a FHIR Bundle JSON file into Neo4j.
        
        Args:
            bundle_path: Path to FHIR Bundle JSON file
            
        Returns:
            Dictionary with counts of loaded resources
        """
        with open(bundle_path) as f:
            bundle_data = json.load(f)
        
        return self.load_bundle(bundle_data)
    
    def load_bundle(self, bundle_data: dict) -> dict:
        """
        Load a FHIR Bundle into Neo4j.
        
        Args:
            bundle_data: Parsed FHIR Bundle dictionary
            
        Returns:
            Dictionary with counts of loaded resources
        """
        bundle = Bundle.model_validate(bundle_data)
        
        stats = {
            "patients": 0,
            "conditions": 0,
            "medications": 0,
            "body_systems": 0
        }
        
        if not bundle.entry:
            return stats
        
        with self.driver.session() as session:
            for entry in bundle.entry:
                if not entry.resource:
                    continue
                    
                resource = entry.resource
                resource_type = resource.resource_type
                
                if resource_type == "Patient":
                    self._create_patient(session, resource)
                    stats["patients"] += 1
                elif resource_type == "Condition":
                    self._create_condition(session, resource)
                    stats["conditions"] += 1
                elif resource_type == "MedicationRequest":
                    self._create_medication(session, resource)
                    stats["medications"] += 1
        
        return stats
    
    def _create_patient(self, session, patient: Patient):
        """Create a Patient node in Neo4j."""
        query = """
        MERGE (p:Patient {id: $id})
        SET p.name = $name,
            p.birthDate = $birthDate,
            p.gender = $gender
        """
        
        # Extract name
        name = "Unknown"
        if patient.name and len(patient.name) > 0:
            name_obj = patient.name[0]
            given = name_obj.given[0] if name_obj.given else ""
            family = name_obj.family or ""
            name = f"{given} {family}".strip()
        
        session.run(query,
            id=patient.id,
            name=name,
            birthDate=str(patient.birthDate) if patient.birthDate else None,
            gender=patient.gender
        )
    
    def _create_condition(self, session, condition: Condition):
        """Create a Condition node and link to Patient and BodySystem."""
        if not condition.code or not condition.code.coding:
            return
        
        coding = condition.code.coding[0]
        
        # Get patient reference
        patient_ref = None
        if condition.subject and condition.subject.reference:
            patient_ref = condition.subject.reference.split("/")[-1]
        
        if not patient_ref:
            return
        
        # Create condition and link to patient
        query = """
        MATCH (p:Patient {id: $patient_id})
        MERGE (c:Condition {code: $code})
        SET c.display = $display,
            c.system = $system
        MERGE (p)-[:HAS_CONDITION {onsetDate: $onset}]->(c)
        """
        
        onset = None
        if condition.onsetDateTime:
            onset = str(condition.onsetDateTime)
        
        session.run(query,
            patient_id=patient_ref,
            code=coding.code,
            display=coding.display or coding.code,
            system=coding.system,
            onset=onset
        )
        
        # Link to body system if we have a mapping
        body_system = CONDITION_TO_BODY_SYSTEM.get(coding.code[:3])  # Try category
        if not body_system:
            body_system = CONDITION_TO_BODY_SYSTEM.get(coding.code)  # Try exact
        
        if body_system:
            self._link_condition_to_body_system(session, coding.code, body_system)
    
    def _link_condition_to_body_system(self, session, condition_code: str, body_system: dict):
        """Create relationship between Condition and BodySystem."""
        query = """
        MATCH (c:Condition {code: $code})
        MERGE (bs:BodySystem {name: $system_name})
        ON CREATE SET bs.description = $description
        MERGE (c)-[:AFFECTS {subsystem: $subsystem}]->(bs)
        """
        
        session.run(query,
            code=condition_code,
            system_name=body_system["system"],
            description=body_system.get("description", ""),
            subsystem=body_system.get("subsystem", "")
        )
    
    def _create_medication(self, session, med_request: MedicationRequest):
        """Create a Medication node and link to Patient."""
        if not med_request.medicationCodeableConcept:
            return
        
        if not med_request.medicationCodeableConcept.coding:
            return
        
        coding = med_request.medicationCodeableConcept.coding[0]
        
        # Get patient reference
        patient_ref = None
        if med_request.subject and med_request.subject.reference:
            patient_ref = med_request.subject.reference.split("/")[-1]
        
        if not patient_ref:
            return
        
        # Create medication and link to patient
        query = """
        MATCH (p:Patient {id: $patient_id})
        MERGE (m:Medication {code: $code})
        SET m.display = $display,
            m.system = $system
        MERGE (p)-[:TAKES_MEDICATION]->(m)
        """
        
        session.run(query,
            patient_id=patient_ref,
            code=coding.code,
            display=coding.display or coding.code,
            system=coding.system
        )
        
        # Link to body system target if we have a mapping
        target = MEDICATION_TO_TARGET.get(coding.code)
        if target:
            self._link_medication_to_target(session, coding.code, target)
    
    def _link_medication_to_target(self, session, med_code: str, target: dict):
        """Create relationship between Medication and BodySystem target."""
        query = """
        MATCH (m:Medication {code: $code})
        MERGE (bs:BodySystem {name: $target_name})
        MERGE (m)-[:TARGETS {action: $action}]->(bs)
        """
        
        session.run(query,
            code=med_code,
            target_name=target["target"],
            action=target.get("action", "")
        )
    
    def load_directory(self, dir_path: Path) -> dict:
        """
        Load all FHIR Bundle JSON files from a directory.
        
        Args:
            dir_path: Path to directory containing FHIR JSON files
            
        Returns:
            Aggregated stats from all loaded files
        """
        total_stats = {
            "patients": 0,
            "conditions": 0,
            "medications": 0,
            "files_processed": 0
        }
        
        for json_file in dir_path.glob("*.json"):
            try:
                stats = self.load_bundle_file(json_file)
                for key in ["patients", "conditions", "medications"]:
                    total_stats[key] += stats.get(key, 0)
                total_stats["files_processed"] += 1
                print(f"✅ Loaded {json_file.name}")
            except Exception as e:
                print(f"❌ Failed to load {json_file.name}: {e}")
        
        return total_stats


def main():
    """CLI for loading FHIR data."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fhir_to_neo4j.py <path_to_fhir_bundles>")
        sys.exit(1)
    
    data_path = Path(sys.argv[1])
    
    # Load from environment or use defaults
    import os
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    print(f"🔌 Connecting to Neo4j at {uri}...")
    loader = FHIRToNeo4jLoader(uri, user, password)
    
    try:
        if data_path.is_file():
            stats = loader.load_bundle_file(data_path)
        else:
            stats = loader.load_directory(data_path)
        
        print("\n📊 Loading complete!")
        print(f"   Patients: {stats.get('patients', 0)}")
        print(f"   Conditions: {stats.get('conditions', 0)}")
        print(f"   Medications: {stats.get('medications', 0)}")
    finally:
        loader.close()


if __name__ == "__main__":
    main()
