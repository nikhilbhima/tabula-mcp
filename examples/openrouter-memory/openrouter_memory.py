# Persistent memory for any OpenRouter script, via Tabula (tabula360.com).
#
# Your model can save facts about the user and recall them in every future
# run, and in every other AI the user has connected to Tabula.
#
# Run:
#   OPENROUTER_API_KEY=sk-or-... TABULA_MCP_TOKEN=mcp_... \
#     uv run --with requests openrouter_memory.py "what do you know about me?"
#
# Works with any OpenAI-compatible endpoint: override OPENROUTER_BASE_URL
# and MODEL to point somewhere else.

import json
import os
import sys

import requests

TABULA_URL = "https://www.tabula360.com/api/mcp/mcp"
BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = (
    "You have persistent memory through Tabula tools. Before answering "
    "anything about the user, call search_memory. When the user shares a "
    "durable fact, preference, or decision, call save_memory. Write each "
    "memory so it stands alone, with names instead of 'this' or 'here'."
)


class Tabula:
    """Minimal MCP client (Streamable HTTP) for the Tabula memory server."""

    def __init__(self, token):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self.next_id = 0
        init = self.request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "openrouter-memory-example", "version": "1.0.0"},
        })
        self.headers["MCP-Protocol-Version"] = init["protocolVersion"]
        self.notify("notifications/initialized")

    def post(self, payload):
        r = requests.post(TABULA_URL, headers=self.headers, json=payload, timeout=60)
        if r.status_code == 401:
            sys.exit("Tabula rejected the token. Check TABULA_MCP_TOKEN "
                     "(generate one at tabula360.com/connect).")
        r.raise_for_status()
        if r.headers.get("mcp-session-id"):
            self.headers["Mcp-Session-Id"] = r.headers["mcp-session-id"]
        return r

    def request(self, method, params=None):
        self.next_id += 1
        payload = {"jsonrpc": "2.0", "id": self.next_id, "method": method}
        if params is not None:
            payload["params"] = params
        r = self.post(payload)
        body = r.text
        if "text/event-stream" in r.headers.get("content-type", ""):
            messages = [json.loads(line[5:].strip())
                        for line in body.splitlines() if line.startswith("data:")]
            reply = next(m for m in messages if m.get("id") == self.next_id)
        else:
            reply = json.loads(body)
        if "error" in reply:
            raise RuntimeError(f"Tabula error on {method}: {reply['error']}")
        return reply["result"]

    def notify(self, method):
        self.post({"jsonrpc": "2.0", "method": method})

    def openai_tools(self):
        tools = self.request("tools/list")["tools"]
        return [{"type": "function", "function": {
            "name": t["name"],
            "description": t.get("description", ""),
            "parameters": t.get("inputSchema", {"type": "object"}),
        }} for t in tools]

    def call(self, name, arguments):
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        parts = [c.get("text", "") for c in result.get("content", [])]
        return "\n".join(p for p in parts if p) or "(no result)"


def chat(prompt):
    tabula = Tabula(os.environ["TABULA_MCP_TOKEN"])
    tools = tabula.openai_tools()
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}]

    while True:
        r = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
            json={"model": MODEL, "messages": messages, "tools": tools},
            timeout=120,
        )
        r.raise_for_status()
        message = r.json()["choices"][0]["message"]
        messages.append(message)

        if not message.get("tool_calls"):
            return message["content"]

        for tc in message["tool_calls"]:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"] or "{}")
            print(f"  [{name}] {json.dumps(args)[:100]}", file=sys.stderr)
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": tabula.call(name, args),
            })


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What do you know about me?"
    print(chat(question))
