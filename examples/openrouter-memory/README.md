# Memory for your OpenRouter scripts

One file, no framework. Your OpenRouter script gets persistent memory through [Tabula](https://www.tabula360.com): the model can save facts about the user and recall them in every future run, and in every other AI the user has connected.

## Run it

```bash
OPENROUTER_API_KEY=sk-or-... \
TABULA_MCP_TOKEN=mcp_... \
uv run --with requests openrouter_memory.py "Remember that I prefer TypeScript."
```

Then, in a fresh run (or a week later):

```bash
uv run --with requests openrouter_memory.py "What language do I prefer?"
```

Get your Tabula token at [tabula360.com/connect](https://www.tabula360.com/connect). It's free during beta.

## What the file does

1. Connects to Tabula's MCP server (Streamable HTTP, bearer token) and lists its five memory tools.
2. Converts them to OpenAI-style tool definitions and passes them to your OpenRouter chat call.
3. Runs the standard tool loop: when the model calls `save_memory` or `search_memory`, the script executes it against Tabula and feeds the result back.

Change `MODEL` with an env var (default `openai/gpt-4o-mini`). `OPENROUTER_BASE_URL` is also an env var, so the same file works against any OpenAI-compatible endpoint.

## Notes

- Memories saved here show up in the user's Tabula dashboard, and in their ChatGPT, Claude, and every other connected AI. That's the point.
- The five tools: `save_memory`, `search_memory`, `list_memories`, `update_memory`, `delete_memory`. Their schemas come from the server at runtime, so this example never goes stale.
