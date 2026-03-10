import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from routes import router
from models import engine, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health", response_model=dict)
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Simple dark‑theme landing page with API overview
    html = """
    <html><head><title>LinkSage API</title></head>
    <body style='background:#0F1A2C;color:#F8FAFC;font-family:Arial;padding:2rem;'>
      <h1>LinkSage – AI‑Powered Bookmark Organizer</h1>
      <p>Give your links context: AI‑generated summaries, smart tags, and adaptive top‑reads.</p>
      <h2>Available Endpoints</h2>
      <ul style='list-style:none;padding:0;'>
        <li><b>GET</b> <code>/health</code> – health check</li>
        <li><b>POST</b> <code>/api/links</code> – add a link (AI summary & tags)</li>
        <li><b>GET</b> <code>/api/dashboard</code> – get adaptive top reads</li>
        <li><b>GET</b> <code>/api/links/{{id}}/health</code> – link health status</li>
      </ul>
      <h2>Tech Stack</h2>
      <ul>
        <li>FastAPI 0.115.0</li>
        <li>PostgreSQL via SQLAlchemy 2.0.35</li>
        <li>DigitalOcean Serverless Inference (model: openai-gpt-oss-120b)</li>
        <li>Python 3.12+</li>
      </ul>
      <p><a href="/docs" style='color:#FF6B35;'>OpenAPI Docs</a> | <a href="/redoc" style='color:#FF6B35;'>ReDoc</a></p>
    </body></html>
    """
    return HTMLResponse(content=html, status_code=200)
