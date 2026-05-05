import os
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Entity(BaseModel):
    name: str = Field(description="The main entity found in the question")

class RAGComparator:
    def __init__(self):
        # LLM Setup (Using LOCAL Ollama)
        self.llm = ChatOpenAI(
            model="llama3",
            openai_api_key="ollama", # Dummy key for local
            base_url="http://localhost:11434/v1",
            temperature=0
        )
        # Use a lightweight local embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Neo4j Setup (GraphRAG)
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

        # Chroma Setup (Flat RAG)
        self.setup_flat_rag()

    def setup_flat_rag(self):
        corpus_path = "tech_company_corpus.txt"
        with open(corpus_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split into simple sentences for Flat RAG chunks
        chunks = [s.strip() for s in content.split(".") if s.strip()]
        self.vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            collection_name="flat_rag"
        )

    def close(self):
        self.driver.close()

    # --- GraphRAG Logic ---
    def get_graph_context(self, question: str) -> str:
        structured_llm = self.llm.with_structured_output(Entity)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Identify the primary tech company or person mentioned in the question."),
            ("human", "{question}")
        ])
        chain = prompt | structured_llm
        entity_name = chain.invoke({"question": question}).name

        with self.driver.session() as session:
            query = (
                "MATCH (e:Entity {name: $name})-[r1]-(n1) "
                "OPTIONAL MATCH (n1)-[r2]-(n2) "
                "RETURN startNode(r1).name as s1, type(r1) as p1, endNode(r1).name as o1, "
                "startNode(r2).name as s2, type(r2) as p2, endNode(r2).name as o2"
            )
            results = session.run(query, name=entity_name)
            triples = set()
            for record in results:
                if record['s1'] and record['p1'] and record['o1']:
                    triples.add(f"({record['s1']}) --[{record['p1']}]--> ({record['o1']})")
                if record['s2'] and record['p2'] and record['o2']:
                    triples.add(f"({record['s2']}) --[{record['p2']}]--> ({record['o2']})")
            return "\n".join(triples) if triples else "No graph context."

    # --- Flat RAG Logic ---
    def get_flat_context(self, question: str) -> str:
        results = self.vector_store.similarity_search(question, k=3)
        return "\n".join([doc.page_content for doc in results])

    def query(self, question: str):
        print(f"\n" + "="*50)
        print(f"QUESTION: {question}")
        print("="*50)

        # 1. Flat RAG Answer
        flat_context = self.get_flat_context(question)
        prompt_flat = ChatPromptTemplate.from_messages([
            ("system", "Answer based ONLY on the provided text context."),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])
        chain_flat = prompt_flat | self.llm
        ans_flat = chain_flat.invoke({"context": flat_context, "question": question})

        # 2. GraphRAG Answer
        graph_context = self.get_graph_context(question)
        prompt_graph = ChatPromptTemplate.from_messages([
            ("system", "Answer accurately based ONLY on the provided graph triples. If multiple relationships exist (e.g. co-founders), mention them."),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])
        chain_graph = prompt_graph | self.llm
        ans_graph = chain_graph.invoke({"context": graph_context, "question": question})

        print(f"\n[FLAT RAG ANSWER]\n{ans_flat.content}")
        print(f"\n[GRAPHRAG ANSWER]\n{ans_graph.content}")

def main():
    comparator = RAGComparator()
    try:
        questions = [
            "Mối liên hệ giữa Microsoft và Sam Altman là gì?",
            "Elon Musk và Sam Altman cùng làm gì tại OpenAI?",
            "Sự nghiệp của Tim Cook sau Steve Jobs như thế nào?",
            "Sundar Pichai quản lý công ty con nào của Alphabet Inc.?",
            "Jeff Bezos và Andy Jassy có liên quan gì đến Amazon?"
        ]
        for q in questions:
            comparator.query(q)
    finally:
        comparator.close()

if __name__ == "__main__":
    main()
