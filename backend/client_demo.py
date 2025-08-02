import os
import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
# from mcp.client.sse import SseServerParameters

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

print(os.getenv("NEO4J_URI"))

class MCPClient:
	def __init__(self):
		self.session: Optional[ClientSession] = None
		self.exit_stack = AsyncExitStack()
		self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
		self.schema = None

	async def connect_to_neo4j_mcp_server(self):
		server_params = StdioServerParameters(
			command="uvx",
			args=["mcp-neo4j-cypher@0.3.0", "--transport", "stdio"],
			env={
				"NEO4J_URI": os.getenv("NEO4J_URI"), 
				"NEO4J_USER": os.getenv("NEO4J_USER"), 
				"NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"), 
				"NEO4J_DATABASE": os.getenv("NEO4J_DATABASE") 
			}
		)

		# Create the stdio transport
		stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
		self.stdio, self.write = stdio_transport
		
		# Create the session using the transport
		self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

		await self.session.initialize()

		# List available tools
		response = await self.session.list_tools()
		tools = response.tools
		print("\nConnected to server with tools:", [tool.name for tool in tools])

		return self.session
	
	async def get_schema(self, messages: list):
		print("Getting database schema...")
		## TODO: use LLM to choose get-schema tool
		schema = await self.session.call_tool("get_neo4j_schema", {})
		self.schema = schema.content
		
		schema_messages = [
			{
				"role": "system",
				"content": """Summarize this graph database schema in a way that is easy to understand. 
				Return a list of nodes and their properties, and a list of relationships and their properties."""
			},
			{
				"role": "user",
				"content": self.schema
			}
		]

		response = self.llm.chat.completions.create(
			model="gpt-4o-mini",
			messages=schema_messages,
			max_tokens=1000,
		)

		messages.insert(1, {
			"role": "system",
			"content": f"Database schema (use this for all queries): {response.choices[0].message}"
		})
		self.schema = response.choices[0].message.content
		return messages
	
	async def process_query(self, query: str):
		messages = [
			{
				"role": "system",
				"content": """You are a helpful assistant that can answer questions about movies, actors, 
				and directors using the Movie database. 

				IMPORTANT: When asked a question, follow these steps:
				1. Use the database schema provided below
				2. Format an appropriate query based on the schema
				3. Use an appropriate tool to query the database
				4. Finally, provide a helpful answer based on the query results
				"""
			},
			{
				"role": "user",
				"content": query
			}
		]
		response = await self.session.list_tools()

		available_tools = [{
			"type": "function",
			"function": {
				"name": tool.name,
				"description": tool.description,
				"parameters": tool.inputSchema,
			}
		} for tool in response.tools]

		if not self.schema:
			messages = await self.get_schema(messages)

		response = self.llm.chat.completions.create(
			model="gpt-4o-mini",
			messages=messages,
			tools=available_tools,
			max_tokens=1000,
		)
		final_text = []
		message = response.choices[0].message

		# add assistant message to conversation
		messages.append({
			"role": "assistant",
			"content": message.content,
			"tool_calls": message.tool_calls
		})

		if message.content:
			final_text.append(message.content)
		
		if message.tool_calls:
			for tool_call in message.tool_calls:
				if tool_call.function.name == "get_neo4j_schema":
					pass
				else:
					if not self.schema:
						messages = await self.get_schema(messages)

				# get tool name and arguments
				tool_name = tool_call.function.name
				tool_args = json.loads(tool_call.function.arguments)

				print(f"Calling tool: {tool_name} with args: {tool_args}")
				tool_response = await self.session.call_tool(tool_name, tool_args)
				final_text.append(f"[Calling tool {tool_name} with args: {tool_args}]")
				final_text.append(f"Tool response: {tool_response.content}")
				
				# add tool result to messages
				messages.append({
					"role": "tool",
					"content": str(tool_response.content),
					"tool_call_id": tool_call.id
				})

		# get next respond from OpenAI after tool execution
		response = self.llm.chat.completions.create(
			model="gpt-4o-mini",
			messages=messages,
			tools=available_tools,
			max_tokens=3000,
		)
		# add final response 
		final_response = response.choices[0].message.content
		if final_response:
			final_text.append(final_response)
		
		return "\n".join(final_text)

	async def chat_loop(self):
		"""Run an interactive chat loop"""
		print("Welcome to the Movie Database Chatbot! Enter your query. Type 'exit' to quit.")

		while True:
			try:
				query = input("Query: ")
				if query.lower() in ["exit", "quit"]:
					print("Exiting...")
					break
				response = await self.process_query(query)
				print("\n" + response)
			except Exception as e:
				print(f"\nError: {e}")
				print("Please try again.")


	async def cleanup(self):
		await self.exit_stack.aclose()


async def main():
	client = MCPClient()
	try:
		await client.connect_to_neo4j_mcp_server()
		await client.chat_loop()
	finally:
		await client.cleanup()

if __name__ == "__main__":
	asyncio.run(main())