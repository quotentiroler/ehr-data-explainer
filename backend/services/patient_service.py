"""
Patient Query Service - Neo4j graph queries for patient health data.
"""
from neo4j import GraphDatabase
from pydantic import BaseModel


class PatientHealthSummary(BaseModel):
    """Structured summary of a patient's health data from the graph."""
    patient_id: str
    patient_name: str
    conditions: list[dict]
    medications: list[dict]
    body_systems_affected: list[dict]
    condition_relationships: list[dict]


class PatientQueryService:
    """Service for querying patient data from Neo4j knowledge graph."""
    
    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver
    
    def get_patient_health_summary(self, patient_id: str) -> PatientHealthSummary:
        """
        Get comprehensive health summary for explanation generation.
        
        Returns patient's conditions, medications, affected body systems,
        and relationships between conditions.
        """
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
            
            if not result or not result["patient_name"]:
                raise ValueError(f"Patient {patient_id} not found")
            
            return PatientHealthSummary(
                patient_id=patient_id,
                patient_name=result["patient_name"] or "Unknown",
                conditions=[c for c in result["conditions"] if c.get("code")],
                medications=[m for m in result["medications"] if m.get("code")],
                body_systems_affected=[bs for bs in result["body_systems"] if bs.get("system")],
                condition_relationships=[r for r in result["relationships"] if r.get("related_to")]
            )
    
    def get_all_patients(self, limit: int = 50) -> list[dict]:
        """Get list of all patients for selector UI."""
        query = """
        MATCH (p:Patient)
        OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
        WITH p, count(c) as condition_count
        RETURN p.id as id, 
               p.name as name, 
               p.gender as gender,
               p.birthDate as birthDate,
               condition_count
        ORDER BY p.name
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            results = session.run(query, limit=limit)
            return [dict(r) for r in results]
    
    def get_patient_conditions(self, patient_id: str) -> list[dict]:
        """Get detailed conditions for a patient."""
        query = """
        MATCH (p:Patient {id: $patient_id})-[hc:HAS_CONDITION]->(c:Condition)
        OPTIONAL MATCH (c)-[:AFFECTS]->(bs:BodySystem)
        RETURN c.code as code,
               c.display as display,
               c.system as coding_system,
               hc.onsetDate as onset_date,
               collect(bs.name) as body_systems
        """
        
        with self.driver.session() as session:
            results = session.run(query, patient_id=patient_id)
            return [dict(r) for r in results]
    
    def get_patient_medications(self, patient_id: str) -> list[dict]:
        """Get detailed medications for a patient."""
        query = """
        MATCH (p:Patient {id: $patient_id})-[:TAKES_MEDICATION]->(m:Medication)
        OPTIONAL MATCH (m)-[:TREATS]->(c:Condition)
        OPTIONAL MATCH (m)-[:TARGETS]->(bs:BodySystem)
        RETURN m.code as code,
               m.display as display,
               collect(DISTINCT c.display) as treats_conditions,
               collect(DISTINCT bs.name) as targets_body_systems
        """
        
        with self.driver.session() as session:
            results = session.run(query, patient_id=patient_id)
            return [dict(r) for r in results]
    
    def search_patients(self, search_term: str, limit: int = 20) -> list[dict]:
        """Search patients by name."""
        query = """
        MATCH (p:Patient)
        WHERE toLower(p.name) CONTAINS toLower($search_term)
        OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
        WITH p, count(c) as condition_count
        RETURN p.id as id,
               p.name as name,
               p.gender as gender,
               condition_count
        ORDER BY p.name
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            results = session.run(query, search_term=search_term, limit=limit)
            return [dict(r) for r in results]
