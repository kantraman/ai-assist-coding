#!/usr/bin/env python3
"""Generate a Postman Collection (v2.1) and Environment from an OpenAPI 3.x spec.

Usage:
    python build_postman_collection.py openapi.json --out-dir docs/postman
    python build_postman_collection.py openapi.yaml --name "Shop API" --base-url https://staging.example.com

Input:  OpenAPI 3.x as JSON, or YAML if PyYAML is installed.
Output: <slug>.postman_collection.json and <slug>.postman_environment.json

Features:
  - Folders from tags, request names from summaries
  - Path/query/header parameters, with examples or schema-derived sample values
  - JSON, form-urlencoded and multipart bodies from examples or schemas
  - Auth from securitySchemes (bearer, basic, apiKey), per-request override or noauth
  - Saved response examples from the spec
  - Automatic tests: status code, response time, JSON content type, required fields
  - Warnings for documentation gaps (no summary, no success response, no examples)
Standard library only.
"""
import argparse
import json
import re
import sys
import uuid
from pathlib import Path

HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head", "options")
COLLECTION_SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"


# ----------------------------------------------------------------- loading
def load_spec(path):
    text = Path(path).read_text(encoding="utf-8")
    if str(path).lower().endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError:
            sys.exit("YAML input needs PyYAML (pip install pyyaml --break-system-packages), "
                     "or convert the spec to JSON.")
        return yaml.safe_load(text)
    return json.loads(text)


def resolve(spec, node, seen=()):
    """Resolve local $refs recursively, guarding against cycles."""
    if isinstance(node, dict):
        if "$ref" in node:
            ref = node["$ref"]
            if ref in seen or not ref.startswith("#/"):
                return {}
            target = spec
            for part in ref[2:].split("/"):
                part = part.replace("~1", "/").replace("~0", "~")
                target = target.get(part, {}) if isinstance(target, dict) else {}
            return resolve(spec, target, seen + (ref,))
        return {k: resolve(spec, v, seen) for k, v in node.items()}
    if isinstance(node, list):
        return [resolve(spec, v, seen) for v in node]
    return node


# ----------------------------------------------------------------- samples
def sample(schema, depth=0):
    """Build a sample value from a (resolved) JSON schema."""
    if not isinstance(schema, dict) or depth > 6:
        return None
    for key in ("example", "default"):
        if key in schema:
            return schema[key]
    if "enum" in schema and schema["enum"]:
        return schema["enum"][0]
    if "allOf" in schema:
        merged = {}
        for part in schema["allOf"]:
            val = sample(part, depth + 1)
            if isinstance(val, dict):
                merged.update(val)
        return merged
    for key in ("oneOf", "anyOf"):
        if schema.get(key):
            return sample(schema[key][0], depth + 1)
    t = schema.get("type")
    if t is None and "properties" in schema:
        t = "object"
    if t == "object":
        props = schema.get("properties", {})
        return {name: sample(sub, depth + 1) for name, sub in props.items()
                if not sub.get("readOnly")}
    if t == "array":
        return [sample(schema.get("items", {}), depth + 1)]
    if t == "string":
        fmt = schema.get("format", "")
        return {
            "date-time": "2025-01-01T00:00:00Z", "date": "2025-01-01",
            "email": "user@example.com", "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "uri": "https://example.com", "password": "<PASSWORD>",
        }.get(fmt, "string")
    if t == "integer":
        return schema.get("minimum", 1)
    if t == "number":
        return schema.get("minimum", 1.5)
    if t == "boolean":
        return True
    return None


def media_example(media):
    """Pick an example for a media-type object: explicit example(s) first, then schema."""
    if "example" in media:
        return media["example"], True
    examples = media.get("examples")
    if isinstance(examples, dict) and examples:
        first = next(iter(examples.values()))
        if isinstance(first, dict) and "value" in first:
            return first["value"], True
    return sample(media.get("schema", {})), False


def to_text(value):
    return value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)


# ----------------------------------------------------------------- auth
def auth_block(scheme):
    stype = scheme.get("type")
    if stype == "http" and scheme.get("scheme", "").lower() == "bearer":
        return {"type": "bearer", "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}]}
    if stype == "http" and scheme.get("scheme", "").lower() == "basic":
        return {"type": "basic", "basic": [
            {"key": "username", "value": "{{username}}", "type": "string"},
            {"key": "password", "value": "{{password}}", "type": "string"}]}
    if stype == "apiKey":
        return {"type": "apikey", "apikey": [
            {"key": "key", "value": scheme.get("name", "X-API-Key"), "type": "string"},
            {"key": "value", "value": "{{apiKey}}", "type": "string"},
            {"key": "in", "value": scheme.get("in", "header"), "type": "string"}]}
    if stype in ("oauth2", "openIdConnect"):
        return {"type": "bearer", "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}]}
    return None


def auth_vars(scheme):
    stype = scheme.get("type")
    if stype == "http" and scheme.get("scheme", "").lower() == "basic":
        return ["username", "password"]
    if stype == "apiKey":
        return ["apiKey"]
    if stype in ("http", "oauth2", "openIdConnect"):
        return ["token"]
    return []


# ----------------------------------------------------------------- tests
def build_tests(op, responses, max_ms):
    ok_codes = sorted(int(c) for c in responses if str(c).isdigit() and 200 <= int(c) < 300)
    lines = []
    if ok_codes:
        lines.append(f"pm.test('Status is {'/'.join(map(str, ok_codes))}', function () {{")
        lines.append(f"    pm.expect(pm.response.code).to.be.oneOf({json.dumps(ok_codes)});")
        lines.append("});")
    else:
        lines.append("pm.test('Status is not a server error', function () {")
        lines.append("    pm.expect(pm.response.code).to.be.below(500);")
        lines.append("});")
    lines.append(f"pm.test('Response time under {max_ms} ms', function () {{")
    lines.append(f"    pm.expect(pm.response.responseTime).to.be.below({max_ms});")
    lines.append("});")

    json_ok = None
    for code in ok_codes:
        content = responses.get(str(code), {}).get("content", {})
        for ctype, media in content.items():
            if "json" in ctype:
                json_ok = media
                break
        if json_ok:
            break
    if json_ok:
        lines.append("pm.test('Response is JSON', function () {")
        lines.append("    pm.response.to.be.json;")
        lines.append("});")
        schema = json_ok.get("schema", {})
        required = schema.get("required") if schema.get("type") == "object" else None
        if required:
            lines.append("pm.test('Has required fields', function () {")
            lines.append("    const body = pm.response.json();")
            for field in required:
                lines.append(f"    pm.expect(body).to.have.property({json.dumps(field)});")
            lines.append("});")
        # Token capture: lets one login request authenticate the rest of the collection.
        value, _ = media_example(json_ok)
        keys = value if isinstance(value, dict) else {}
        schema_keys = schema.get("properties", {}) if isinstance(schema, dict) else {}
        for tok in ("token", "accessToken", "access_token", "jwt"):
            if tok in keys or tok in schema_keys:
                lines.append(f"if (pm.response.code < 300) {{ const t = pm.response.json().{tok}; "
                             f"if (t) pm.collectionVariables.set('token', t); }}")
                break
    return lines


# ----------------------------------------------------------------- build
def server_url(spec, override):
    if override:
        return override.rstrip("/")
    servers = spec.get("servers") or [{"url": "http://localhost:3000"}]
    url = servers[0].get("url", "http://localhost:3000")
    for name, var in (servers[0].get("variables") or {}).items():
        url = url.replace("{" + name + "}", str(var.get("default", "")))
    return url.rstrip("/")


def build_request(spec, path, method, op, path_params, global_security, schemes,
                  max_ms, warnings):
    label = f"{method.upper()} {path}"
    if not op.get("summary") and not op.get("operationId"):
        warnings.append(f"{label}: no summary/operationId (request is named by method+path)")
    name = op.get("summary") or op.get("operationId") or label

    # operation-level params override path-level ones with same name+in
    merged = {}
    for p in path_params + op.get("parameters", []):
        merged[(p.get("name"), p.get("in"))] = p
    params = list(merged.values())

    def pval(p):
        if "example" in p:
            return to_text(p["example"])
        val = sample(p.get("schema", {}))
        return "" if val is None else to_text(val)

    segments, variables = [], []
    for seg in [s for s in path.split("/") if s]:
        m = re.fullmatch(r"\{(.+)\}", seg)
        if m:
            seg_name = m.group(1)
            segments.append(":" + seg_name)
            p = next((q for q in params if q.get("in") == "path" and q.get("name") == seg_name), {})
            variables.append({"key": seg_name, "value": pval(p) or "1",
                              "description": p.get("description", "")})
        else:
            segments.append(seg)

    query = [{"key": p["name"], "value": pval(p), "disabled": not p.get("required", False),
              "description": p.get("description", "")}
             for p in params if p.get("in") == "query"]
    headers = [{"key": p["name"], "value": pval(p), "disabled": not p.get("required", False),
                "description": p.get("description", "")}
               for p in params if p.get("in") == "header"]

    raw = "{{baseUrl}}/" + "/".join(segments)
    enabled_q = [q for q in query if not q["disabled"]]
    if enabled_q:
        raw += "?" + "&".join(f"{q['key']}={q['value']}" for q in enabled_q)
    url = {"raw": raw, "host": ["{{baseUrl}}"], "path": segments}
    if query:
        url["query"] = query
    if variables:
        url["variable"] = variables

    request = {"method": method.upper(), "header": headers, "url": url}
    desc = op.get("description") or op.get("summary") or ""
    if op.get("deprecated"):
        desc = "**Deprecated.** " + desc
    if desc:
        request["description"] = desc

    body_spec = op.get("requestBody", {}).get("content", {})
    if body_spec:
        ctype = next((c for c in body_spec if "json" in c), next(iter(body_spec)))
        media = body_spec[ctype]
        value, explicit = media_example(media)
        if not explicit:
            warnings.append(f"{label}: request body has no explicit example (generated from schema)")
        if "json" in ctype:
            headers.append({"key": "Content-Type", "value": ctype})
            request["body"] = {"mode": "raw", "raw": to_text(value),
                               "options": {"raw": {"language": "json"}}}
        elif "x-www-form-urlencoded" in ctype:
            request["body"] = {"mode": "urlencoded", "urlencoded": [
                {"key": k, "value": to_text(v)} for k, v in (value or {}).items()]}
        elif "multipart" in ctype:
            props = media.get("schema", {}).get("properties", {})
            fields = []
            for k, v in (value or {}).items():
                is_file = props.get(k, {}).get("format") == "binary"
                fields.append({"key": k, "type": "file" if is_file else "text",
                               **({"src": []} if is_file else {"value": to_text(v)})})
            request["body"] = {"mode": "formdata", "formdata": fields}
        else:
            request["body"] = {"mode": "raw", "raw": to_text(value)}

    # auth override
    security = op.get("security", global_security)
    if security == []:
        request["auth"] = {"type": "noauth"}
    elif "security" in op and security:
        scheme = schemes.get(next(iter(security[0]), ""), {})
        block = auth_block(scheme)
        if block:
            request["auth"] = block

    responses = op.get("responses", {})
    if not any(str(c).startswith("2") for c in responses):
        warnings.append(f"{label}: no 2xx response documented")

    item = {"name": name, "request": request, "response": [],
            "event": [{"listen": "test", "script": {"type": "text/javascript",
                                                    "exec": build_tests(op, responses, max_ms)}}]}

    for code, resp in responses.items():
        if not str(code).isdigit():
            continue
        saved = {"name": f"{code} {resp.get('description', '')}".strip(), "originalRequest": request,
                 "status": resp.get("description", ""), "code": int(code), "header": [], "body": ""}
        for ctype, media in resp.get("content", {}).items():
            value, _ = media_example(media)
            saved["header"] = [{"key": "Content-Type", "value": ctype}]
            saved["body"] = "" if value is None else to_text(value)
            break
        item["response"].append(saved)
    if not any(int(c) >= 400 for c in responses if str(c).isdigit()):
        warnings.append(f"{label}: no error responses documented")
    return item


def build(spec, args):
    spec = resolve(spec, spec)
    info = spec.get("info", {})
    title = args.name or info.get("title", "API")
    schemes = spec.get("components", {}).get("securitySchemes", {})
    global_security = spec.get("security", [])
    warnings = []

    folders, order = {}, []
    for path, item in (spec.get("paths") or {}).items():
        path_params = item.get("parameters", [])
        for method in HTTP_METHODS:
            op = item.get(method)
            if not op:
                continue
            tag = (op.get("tags") or ["General"])[0]
            if tag not in folders:
                folders[tag] = []
                order.append(tag)
            folders[tag].append(build_request(spec, path, method, op, path_params,
                                              global_security, schemes, args.max_ms, warnings))

    tag_desc = {t.get("name"): t.get("description", "") for t in spec.get("tags", [])}
    items = [{"name": t, "description": tag_desc.get(t, ""), "item": folders[t]} for t in order]

    base_url = server_url(spec, args.base_url)
    variables = [{"key": "baseUrl", "value": base_url, "type": "string"}]
    env_values = [{"key": "baseUrl", "value": base_url, "type": "default", "enabled": True}]
    collection_auth = None
    if global_security:
        scheme = schemes.get(next(iter(global_security[0]), ""), {})
        collection_auth = auth_block(scheme)
        for v in auth_vars(scheme):
            variables.append({"key": v, "value": "", "type": "string"})
            env_values.append({"key": v, "value": "", "type": "secret", "enabled": True})
    for scheme in schemes.values():  # per-request overrides may need other vars
        for v in auth_vars(scheme):
            if not any(x["key"] == v for x in variables):
                variables.append({"key": v, "value": "", "type": "string"})
                env_values.append({"key": v, "value": "", "type": "secret", "enabled": True})

    collection = {
        "info": {"_postman_id": str(uuid.uuid4()), "name": title,
                 "description": info.get("description", ""), "schema": COLLECTION_SCHEMA},
        "item": items,
        "variable": variables,
    }
    if collection_auth:
        collection["auth"] = collection_auth
    environment = {"id": str(uuid.uuid4()), "name": f"{title} - {args.env_name}",
                   "values": env_values, "_postman_variable_scope": "environment"}
    return collection, environment, warnings


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "api"


def validate(collection):
    """Structural sanity checks. Returns a list of problems."""
    problems = []

    def walk(items, trail):
        for it in items:
            here = f"{trail}/{it.get('name', '?')}"
            if "item" in it:
                walk(it["item"], here)
            else:
                req = it.get("request", {})
                if not req.get("method"):
                    problems.append(f"{here}: missing method")
                if not req.get("url", {}).get("raw"):
                    problems.append(f"{here}: missing url")
    walk(collection.get("item", []), "")
    if not collection.get("item"):
        problems.append("collection has no requests")
    return problems


def count_requests(items):
    return sum(count_requests(i["item"]) if "item" in i else 1 for i in items)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="OpenAPI 3.x file (.json, or .yaml/.yml with PyYAML)")
    ap.add_argument("--out-dir", default=".", help="where to write the files (default: current dir)")
    ap.add_argument("--name", help="collection name (default: info.title)")
    ap.add_argument("--base-url", help="override base URL (default: servers[0].url)")
    ap.add_argument("--env-name", default="Local", help="environment name suffix (default: Local)")
    ap.add_argument("--max-ms", type=int, default=2000, help="response-time test threshold in ms")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    if not str(spec.get("openapi", "")).startswith("3"):
        sys.exit("Only OpenAPI 3.x is supported (found: %r). Convert Swagger 2.0 first." % spec.get("openapi"))

    collection, environment, warnings = build(spec, args)
    problems = validate(collection)
    if problems:
        sys.exit("Invalid collection:\n  " + "\n  ".join(problems))

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = slugify(collection["info"]["name"])
    cpath = out / f"{slug}.postman_collection.json"
    epath = out / f"{slug}.postman_environment.json"
    cpath.write_text(json.dumps(collection, indent=2, ensure_ascii=False), encoding="utf-8")
    epath.write_text(json.dumps(environment, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {cpath}  ({count_requests(collection['item'])} requests, "
          f"{len(collection['item'])} folders)")
    print(f"Wrote {epath}")
    if warnings:
        print(f"\n{len(warnings)} documentation gap(s) worth fixing in the spec:")
        for w in warnings:
            print("  - " + w)


if __name__ == "__main__":
    main()
