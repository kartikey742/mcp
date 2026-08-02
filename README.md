# FastMCP Image Generator Server (Streamable HTTP / SSE Endpoint)

A minimal Model Context Protocol (MCP) server built with FastMCP. It provides a single tool (`generate_image`) over a Streamable HTTP / SSE endpoint (`/sse`) accepting both GET (events) and POST (tool calls) from Claude Web.

## Dependencies

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python server.py
```

This starts the server on `http://0.0.0.0:8000/sse`.

## Connecting to Claude Web (`claude.ai`)

1. Run `python server.py`.
2. Port-forward or tunnel port 8000 (e.g. using ngrok: `ngrok http 8000`).
3. Enter `https://<your-public-url>/sse` as your custom connector endpoint in Claude Web.
