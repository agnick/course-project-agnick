import time

from fastapi import APIRouter

from app.core.db import _DB

router = APIRouter()

STARTUP_TS = time.time()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/metrics")
def metrics():
    uptime = round(time.time() - STARTUP_TS, 2)
    total = len(_DB["wishes"])
    avg_price = (
        sum(w.get("price_estimate", 0) for w in _DB["wishes"]) / total
        if total > 0
        else 0
    )
    return {"uptime_s": uptime, "total_wishes": total, "avg_price": round(avg_price, 2)}
