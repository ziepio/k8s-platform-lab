import time

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

REQUESTS = Counter(
    "pacer_http_requests_total",
    "HTTP requests handled",
    ["method", "path", "status"],
)

LATENCY = Histogram(
    "pacer_http_request_duration_seconds",
    "How long each request took",
    ["method", "path"],
)

CALCULATIONS = Counter(
    "pacer_calculations_total",
    "Pace calculations performed",
    ["outcome"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        LATENCY.labels(request.method, path).observe(time.perf_counter() - started)
        REQUESTS.labels(request.method, path, response.status_code).inc()
        return response
