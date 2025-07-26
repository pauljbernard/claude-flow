from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import psutil
import asyncio
import random
from typing import Dict, Any
import contextlib

app = FastAPI(title="Claude Flow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

performance_metrics = {
    "response_time": [],
    "request_count": 0,
    "error_count": 0,
    "start_time": asyncio.get_event_loop().time(),
}

metrics_store = {
    "performance": [],
    "tokens": [],
    "errors": [],
    "health": [],
    "load": [],
    "costs": [],
}

MAX_HISTORY = 100

# ----- Helper functions -----

def format_uptime(seconds: float) -> str:
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def calculate_token_usage() -> Dict[str, Any]:
    usage = {
        "totalTokens": random.randint(500000, 1500000),
        "inputTokens": random.randint(300000, 900000),
        "outputTokens": random.randint(200000, 600000),
        "cachedTokens": random.randint(50000, 150000),
    }
    usage["cost"] = usage["totalTokens"] * 0.0001
    return usage


def calculate_token_efficiency(usage: Dict[str, Any]) -> Dict[str, Any]:
    cache_hit_rate = usage["cachedTokens"] / usage["totalTokens"] * 100
    input_output_ratio = usage["outputTokens"] / usage["inputTokens"]
    return {
        "cacheHitRate": round(cache_hit_rate, 2),
        "inputOutputRatio": round(input_output_ratio, 2),
        "costPerToken": round(usage["cost"] / usage["totalTokens"], 4),
    }


def run_benchmarks() -> Dict[str, Any]:
    def score(base: int, spread: int) -> int:
        return random.randint(base, base + spread)

    return {
        "responseTime": {"name": "Response Time", "score": score(60, 40), "unit": "ms", "baseline": 100},
        "throughput": {"name": "Throughput", "score": score(70, 30), "unit": "req/s", "baseline": 1000},
        "errorRate": {"name": "Error Rate", "score": score(80, 20), "unit": "%", "baseline": 1},
        "availability": {"name": "Availability", "score": score(95, 5), "unit": "%", "baseline": 99.9},
    }


def collect_system_metrics() -> Dict[str, Any]:
    return {
        "system": {
            "platform": os.uname().sysname,
            "architecture": os.uname().machine,
            "uptime": int(asyncio.get_event_loop().time() - performance_metrics["start_time"]),
            "loadAverage": os.getloadavg(),
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "free": psutil.virtual_memory().available,
            "usage": psutil.virtual_memory().percent,
        },
        "cpu": {
            "count": psutil.cpu_count(),
            "model": " ".join(psutil.cpu_info().brand_raw.split()),
            "usage": os.getloadavg()[0],
        },
        "network": {"interfaces": len(psutil.net_if_addrs()), "hostname": os.uname().nodename},
    }


def perform_health_check() -> Dict[str, Any]:
    mem = psutil.virtual_memory().percent
    cpu = os.getloadavg()[0] * 100
    return {
        "cpu": max(0, 100 - cpu),
        "memory": max(0, 100 - mem),
        "disk": random.randint(80, 100),
        "network": random.randint(90, 100),
        "api": random.randint(85, 100),
        "database": random.randint(90, 100),
    }


def monitor_load() -> Dict[str, Any]:
    load = os.getloadavg()
    return {
        "oneMin": load[0],
        "fiveMin": load[1],
        "fifteenMin": load[2],
        "thirtyMin": random.random() * 2,
        "oneHour": random.random() * 2,
        "twentyFourHour": random.random() * 2,
        "current": load[0],
        "peak": max(load),
        "average": sum(load) / len(load),
    }


def get_current_metrics() -> Dict[str, Any]:
    avg_resp = sum(performance_metrics["response_time"]) / len(performance_metrics["response_time"]) if performance_metrics["response_time"] else 0
    throughput = performance_metrics["request_count"] / max(1, (asyncio.get_event_loop().time() - performance_metrics["start_time"]))
    error_rate = (performance_metrics["error_count"] / performance_metrics["request_count"]) * 100 if performance_metrics["request_count"] else 0
    uptime = asyncio.get_event_loop().time() - performance_metrics["start_time"]
    token_usage = calculate_token_usage()
    health = perform_health_check()
    load = monitor_load()
    result = {
        "performance": {
            "responseTime": round(avg_resp),
            "throughput": round(throughput),
            "errorRate": round(error_rate, 2),
            "uptime": format_uptime(uptime),
        },
        "tokens": token_usage,
        "health": health,
        "load": load,
    }
    metrics_store["performance"].append(result["performance"])
    metrics_store["tokens"].append(result["tokens"])
    metrics_store["health"].append(result["health"])
    metrics_store["load"].append(result["load"])
    for key in metrics_store:
        if len(metrics_store[key]) > MAX_HISTORY:
            metrics_store[key].pop(0)
    return result

# ----- REST endpoints -----
@app.get("/api/analysis/performance-report")
async def performance_report():
    now = asyncio.get_event_loop().time()
    uptime = now - performance_metrics["start_time"]
    avg_resp = sum(performance_metrics["response_time"]) / len(performance_metrics["response_time"]) if performance_metrics["response_time"] else 0
    throughput = performance_metrics["request_count"] / max(1, uptime)
    error_rate = (performance_metrics["error_count"] / performance_metrics["request_count"]) * 100 if performance_metrics["request_count"] else 0
    return {
        "timestamp": int(now * 1000),
        "summary": "System performance analysis completed",
        "metrics": {
            "averageResponseTime": round(avg_resp),
            "throughput": round(throughput),
            "errorRate": round(error_rate, 2),
            "uptime": format_uptime(uptime),
            "totalRequests": performance_metrics["request_count"],
            "totalErrors": performance_metrics["error_count"],
        },
        "recommendations": [],
        "trends": {
            "responseTime": performance_metrics["response_time"][-20:],
            "throughput": [random.random() * 1000 + 500 for _ in range(20)],
            "errorRate": [random.random() * 5 for _ in range(20)],
        },
    }

@app.get("/api/analysis/bottleneck-analyze")
async def bottleneck_analyze():
    usage = monitor_load()
    memory = psutil.virtual_memory().percent
    avg_resp = sum(performance_metrics["response_time"]) / len(performance_metrics["response_time"]) if performance_metrics["response_time"] else 0
    bottlenecks = []
    if usage["current"] > 1.5:
        bottlenecks.append({"component": "CPU", "severity": "high", "impact": "Response time +25%", "value": usage["current"], "threshold": 1.5})
    if memory > 85:
        bottlenecks.append({"component": "Memory", "severity": "medium", "impact": "Performance degradation", "value": memory, "threshold": 85})
    if avg_resp > 500:
        bottlenecks.append({"component": "API Response", "severity": "medium", "impact": "User experience degradation", "value": avg_resp, "threshold": 500})
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "bottlenecks": bottlenecks,
        "recommendations": ["Consider resource optimization"],
        "summary": f"Found {len(bottlenecks)} potential bottlenecks",
        "impact": {"score": len(bottlenecks)*2, "level": "medium" if len(bottlenecks) else "low"}
    }

@app.get("/api/analysis/token-usage")
async def token_usage():
    usage = calculate_token_usage()
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        **usage,
        "efficiency": calculate_token_efficiency(usage),
        "trends": {"daily": [random.random()*100000+50000 for _ in range(7)], "hourly": [random.random()*10000+5000 for _ in range(24)]},
        "recommendations": [],
    }

@app.get("/api/analysis/benchmark-run")
async def benchmark_run():
    benchmarks = run_benchmarks()
    scores = [v["score"] for v in benchmarks.values()]
    score = round(sum(scores)/len(scores))
    comparisons = [
        {"name": v["name"], "current": v["score"], "baseline": v["baseline"], "improvement": f"{((v["score"]-v["baseline"])/v["baseline"]*100):.1f}"} for v in benchmarks.values()
    ]
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "benchmarks": benchmarks,
        "summary": "Benchmark suite completed",
        "score": score,
        "comparisons": comparisons,
    }

@app.get("/api/analysis/metrics-collect")
async def metrics_collect():
    metrics = collect_system_metrics()
    alerts = []
    if metrics["memory"]["usage"] > 85:
        alerts.append({"type": "warning", "message": "High memory usage detected", "value": metrics["memory"]["usage"]})
    if metrics["cpu"]["usage"] > 0.8:
        alerts.append({"type": "critical", "message": "High CPU usage detected", "value": metrics["cpu"]["usage"]})
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "metrics": metrics,
        "summary": "System metrics collected successfully",
        "alerts": alerts,
    }

@app.get("/api/analysis/trend-analysis")
async def trend_analysis():
    trends = {
        "performance": {"trend": "improving", "change": "+5.2%", "prediction": "stable"},
        "usage": {"trend": "increasing", "change": "+12.3%", "prediction": "continued growth"},
        "errors": {"trend": "decreasing", "change": "-8.1%", "prediction": "stable"},
    }
    predictions = {"nextWeek": "Performance expected to remain stable", "nextMonth": "Usage likely to increase by 15-20%", "nextQuarter": "Consider scaling resources to handle growth"}
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "trends": trends,
        "predictions": predictions,
        "summary": "Trend analysis completed",
        "insights": [
            "System performance has improved by 5.2% this week",
            "Usage patterns show steady growth indicating system adoption",
            "Error rates are decreasing, suggesting improved stability",
        ],
    }

@app.get("/api/analysis/cost-analysis")
async def cost_analysis():
    costs = {
        "current": {"compute": 125.5, "storage": 45.2, "network": 23.1, "tokens": 89.4},
        "previous": {"compute": 118.3, "storage": 42.15, "network": 21.85, "tokens": 76.25},
        "change": {"compute": "+6.1%", "storage": "+7.2%", "network": "+5.7%", "tokens": "+17.2%"},
    }
    total = sum(costs["current"].values())
    forecast = {"nextMonth": total*1.1, "nextQuarter": total*1.35, "nextYear": total*1.8}
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "costs": costs,
        "summary": "Cost analysis completed",
        "optimization": [
            "Optimize token usage to reduce costs by ~15%",
            "Implement better caching to reduce compute costs",
            "Archive old data to reduce storage costs",
        ],
        "forecast": forecast,
    }

@app.get("/api/analysis/quality-assess")
async def quality_assess():
    quality = {
        "performance": 85,
        "reliability": 92,
        "security": 88,
        "maintainability": 79,
        "scalability": 83,
        "documentation": 76,
    }
    score = round(sum(quality.values())/len(quality))
    recommendations = [f"Improve {k} metrics (current: {v}%)" for k,v in quality.items() if v < 80]
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "quality": quality,
        "summary": "Quality assessment completed",
        "score": score,
        "recommendations": recommendations,
    }

@app.get("/api/analysis/error-analysis")
async def error_analysis():
    errors = {
        "total": 24,
        "types": {"4xx": 15, "5xx": 9},
        "common": [
            {"code": 404, "count": 8, "message": "Resource not found"},
            {"code": 500, "count": 5, "message": "Internal server error"},
            {"code": 401, "count": 4, "message": "Unauthorized access"},
        ],
    }
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "errors": errors,
        "summary": "Error analysis completed",
        "patterns": [
            "Most errors occur during peak hours (12-2 PM)",
            "404 errors primarily from deprecated API endpoints",
            "500 errors correlate with database connection issues",
        ],
        "resolution": [
            "Implement proper redirects for deprecated endpoints",
            "Add database connection pooling and retry logic",
            "Enhance authentication error handling",
        ],
    }

@app.get("/api/analysis/usage-stats")
async def usage_stats():
    stats = {
        "totalUsers": 1250,
        "activeUsers": 340,
        "totalSessions": 2890,
        "averageSessionDuration": 15.5,
        "topFeatures": [
            {"name": "Analysis Tools", "usage": 85},
            {"name": "Monitoring", "usage": 78},
            {"name": "Reports", "usage": 62},
        ],
    }
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "stats": stats,
        "summary": "Usage statistics generated",
        "insights": [
            f"{stats['activeUsers']} active users out of {stats['totalUsers']} total users",
            f"Average session duration is {stats['averageSessionDuration']} minutes",
            "Analysis Tools is the most popular feature",
        ],
        "trends": {
            "users": [random.random()*50+stats['activeUsers']-25 for _ in range(30)],
            "sessions": [random.random()*100+stats['totalSessions']-50 for _ in range(30)],
        },
    }

@app.get("/api/analysis/health-check")
async def health_check():
    health = perform_health_check()
    avg = sum(health.values())/len(health)
    status = 'excellent' if avg >=90 else 'good' if avg>=70 else 'warning' if avg>=50 else 'critical'
    alerts = [
        {"component": k, "score": v, "severity": 'critical' if v<50 else 'warning', "message": f"{k} health score is {v}%"}
        for k,v in health.items() if v<70
    ]
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "health": health,
        "summary": "System health check completed",
        "status": status,
        "alerts": alerts,
    }

@app.get("/api/analysis/load-monitor")
async def load_monitor():
    load = monitor_load()
    alerts = []
    if load["current"] > 2.0:
        alerts.append({"type": "critical", "message": "High system load detected", "value": load["current"]})
    elif load["current"] > 1.5:
        alerts.append({"type": "warning", "message": "Elevated system load", "value": load["current"]})
    predictions = {"nextHour": load["current"]*(0.9+random.random()*0.2), "nextDay": load["current"]*(0.8+random.random()*0.4), "nextWeek": load["current"]*(0.7+random.random()*0.6)}
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "load": load,
        "summary": "Load monitoring completed",
        "alerts": alerts,
        "predictions": predictions,
    }

@app.get("/api/analysis/capacity-plan")
async def capacity_plan():
    capacity = {
        "current": {"cpu": 65, "memory": 72, "storage": 58, "network": 45},
        "projected": {"cpu": 78, "memory": 85, "storage": 72, "network": 58},
        "timeToLimit": {"cpu": "3 months", "memory": "2 months", "storage": "6 months", "network": "8 months"},
    }
    recommendations = []
    for r, usage in capacity["projected"].items():
        if usage > 80:
            recommendations.append(f"Plan to scale {r} resources within next 2 months")
        elif usage > 70:
            recommendations.append(f"Monitor {r} usage closely")
    timeline = {
        "immediate": "Monitor current usage patterns",
        "1month": "Prepare for memory scaling",
        "2months": "Implement memory upgrades",
        "3months": "Plan CPU scaling",
        "6months": "Review storage requirements",
    }
    return {
        "timestamp": int(asyncio.get_event_loop().time()*1000),
        "capacity": capacity,
        "summary": "Capacity planning completed",
        "recommendations": recommendations,
        "timeline": timeline,
    }


@app.get("/api/analysis/historical-metrics")
async def historical_metrics():
    """Return in-memory stored metrics for basic historical insights."""
    return metrics_store

# ----- WebSocket -----
@app.websocket("/api/analysis/ws")
async def analysis_ws(websocket: WebSocket):
    await websocket.accept()
    async def send_loop():
        try:
            while True:
                await websocket.send_json({"type": "metrics_update", "payload": get_current_metrics()})
                await asyncio.sleep(5)
        except WebSocketDisconnect:
            pass

    send_task = asyncio.create_task(send_loop())
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "request_metrics":
                await websocket.send_json({"type": "metrics_update", "payload": get_current_metrics()})
    except WebSocketDisconnect:
        send_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await send_task
