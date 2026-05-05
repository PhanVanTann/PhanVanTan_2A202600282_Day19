import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_triple(self, subject, predicate, obj):
        with self.driver.session() as session:
            # Cypher query to merge nodes and create relationship
            # Note: Relationship type cannot be parameterized, so we sanitize and format it.
            predicate = predicate.replace(" ", "_").upper()
            query = (
                f"MERGE (s:Entity {{name: $subject}}) "
                f"MERGE (o:Entity {{name: $obj}}) "
                f"MERGE (s)-[:{predicate}]->(o)"
            )
            session.run(query, subject=subject, obj=obj)

def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    if not password:
        print("Error: NEO4J_PASSWORD not found in environment variables.")
        return

    input_path = "extracted_triples.json"
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Please run extract_triples.py first.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        triples = json.load(f)

    print(f"Connecting to Neo4j at {uri}...")
    try:
        graph = Neo4jGraph(uri, user, password)
        
        print(f"Loading {len(triples)} triples into Neo4j...")
        for i, t in enumerate(triples):
            graph.create_triple(t['subject'], t['predicate'], t['object'])
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1} triples...")
        
        graph.close()
        print("Successfully built the knowledge graph in Neo4j!")
        
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")

if __name__ == "__main__":
    main()
