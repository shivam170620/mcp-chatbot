# mcp-chatbot
mcp chatbot with datasources as sql database, mongodb database, arxiv, google drive, news api, google custom apis and wikipedia.


## mcp client talks to the mcp server 

MCP Client --> MCP Server ( ListToolsRequest i.e it lists all tools)
MCP Client --> MCP Server ( Call Tool Request i.e calls a particular tool )

We are building mcp server with high level implementation using FastMCP

# launching server 

You're launching research_server.py using uv run (possibly via VS Code or terminal), and your environment sets up transports (communication channels) like stdio and web socket for real-time communication/debugging. The session ID is used to track this execution session.

--> New connection
Query parameters: [Object: null prototype] {
  command: 'uv',
  args: 'run research_server.py',
  env: '{"HOME":"/Users/shivamkumar","LOGNAME":"shivamkumar","PATH":"/Users/shivamkumar/.npm/_npx/5a9d879542beca3a/node_modules/.bin:/Users/shivamkumar/Documents/GEN AI/mcp-chatbot/node_modules/.bin:/Users/shivamkumar/Documents/GEN AI/node_modules/.bin:/Users/shivamkumar/Documents/node_modules/.bin:/Users/shivamkumar/node_modules/.bin:/Users/node_modules/.bin:/node_modules/.bin:/opt/homebrew/lib/node_modules/npm/node_modules/@npmcli/run-script/lib/node-gyp-bin:/Users/shivamkumar/Documents/GEN AI/mcp-chatbot/.venv/bin:/Users/shivamkumar/.vscode/extensions/ms-python.python-2025.6.1-darwin-arm64/python_files/deactivate/zsh:/Users/shivamkumar/.pyenv/versions/3.11.4/bin:/Users/shivamkumar/.vscode/extensions/ms-python.python-2025.6.1-darwin-arm64/python_files/deactivate/zsh:/Users/shivamkumar/.pyenv/versions/3.11.4/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/Users/shivamkumar/.vscode/extensions/ms-python.python-2025.6.1-darwin-arm64/python_files/deactivate/zsh:/Users/shivamkumar/.pyenv/versions/3.11.4/bin:/opt/anaconda3/bin:/opt/anaconda3/condabin:/opt/homebrew/bin:/opt/homebrew/sbin","SHELL":"/bin/zsh","TERM":"xterm-256color","USER":"shivamkumar"}',
  transportType: 'stdio'
}
Stdio transport: command=/Users/shivamkumar/.pyenv/versions/3.11.4/bin/uv, args=run,research_server.py
Spawned stdio transport
Connected MCP client to backing server transport
Created web app transport
Set up MCP proxy
Received message for sessionId b60cf4a7-48ff-4541-af5b-5e87714bfa8f
Received message for sessionId b60cf4a7-48ff-4541-af5b-5e87714bfa8f

# MCP Architecture 

Connecting the mcp chatbot ( client ) to mcp servers where we have tools.
![MCP Architecture](https://www.google.com/url?sa=i&url=https%3A%2F%2Fpieces.app%2Fblog%2Fmcp&psig=AOvVaw0ChZ88665OWWfIQ_9Hvbtk&ust=1747654582804000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCJCwnez2rI0DFQAAAAAdAAAAABAE)

![screen_shot](data/Screenshot%202025-05-18%20at%205.04.26%20PM.png)


# Connecting the mcp chatbot to reference servers 

# Admding prompt and resource features 