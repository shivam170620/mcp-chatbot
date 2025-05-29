# mcp-chatbot
mcp chatbot with datasources as sql database, mongodb database, arxiv, google drive, news api, google custom apis and wikipedia.


## mcp client talks to the mcp server 

MCP Client --> MCP Server ( ListToolsRequest i.e it lists all tools)
MCP Client --> MCP Server ( Call Tool Request i.e calls a particular tool )

We are building mcp server with high level implementation using FastMCP

# launching server 

## Weather server 

{
    "mcpServers": {
        "weather_server": {
            "command": "uvx",
             "args": ["--from", "git+https://github.com/shivam170620/mcp-chatbot.git", "mcp-chatbot"],
            "env": {
                "ACCUWEATHER_API_KEY": "your_api_key_here"
            }
        }
    }
}


## Research server 

{
    "mcpServers": {
        "research_server": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/shivam170620/mcp-chatbot.git", "mcp-chatbot"],
            
        }
    }
}


## Postgres mcp server (running through docker running on 5432 port with database name as "postgres" ) 

- eg -> postgresql://postgres:YourPassword123@host.docker.internal:5432/postgres

"mcpServers": {
      "postgres": {
        "command": "docker",
        "args": [
          "run", 
          "-i", 
          "--rm", 
          "mcp/postgres", 
          "postgresql://{postgres_username}:{postgres_password}@host.docker.internal:5432/{postgres_databasename}"]
      }
}



# MCP Architecture 

Connecting the mcp chatbot ( client ) to mcp servers where we have tools.
![MCP Architecture](https://www.google.com/url?sa=i&url=https%3A%2F%2Fpieces.app%2Fblog%2Fmcp&psig=AOvVaw0ChZ88665OWWfIQ_9Hvbtk&ust=1747654582804000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCJCwnez2rI0DFQAAAAAdAAAAABAE)

![screen_shot](data/Screenshot%202025-05-18%20at%205.04.26%20PM.png)


# Connecting the mcp chatbot to reference servers 



