# Movie Database Query Web App

A modern web application that allows users to query a Neo4j movie database using natural language. The app translates natural language queries into Cypher queries and executes them against the database.

## Features

- **Natural Language Processing**: Uses OpenAI GPT to translate natural language queries into Cypher
- **Real-time Query Execution**: Executes queries against Neo4j database via MCP tools
- **Modern UI**: Beautiful React frontend with syntax highlighting
- **Schema Information**: Displays database schema and example queries
- **Error Handling**: Comprehensive error handling and user feedback

## Architecture

- **Backend**: FastAPI (Python) with OpenAI integration
- **Frontend**: React with modern styling
- **Database**: Neo4j with MCP client integration
- **AI**: OpenAI GPT-3.5-turbo for query translation

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Neo4j database running
- OpenAI API key

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```
   The server will run on `http://localhost:8000`

### Frontend Setup

1. **Install Node.js dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the React development server**:
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter a natural language query in the search box
3. Click "Search" to execute the query
4. View the generated Cypher query and results
5. Try the example queries for inspiration

### Example Queries

- "Find all movies with Russell Crowe"
- "Show me action movies from 2020"
- "Who directed Gladiator?"
- "List movies with Tom Hanks"
- "Find movies with both Russell Crowe and Tom Hanks"

## Database Schema

The application works with a movie database containing:

- **Movie Nodes** (681,857): title, year, runtimeMinutes, genres, titleId
- **Person Nodes** (434,118): name, birthYear, deathYear, nameId
- **Relationships**: ACTOR (Person→Movie), DIRECTOR (Person→Movie)

## API Endpoints

- `POST /api/query`: Process natural language queries
- `GET /api/schema`: Get database schema information
- `GET /`: Health check endpoint

## MCP Integration

The application is designed to work with MCP (Model Context Protocol) tools for Neo4j:

- `mcp_neo4j-local_read_neo4j_cypher`: Execute read queries
- `mcp_neo4j-local_write_neo4j_cypher`: Execute write queries
- `mcp_neo4j-local_get_neo4j_schema`: Get database schema

## Development

### Project Structure

```
movie-db/
├── backend/
│   ├── main.py          # FastAPI application
│   └── mcp_client.py    # MCP client integration
├── frontend/
│   ├── src/
│   │   ├── App.js       # Main React component
│   │   ├── App.css      # Component styles
│   │   └── index.js     # React entry point
│   └── package.json     # Node.js dependencies
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Customization

- **Query Translation**: Modify the system prompt in `backend/main.py` to improve query translation
- **UI Styling**: Update CSS files in `frontend/src/` to customize the appearance
- **Database Schema**: Update the schema information in the backend to match your database

## Troubleshooting

1. **Backend not starting**: Check that all Python dependencies are installed and the `.env` file is configured
2. **Frontend not loading**: Ensure Node.js dependencies are installed with `npm install`
3. **Query errors**: Check that your Neo4j database is running and accessible
4. **Translation errors**: Verify your OpenAI API key is valid and has sufficient credits

## License

This project is open source and available under the MIT License. 