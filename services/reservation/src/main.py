"""NekoCafe Reservation Service — FastAPI + OpenTelemetry"""
import logging
import sys
import json
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Structured JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "level": record.levelname,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "reservation",
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_obj, ensure_ascii=False)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NekoCafe Reservation Service",
    version="0.1.0",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ReservationCreate(BaseModel):
    store_id: str = Field(..., description="Store ID")
    customer_id: str = Field(..., description="Customer ID")
    date: str = Field(..., description="Reservation date YYYY-MM-DD")
    time_slot: str = Field(..., description="Time slot HH:MM-HH:MM")
    guest_count: int = Field(ge=1, le=20)
    table_type: str = Field(default="standard")
    remark: str = Field(default="", max_length=200)

class ReservationResponse(BaseModel):
    id: str
    store_id: str
    customer_id: str
    date: str
    time_slot: str
    guest_count: int
    status: str
    created_at: str
    expires_at: str

# Endpoints
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "reservation", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/reservations", response_model=ReservationResponse, status_code=201)
async def create_reservation(req: ReservationCreate):
    logger.info("Creating reservation", extra={"customer_id": req.customer_id, "store_id": req.store_id})
    now = datetime.now(timezone.utc).isoformat()
    reservation = ReservationResponse(
        id=f"res_{hash(req.customer_id + req.date + req.time_slot) % 10**8:08d}",
        store_id=req.store_id,
        customer_id=req.customer_id,
        date=req.date,
        time_slot=req.time_slot,
        guest_count=req.guest_count,
        status="PENDING",
        created_at=now,
        expires_at=now,
    )
    logger.info("Reservation created", extra={"reservation_id": reservation.id})
    return reservation

@app.get("/api/reservations/{reservation_id}")
async def get_reservation(reservation_id: str):
    raise HTTPException(status_code=404, detail="Reservation not found")

@app.delete("/api/reservations/{reservation_id}")
async def cancel_reservation(reservation_id: str):
    logger.info("Reservation cancelled", extra={"reservation_id": reservation_id})
    return {"status": "CANCELLED", "reservation_id": reservation_id}

@app.get("/api/reservations")
async def list_reservations(customer_id: str | None = None, store_id: str | None = None,
                             date: str | None = None, status: str | None = None,
                             page: int = 1, page_size: int = 20):
    return {"items": [], "page": page, "page_size": page_size, "total": 0}

@app.get("/api/stores/{store_id}/slots")
async def get_available_slots(store_id: str, date: str):
    return {
        "store_id": store_id,
        "date": date,
        "slots": [
            {"time": "10:00-11:00", "available": 3, "total": 10},
            {"time": "11:00-12:00", "available": 5, "total": 10},
            {"time": "12:00-13:00", "available": 1, "total": 10},
            {"time": "13:00-14:00", "available": 0, "total": 10},
        ],
    }
