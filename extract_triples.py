import os
import json
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Triple(BaseModel):
    subject: str = Field(description="The subject of the triple (e.g., OpenAI)")
    predicate: str = Field(description="The relationship between subject and object (e.g., FOUNDED_BY)")
    object: str = Field(description="The object of the triple (e.g., Sam Altman)")

class Triples(BaseModel):
    triples: List[Triple]

def extract_triples(text: str):
    """
    Extracts triples (Subject, Predicate, Object) from the given text using an LLM.
    """
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY or OPENAI_API_KEY not found in environment variables.")
        return []

    # Use LOCAL Ollama
    llm = ChatOpenAI(
        model="llama3", 
        openai_api_key="ollama",
        base_url="http://localhost:11434/v1",
        temperature=0
    )
    structured_llm = llm.with_structured_output(Triples)

    system_prompt = (
        "You are an expert at extracting information and forming knowledge graphs. "
        "Extract all key entities and their relationships from the provided text. "
        "Output the results as a list of triples (subject, predicate, object). "
        "The predicate should be in UPPERCASE and use underscores instead of spaces (e.g., FOUNDED_BY, LOCATED_IN)."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])

    chain = prompt | structured_llm
    
    print("Extracting triples...")
    result = chain.invoke({"input": text})
    return result.triples

def main():
    corpus_path = "tech_company_corpus.txt"
    output_path = "extracted_triples.json"

    if not os.path.exists(corpus_path):
        print(f"Error: {corpus_path} not found.")
        return

    with open(corpus_path, "r", encoding="utf-8") as f:
        text = f.read()

    extracted = extract_triples(text)
    
    if extracted:
        # Convert Pydantic models to dicts for JSON serialization
        triples_data = [t.model_dump() for t in extracted]
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(triples_data, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully extracted {len(triples_data)} triples and saved to {output_path}")
        for t in triples_data[:5]:
            print(f"  ({t['subject']}, {t['predicate']}, {t['object']})")
        if len(triples_data) > 5:
            print("  ...")

if __name__ == "__main__":
    main()
