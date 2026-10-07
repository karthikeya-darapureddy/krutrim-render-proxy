import os
import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI()

BACKEND_URL = os.environ["BACKEND_URL"]
BACKEND_KEY = os.environ["BACKEND_KEY"]

@app.get("/health")
async def health():
    return {"status": "ok", "proxy": "render", "backend": BACKEND_URL}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(path: str, request: Request):
    url = f"{BACKEND_URL.rstrip('/')}/{path}"

    body = await request.body()

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length"}
    }

    headers["x-proxy-key"] = BACKEND_KEY

    async with httpx.AsyncClient(timeout=180.0) as client:
        r = await client.request(
            request.method,
            url,
            content=body,
            headers=headers,
            params=request.query_params,
        )

    response_headers = {
        k: v for k, v in r.headers.items()
        if k.lower() not in {
            "content-length",
            "transfer-encoding",
            "connection",
        }
    }

    return Response(
        content=r.content,
        status_code=r.status_code,
        headers=response_headers,
        media_type=r.headers.get("content-type"),
    )