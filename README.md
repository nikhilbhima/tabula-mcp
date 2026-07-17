# Tabula MCP Server

One memory. Every AI.

[Tabula](https://www.tabula360.com) is a shared memory layer for your AIs. Tell Claude once, and ChatGPT already knows. Connected AIs save the durable facts you share (who you are, what you're building, how you like to work) and recall them in any other AI, so you never re-explain yourself.

This repo documents Tabula's hosted MCP server and how to connect it from any MCP client.

## Endpoint

|             |                                              |
| ----------- | -------------------------------------------- |
| URL         | `https://www.tabula360.com/api/mcp/mcp`      |
| Transport   | Streamable HTTP                              |
| Auth        | OAuth 2.1 (web clients) or Bearer token (CLIs and IDEs) |

Sign up at [tabula360.com](https://www.tabula360.com), then get your access token on the [Connect page](https://www.tabula360.com/connect). The token is shown once, treat it like a password.

## Tools

| Tool            | What it does                                        |
| --------------- | --------------------------------------------------- |
| `save_memory`   | Save a durable fact, preference, or decision        |
| `search_memory` | Semantic search across everything saved             |
| `list_memories` | Browse saved memories                               |
| `update_memory` | Correct or refresh an existing memory               |
| `delete_memory` | Remove a memory for good                            |

## Connect

### ChatGPT, Claude, Mistral, Grok, Perplexity, Manus

Web clients connect as a custom connector with OAuth. Follow the step-by-step [guide](https://www.tabula360.com/guide).

### Claude Code

```bash
claude mcp add --transport http tabula \
  https://www.tabula360.com/api/mcp/mcp \
  --header "Authorization: Bearer YOUR_TOKEN"
```

### Cursor

Add to `~/.cursor/mcp.json` (or `.cursor/mcp.json` in a project):

```json
{
  "mcpServers": {
    "tabula": {
      "url": "https://www.tabula360.com/api/mcp/mcp",
      "headers": {
        "Authorization": "Bearer ${env:TABULA_MCP_TOKEN}"
      }
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json`. VS Code uses `servers` and prompts for the token via `inputs`:

```json
{
  "servers": {
    "tabula": {
      "type": "http",
      "url": "https://www.tabula360.com/api/mcp/mcp",
      "headers": { "Authorization": "Bearer ${input:tabula-token}" }
    }
  },
  "inputs": [
    { "type": "promptString", "id": "tabula-token", "description": "Tabula token", "password": true }
  ]
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "tabula": {
      "serverUrl": "https://www.tabula360.com/api/mcp/mcp",
      "headers": {
        "Authorization": "Bearer ${env:TABULA_MCP_TOKEN}"
      }
    }
  }
}
```

### Codex CLI

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.tabula]
url = "https://www.tabula360.com/api/mcp/mcp"
bearer_token_env_var = "TABULA_MCP_TOKEN"
```

### Mistral Vibe CLI

Add to `~/.vibe/config.toml`, with `TABULA_MCP_TOKEN` in `~/.vibe/.env`:

```toml
[[mcp_servers]]
name = "tabula"
transport = "http"
url = "https://www.tabula360.com/api/mcp/mcp"

[mcp_servers.auth]
type = "static"
api_key_env = "TABULA_MCP_TOKEN"
```

### Your own code (OpenRouter or any OpenAI-compatible API)

Give a plain API script persistent memory with the standard tool-calling loop. A complete single-file example lives in [`examples/openrouter-memory`](examples/openrouter-memory): it fetches Tabula's tools over MCP, hands them to the model, and executes the calls.

## Privacy

Memories are isolated per account with row-level security, and never sold or shared. You can view, edit, export, or delete everything at any time. [Privacy policy](https://www.tabula360.com/privacy).

## Pricing

Free during beta, no card required.

## Links

- [Website](https://www.tabula360.com)
- [Setup guide](https://www.tabula360.com/guide)
- [Blog](https://www.tabula360.com/blog)
- [Manifesto](https://www.tabula360.com/manifesto)
