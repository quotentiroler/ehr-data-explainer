#!/usr/bin/env python3
"""Quick data loader - loads sample patients directly into Neo4j without FHIR parsing."""

from neo4j import GraphDatabase

# Neo4j connection
uri = "bolt://localhost:7687"
user = "neo4j"
password = "healthgraph123"

driver = GraphDatabase.driver(uri, auth=(user, password))

def clear_and_load():
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("✅ Cleared existing data")
        
        # Create body systems
        session.run("""
            CREATE (bs1:BodySystem {name: 'Cardiovascular', description: 'Heart and blood vessels'})
            CREATE (bs2:BodySystem {name: 'Endocrine', description: 'Hormone-producing glands'})
            CREATE (bs3:BodySystem {name: 'Respiratory', description: 'Lungs and airways'})
            CREATE (bs4:BodySystem {name: 'Nervous', description: 'Brain and nerves'})
            CREATE (bs5:BodySystem {name: 'Digestive', description: 'Stomach and intestines'})
        """)
        print("✅ Created body systems")
        
        # Patient 1: Maria Garcia - Diabetes & Hypertension
        session.run("""
            CREATE (p:Patient {
                id: 'patient-001',
                name: 'Maria Garcia',
                gender: 'female',
                birthDate: '1965-03-15'
            })
            CREATE (c1:Condition {
                code: 'E11',
                display: 'Type 2 Diabetes Mellitus',
                clinicalStatus: 'active',
                onsetDate: '2015-06-20'
            })
            CREATE (c2:Condition {
                code: 'I10',
                display: 'Essential Hypertension',
                clinicalStatus: 'active',
                onsetDate: '2018-01-10'
            })
            CREATE (m1:Medication {
                code: '860975',
                display: 'Metformin 500mg',
                status: 'active'
            })
            CREATE (m2:Medication {
                code: '197884',
                display: 'Lisinopril 10mg',
                status: 'active'
            })
            
            // Create relationships
            CREATE (p)-[:HAS_CONDITION]->(c1)
            CREATE (p)-[:HAS_CONDITION]->(c2)
            CREATE (p)-[:TAKES_MEDICATION]->(m1)
            CREATE (p)-[:TAKES_MEDICATION]->(m2)
            
            // Link to body systems
            WITH p, c1, c2, m1, m2
            MATCH (bs1:BodySystem {name: 'Endocrine'})
            MATCH (bs2:BodySystem {name: 'Cardiovascular'})
            CREATE (c1)-[:AFFECTS]->(bs1)
            CREATE (c2)-[:AFFECTS]->(bs2)
            CREATE (m1)-[:TREATS]->(c1)
            CREATE (m1)-[:TARGETS]->(bs1)
            CREATE (m2)-[:TREATS]->(c2)
            CREATE (m2)-[:TARGETS]->(bs2)
        """)
        print("✅ Created Patient 1: Maria Garcia (Diabetes, Hypertension)")
        
        # Patient 2: James Wilson - Heart Disease
        session.run("""
            CREATE (p:Patient {
                id: 'patient-002',
                name: 'James Wilson',
                gender: 'male',
                birthDate: '1958-11-22'
            })
            CREATE (c1:Condition {
                code: 'I25.10',
                display: 'Coronary Artery Disease',
                clinicalStatus: 'active',
                onsetDate: '2019-04-15'
            })
            CREATE (c2:Condition {
                code: 'E78.0',
                display: 'Hypercholesterolemia',
                clinicalStatus: 'active',
                onsetDate: '2017-08-01'
            })
            CREATE (m1:Medication {
                code: '617312',
                display: 'Atorvastatin 20mg',
                status: 'active'
            })
            CREATE (m2:Medication {
                code: '308416',
                display: 'Aspirin 81mg',
                status: 'active'
            })
            
            CREATE (p)-[:HAS_CONDITION]->(c1)
            CREATE (p)-[:HAS_CONDITION]->(c2)
            CREATE (p)-[:TAKES_MEDICATION]->(m1)
            CREATE (p)-[:TAKES_MEDICATION]->(m2)
            
            WITH p, c1, c2, m1, m2
            MATCH (bs:BodySystem {name: 'Cardiovascular'})
            CREATE (c1)-[:AFFECTS]->(bs)
            CREATE (c2)-[:AFFECTS]->(bs)
            CREATE (m1)-[:TREATS]->(c2)
            CREATE (m1)-[:TARGETS]->(bs)
            CREATE (m2)-[:TREATS]->(c1)
            CREATE (m2)-[:TARGETS]->(bs)
        """)
        print("✅ Created Patient 2: James Wilson (Heart Disease)")
        
        # Patient 3: Sarah Johnson - Asthma
        session.run("""
            CREATE (p:Patient {
                id: 'patient-003',
                name: 'Sarah Johnson',
                gender: 'female',
                birthDate: '1972-07-08'
            })
            CREATE (c1:Condition {
                code: 'J45.20',
                display: 'Mild Persistent Asthma',
                clinicalStatus: 'active',
                onsetDate: '1990-05-12'
            })
            CREATE (m1:Medication {
                code: '896188',
                display: 'Albuterol Inhaler',
                status: 'active'
            })
            CREATE (m2:Medication {
                code: '895994',
                display: 'Fluticasone Inhaler',
                status: 'active'
            })
            
            CREATE (p)-[:HAS_CONDITION]->(c1)
            CREATE (p)-[:TAKES_MEDICATION]->(m1)
            CREATE (p)-[:TAKES_MEDICATION]->(m2)
            
            WITH p, c1, m1, m2
            MATCH (bs:BodySystem {name: 'Respiratory'})
            CREATE (c1)-[:AFFECTS]->(bs)
            CREATE (m1)-[:TREATS]->(c1)
            CREATE (m1)-[:TARGETS]->(bs)
            CREATE (m2)-[:TREATS]->(c1)
            CREATE (m2)-[:TARGETS]->(bs)
        """)
        print("✅ Created Patient 3: Sarah Johnson (Asthma)")
        
        # Verify
        result = session.run("""
            MATCH (p:Patient) WITH count(p) as patients
            MATCH (c:Condition) WITH patients, count(c) as conditions
            MATCH (m:Medication) WITH patients, conditions, count(m) as medications
            MATCH (bs:BodySystem) WITH patients, conditions, medications, count(bs) as systems
            RETURN patients, conditions, medications, systems
        """)
        record = result.single()
        print(f"\n📊 Database Summary:")
        print(f"   👤 Patients: {record['patients']}")
        print(f"   🏥 Conditions: {record['conditions']}")
        print(f"   💊 Medications: {record['medications']}")
        print(f"   🫀 Body Systems: {record['systems']}")

if __name__ == "__main__":
    print("=" * 50)
    print("🏥 Quick Data Loader")
    print("=" * 50)
    try:
        driver.verify_connectivity()
        print("✅ Connected to Neo4j!")
        clear_and_load()
        print("\n🎉 Data loaded! Refresh http://localhost:5173")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()
