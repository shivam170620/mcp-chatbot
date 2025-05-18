from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List, Optional, Dict
import asyncio
import nest_asyncio
import os
import json

nest_asyncio.apply()

load_dotenv()

class GeminiClientWrapper:
    """Wrapper for the Gemini client to handle generation requests."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = "gemini-2.0-flash", mock_mode: bool = False):
        self.mock_mode = mock_mode
        
        if not mock_mode:
            import google.generativeai as genai
            
            if api_key is None:
                api_key = os.getenv("GEMINI_API_KEY")
            if model_name is None:
                model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY must be set in env or passed directly")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.mock_responses = {}
    
    def set_mock_response(self, step_id: str, response: Dict):
        if not self.mock_mode:
            raise ValueError("Cannot set mock responses when not in mock mode")
        self.mock_responses[step_id] = response
    
    def generate_response(self, prompt: str, step_id: Optional[str] = None) -> str:
        if self.mock_mode:
            return self.mock_responses.get(step_id, {}).get("response", "Mocked response")
        else:
            response = self.model.generate_content(prompt)
            return response.text.strip()

class MCP_ChatBot:

    def __init__(self, mock_mode: bool = False):
        # Initialize session and client objects
        self.session: ClientSession = None
        self.gemini_client = GeminiClientWrapper(mock_mode=mock_mode)
        self.available_tools: List[dict] = []

    def _create_tool_prompt(self, query: str, conversation_history: List[Dict] = None) -> str:
        """Create a prompt for Gemini that includes tool descriptions and conversation history."""
        prompt_parts = []
        
        # Add system instruction about tool usage
        prompt_parts.append("""You are an AI assistant with access to tools. You can call tools to help answer user questions.

Available tools:""")
        
        # Add tool descriptions
        for tool in self.available_tools:
            tool_desc = f"""
Tool: {tool['name']}
Description: {tool['description']}
Input Schema: {json.dumps(tool['input_schema'], indent=2)}
"""
            prompt_parts.append(tool_desc)
        
        prompt_parts.append("""
When you need to use a tool, respond with a JSON object in this format:
{
    "action": "tool_call",
    "tool_name": "tool_name",
    "tool_args": {
        "arg1": "value1",
        "arg2": "value2"
    }
}

When you don't need to use a tool, just respond normally with text.

""")
        
        # Add conversation history if provided
        if conversation_history:
            prompt_parts.append("Conversation history:")
            for message in conversation_history:
                if message['role'] == 'user':
                    prompt_parts.append(f"User: {message['content']}")
                elif message['role'] == 'assistant':
                    prompt_parts.append(f"Assistant: {message['content']}")
                elif message['role'] == 'tool_result':
                    prompt_parts.append(f"Tool result: {message['content']}")
            prompt_parts.append("")
        
        # Add current query
        prompt_parts.append(f"User: {query}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)

    def _parse_gemini_response(self, response_text: str):
        """Parse Gemini response to check if it contains a tool call."""
        response_text = response_text.strip()
        
        # Try to parse as JSON for tool calls
        try:
            parsed = json.loads(response_text)
            if isinstance(parsed, dict) and parsed.get("action") == "tool_call":
                return {
                    "type": "tool_call",
                    "tool_name": parsed.get("tool_name"),
                    "tool_args": parsed.get("tool_args", {})
                }
        except json.JSONDecodeError:
            pass
        
        # If not a tool call, treat as regular text response
        return {
            "type": "text",
            "content": response_text
        }

    async def process_query(self, query):
        conversation_history = []
        original_query = query  # Store the original query
        current_query = query  # Keep track of the current query
        
        while True:  # Use while True instead of process_query flag
            # Create prompt with current query and conversation history
            prompt = self._create_tool_prompt(current_query, conversation_history)
            
            # Get response from Gemini
            response_text = self.gemini_client.generate_response(prompt)
            parsed_response = self._parse_gemini_response(response_text)
            
            if parsed_response["type"] == "text":
                # Regular text response - this is our final answer
                print(parsed_response["content"])
                break  # Exit the loop, we have our final response
                
            elif parsed_response["type"] == "tool_call":
                # Tool call response
                tool_name = parsed_response["tool_name"]
                tool_args = parsed_response["tool_args"]
                
                print(f"Calling tool {tool_name} with args {tool_args}")
                
                # Add the tool call to conversation history
                conversation_history.append({
                    "role": "assistant",
                    "content": f"I need to use the {tool_name} tool to help answer your question."
                })
                
                try:
                    # Call the tool through MCP session
                    result = await self.session.call_tool(tool_name, arguments=tool_args)
                    tool_result = str(result.content)
                    
                    print(f"Tool result: {tool_result}")
                    
                    # Add tool result to conversation history
                    conversation_history.append({
                        "role": "tool_result",
                        "content": tool_result
                    })
                    
                    # Update the query to ask for interpretation of the tool result
                    # This ensures the next iteration will generate a response based on the tool result
                    current_query = f"Based on the tool result above, please provide a comprehensive answer to the user's original question: '{original_query}'. Use the information from the tool result to give a helpful and detailed response."
                    
                    # Continue the loop to get the final response
                    
                except Exception as e:
                    error_msg = f"Error calling tool {tool_name}: {str(e)}"
                    print(error_msg)
                    conversation_history.append({
                        "role": "tool_result",
                        "content": f"Error: {error_msg}"
                    })
                    # Set the query to handle the error and provide a response
                    current_query = f"There was an error with the tool call: {error_msg}. Please provide a helpful response to the user's original query: '{original_query}'"
                    # Continue the loop to get an error handling response

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
        
                if query.lower() == 'quit':
                    break
                    
                await self.process_query(query)
                print("\n" + "="*50 + "\n")  # Add separator between queries
                    
            except Exception as e:
                print(f"\nError: {str(e)}")

    
    async def connect_to_server_and_run(self):
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="uv",  # Executable
            args=["run", "research_server.py"],  # Optional command line arguments
            env=None,  # Optional environment variables
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                # Initialize the connection
                await session.initialize()
    
                # List available tools
                response = await session.list_tools()
                
                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])
                
                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]
    
                await self.chat_loop()


async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()
  

if __name__ == "__main__":
    asyncio.run(main())