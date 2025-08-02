from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import openai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Movie Database Query API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    cypher_query: str
    results: List[Dict[str, Any]]
    explanation: str
    error: Optional[str] = None

# Database schema information for the AI
SCHEMA_INFO = """
Neo4j Database Schema:
- Nodes: Movie (681,857), Person (434,118)
- Movie properties: title, year, runtimeMinutes, genres, titleId
- Person properties: name, birthYear, deathYear, nameId
- Relationships: ACTOR (Person->Movie), DIRECTOR (Person->Movie)
- Both relationships are bidirectional and have no properties
"""

def translate_to_cypher(natural_query: str) -> str:
    """Translate natural language query to Cypher using OpenAI"""
    
    system_prompt = f"""
You are a Cypher query translator for a movie database. 
{SCHEMA_INFO}

Convert the user's natural language query into a valid Cypher query.
- Use MATCH patterns to find nodes and relationships
- Use RETURN to specify what to return
- Use WHERE for filtering conditions
- Use ORDER BY for sorting
- Use LIMIT to limit results
- Always use proper Cypher syntax

Examples:
- "Find all movies with Russell Crowe" -> MATCH (p:Person {name: 'Russell Crowe'})-[:actor]->(m:Movie) RETURN m.title, m.year ORDER BY m.year
- "Show me action movies from 2020" -> MATCH (m:Movie) WHERE m.year = 2020 AND m.genres CONTAINS 'Action' RETURN m.title, m.genres
- "Who directed Gladiator?" -> MATCH (p:Person)-[:director]->(m:Movie {title: 'Gladiator'}) RETURN p.name

Return ONLY the Cypher query, nothing else.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_query}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        cypher_query = response.choices[0].message.content.strip()
        
        # Clean up the response - remove any markdown formatting
        if cypher_query.startswith("```cypher"):
            cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()
        elif cypher_query.startswith("```"):
            cypher_query = cypher_query.replace("```", "").strip()
            
        return cypher_query
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

from mcp_client import execute_cypher_with_mcp

def execute_cypher_query(cypher_query: str) -> List[Dict[str, Any]]:
    """Execute Cypher query using the MCP Neo4j tool"""
    # Use the MCP client to execute the query
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(execute_cypher_with_mcp(cypher_query))
        loop.close()
        return results
    except Exception as e:
        return [{"error": str(e), "cypher": cypher_query}]

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query and return results"""
    try:
        # Translate natural language to Cypher
        cypher_query = translate_to_cypher(request.query)
        
        # Execute the query (in real implementation, use MCP client)
        results = execute_cypher_query(cypher_query)
        
        explanation = f"Translated '{request.query}' to Cypher query: {cypher_query}"
        
        return QueryResponse(
            cypher_query=cypher_query,
            results=results,
            explanation=explanation
        )
        
    except Exception as e:
        return QueryResponse(
            cypher_query="",
            results=[],
            explanation="",
            error=str(e)
        )

@app.get("/api/schema")
async def get_schema():
    """Get database schema information"""
    return {
        "nodes": {
            "Movie": {
                "count": 681857,
                "properties": ["title", "year", "runtimeMinutes", "genres", "titleId"]
            },
            "Person": {
                "count": 434118,
                "properties": ["name", "birthYear", "deathYear", "nameId"]
            }
        },
        "relationships": {
            "ACTOR": "Person -> Movie (bidirectional)",
            "DIRECTOR": "Person -> Movie (bidirectional)"
        }
    }

@app.get("/")
async def root():
    return {"message": "Movie Database Query API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 