docker run -p 8000:8000 \
-e NEO4J_URI="bolt://host.docker.internal:7687" \
-e NEO4J_USERNAME="neo4j" \
-e NEO4J_PASSWORD="password" \
mcp-neo4j-cypher