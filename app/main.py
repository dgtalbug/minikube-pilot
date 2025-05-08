from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from prometheus_client import (
    Counter,
    generate_latest,
    Gauge,
    CONTENT_TYPE_LATEST,
)
from dotenv import load_dotenv
import os
import psutil
import threading
import time
import random
import socket

load_dotenv()
app = FastAPI()

REQUEST_COUNT = Counter("get_info_requests_total", "Total number of GET /get_info requests")
REQUEST_COUNT_PER_VERSION = Counter(
    "get_info_requests_total_by_version",
    "GET /get_info requests by app version",
    ["version"]
)
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage percentage")
UPTIME = Gauge("uptime_seconds", "App uptime in seconds")
THREAD_COUNT = Gauge("thread_count", "Number of active threads")
DISK_USAGE = Gauge("disk_usage_percent", "Disk usage percentage")

START_TIME = time.time()

@app.get("/")
def root():
    return RedirectResponse(url="/get_info")

@app.get("/get_info")
async def get_info():
    app_title = os.getenv("APP_TITLE", "My FastAPI App")
    app_version = os.getenv("APP_VERSION", "1.0")

    REQUEST_COUNT.inc()
    REQUEST_COUNT_PER_VERSION.labels(version=app_version).inc()

    return {
        "APP_VERSION": app_version,
        "APP_TITLE": app_title,
        "MESSAGE": "Hello from " + socket.gethostname(),
    }

@app.get("/metrics")
def metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    UPTIME.set(time.time() - START_TIME)
    THREAD_COUNT.set(threading.active_count())
    DISK_USAGE.set(psutil.disk_usage("/").percent)

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
