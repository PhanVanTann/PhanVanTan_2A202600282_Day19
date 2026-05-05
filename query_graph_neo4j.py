import os
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Entity(BaseModel):
    name: str = Field(description="The main entity found in the question (e.g., Google, OpenAI, Elon Musk)")

class GraphRAG:
    def __init__(self):
        # Neo4j Setup
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

        self.llm = ChatOpenAI(
            model="llama3",
            openai_api_key="ollama",
            base_url="http://localhost:11434/v1",
            temperature=0
        )

    def close(self):
        self.driver.close()

    def extract_entity(self, question: str) -> str:
        """Extracts the main entity from the user's question."""
        structured_llm = self.llm.with_structured_output(Entity)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Identify the primary tech company or person mentioned in the following question. Just return the name."),
            ("human", "{question}")
        ])
        chain = prompt | structured_llm
        result = chain.invoke({"question": question})
        return result.name

    def get_graph_context(self, entity_name: str) -> str:
        """Retrieves 2-hop relationships for the given entity from Neo4j."""
        with self.driver.session() as session:
            # Query for 1-hop and 2-hop relationships with correct directions
            query = (
                "MATCH (e:Entity {name: $name})-[r1]-(n1) "
                "OPTIONAL MATCH (n1)-[r2]-(n2) "
                "RETURN startNode(r1).name as s1, type(r1) as p1, endNode(r1).name as o1, "
                "startNode(r2).name as s2, type(r2) as p2, endNode(r2).name as o2"
            )
            results = session.run(query, name=entity_name)
            
            triples = set()
            for record in results:
                # Add 1-hop
                if record['s1'] and record['p1'] and record['o1']:
                    triples.add(f"({record['s1']}) --[{record['p1']}]--> ({record['o1']})")
                # Add 2-hop if exists
                if record['s2'] and record['p2'] and record['o2']:
                    triples.add(f"({record['s2']}) --[{record['p2']}]--> ({record['o2']})")
            
            if not triples:
                return "No information found in the graph."
            
            return "\n".join(triples)

    def answer_question(self, question: str):
        """Main GraphRAG flow."""
        print(f"\nQuestion: {question}")
        
        # 1. Extract Entity
        entity = self.extract_entity(question)
        print(f"Extracted Entity: {entity}")
        
        # 2. Get Context from Graph
        context = self.get_graph_context(entity)
        print(f"Graph Context found:\n{context[:500]}..." if len(context) > 500 else f"Graph Context found:\n{context}")
        
        # 3. Final Answer
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer the user's question accurately using ONLY the provided graph context. "
                       "If multiple people have the same relationship to an entity (e.g., multiple founders), make sure to mention them or use terms like 'co-founded' to be precise. "
                       "If the context doesn't contain the answer, say you don't know."),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({"context": context, "question": question})
        
        print(f"\nAnswer: {response.content}")
        return response.content

def main():
    rag = GraphRAG()
    try:
        # Sample questions
        rag.answer_question("Sam Altman là ai và ông ấy liên quan gì đến OpenAI?")
        rag.answer_question("Elon Musk thành lập những công ty nào?")
        rag.answer_question("Google thuộc về công ty nào và ai là CEO hiện tại?")
    finally:
        rag.close()

if __name__ == "__main__":
    main()
