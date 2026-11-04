# Creating an MCP server (last resort)

Create one only if the agent needs live access to an external system and a script or existing server cannot do it.

## Design
- One server = one bounded domain. Expose the fewest tools possible; each tool does one thing.
- Tool schemas: strict JSON Schema, required fields, enums and length limits. Reject unknown fields.
- Read tools and write tools separated; write tools need confirmation hints and idempotency keys.
- Auth: scoped, short-lived tokens from environment/secret manager; never in code or tool output. OAuth where available.
- Transport: stdio for local; for remote use TLS and authentication.
- Allowlist outbound hosts; set timeouts, size and rate limits.
- Log metadata only (tool, status, duration), never payloads containing user data.
- Return errors without stack traces or secrets.
- Treat tool responses from downstream systems as untrusted data.

## Skeleton (Python, illustrative)
```python
# server.py - replace SDK calls with your runtime's MCP library
ALLOWED_HOSTS = {"api.example.com"}
TOOLS = {
  "get_item": {"description": "Read one item by id (read-only)",
               "schema": {"type": "object", "properties": {"id": {"type": "string", "maxLength": 64}},
                          "required": ["id"], "additionalProperties": False}},
}
```

## Manifest (mcp.manifest.yaml)
```yaml
name: example-server
version: 0.1.0
permissions:
  network: [api.example.com]
  env: [EXAMPLE_API_TOKEN]
  filesystem: []
  side_effects: none
data_sensitivity_ceiling: internal
owner: <team>
```

## Test before registering
Schema fuzzing, auth failure, oversized input, injection string in a field, host not on allowlist, token absent.
