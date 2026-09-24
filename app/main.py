import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel

from app.metrics import CALCULATIONS, MetricsMiddleware
from app.pace import PaceError, calculate

VERSION = os.getenv("APP_VERSION", "dev")
GREETING = os.getenv("APP_GREETING", "Work out your running pace.")

app = FastAPI(title="pacer", version=VERSION)
app.add_middleware(MetricsMiddleware)

ready = True


class PaceRequest(BaseModel):
    distance_km: float
    duration: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>pacer</title>
<style>
  body {{ font: 16px/1.6 system-ui, sans-serif; max-width: 30rem;
         margin: 4rem auto; padding: 0 1.5rem; }}
  input, button {{ font: inherit; padding: .5rem; width: 100%;
                   margin-bottom: .75rem; box-sizing: border-box; }}
  output {{ display: block; font-size: 1.5rem; font-weight: 600; }}
  small {{ color: #666; }}
</style></head>
<body>
  <h1>pacer</h1>
  <p>{GREETING}</p>
  <input id="d" type="number" step="0.01" placeholder="Distance in km" value="21.0975">
  <input id="t" type="text" placeholder="Time as HH:MM:SS" value="2:00:00">
  <button onclick="go()">Calculate</button>
  <output id="out"></output>
  <p><small>version {VERSION}</small></p>
<script>
async function go() {{
  const body = {{ distance_km: Number(document.getElementById('d').value),
                  duration: document.getElementById('t').value }};
  const r = await fetch('/api/pace', {{ method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(body) }});
  const j = await r.json();
  document.getElementById('out').textContent =
    r.ok ? j.pace + '  ·  ' + j.speed_kmh.toFixed(2) + ' km/h' : j.detail;
}}
</script>
</body></html>"""


@app.post("/api/pace")
def pace(req: PaceRequest) -> dict:
    try:
        result = calculate(req.distance_km, req.duration)
    except PaceError as exc:
        CALCULATIONS.labels("invalid").inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    CALCULATIONS.labels("ok").inc()
    return {
        "pace": result.pace_label(),
        "pace_seconds_per_km": round(result.pace_seconds_per_km, 2),
        "speed_kmh": result.speed_kmh,
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "alive"}


@app.get("/readyz")
def readyz() -> dict:
    if not ready:
        raise HTTPException(status_code=503, detail="not ready")
    return {"status": "ready"}


@app.get("/version")
def version() -> dict:
    return {"version": VERSION}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
