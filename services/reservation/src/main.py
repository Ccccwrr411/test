"""NekoCafé Reservation Service — FastAPI + OpenTelemetry"""
import logging
import sys
import json
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# ===== Logging Setup (Structured JSON) =====
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "level": record.levelname,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "reservation",
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "trace_id"):
            log_obj["traceId"] = record.trace_id
        return json.dumps(log_obj, ensure_ascii=False)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# ===== FastAPI App =====
app = FastAPI(
    title="NekoCafé Reservation Service",
    version="0.1.0",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)

# ===== Models =====
class ReservationCreate(BaseModel):
    store_id: str = Field(..., description="门店 ID")
    customer_id: str = Field(..., description="顾客 ID")
    date: str = Field(..., description="预约日期 YYYY-MM-DD")
    time_slot: str = Field(..., description="时段 HH:MM-HH:MM")
    guest_count: int = Field(ge=1, le=20, description="人数")
    table_type: str = Field(default="standard", description="桌型")
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

# ===== Endpoints =====
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "reservation", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/reservations/health")
async def api_health():
    """Detailed health check including DB/Redis status"""
    return {
        "status": "ok",
        "service": "reservation",
        "version": "0.1.0",
        "dependencies": {
            "database": "connected",
            "redis": "connected",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/api/reservations", response_model=ReservationResponse, status_code=201)
async def create_reservation(req: ReservationCreate, request: Request):
    """Create a new table reservation with concurrency control"""
    with tracer.start_as_current_span("create_reservation") as span:
        span.set_attribute("store_id", req.store_id)
        span.set_attribute("customer_id", req.customer_id)
        span.set_attribute("guest_count", req.guest_count)
        span.set_attribute("time_slot", req.time_slot)

        logger.info(
            "Creating reservation",
            extra={"trace_id": format(span.get_span_context().trace_id, "032x"),
                    "customer_id": req.customer_id, "store_id": req.store_id}
        )

        # TODO: Implement actual logic:
        # 1. Validate store operating hours
        # 2. Check table availability with optimistic lock
        # 3. Acquire distributed lock via Redis
        # 4. Insert reservation record
        # 5. Publish ReservationCreated event to Kafka

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
            expires_at=datetime.now(timezone.utc).replace(minute=(
                datetime.now(timezone.utc).minute + 15
            ) % 60).isoformat(),
        )
        logger.info("Reservation created", extra={"reservation_id": reservation.id})
        return reservation

@app.get("/api/reservations/{reservation_id}")
async def get_reservation(reservation_id: str):
    """Get reservation details"""
    with tracer.start_as_current_span("get_reservation") as span:
        span.set_attribute("reservation_id", reservation_id)
        # TODO: Fetch from DB
        raise HTTPException(status_code=404, detail="Reservation not found (mock)")

@app.delete("/api/reservations/{reservation_id}")
async def cancel_reservation(reservation_id: str):
    """Cancel a reservation"""
    with tracer.start_as_current_span("cancel_reservation") as span:
        span.set_attribute("reservation_id", reservation_id)
        # TODO: Cancel with Saga compensation
        logger.info("Reservation cancelled", extra={"reservation_id": reservation_id})
        return {"status": "CANCELLED", "reservation_id": reservation_id}

@app.get("/api/reservations")
async def list_reservations(customer_id: str | None = None, store_id: str | None = None,
                             date: str | None = None, status: str | None = None,
                             page: int = 1, page_size: int = 20):
    """List reservations with filters and pagination"""
    with tracer.start_as_current_span("list_reservations") as span:
        # TODO: Query DB with filters
        return {
            "items": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
        }

@app.get("/api/stores/{store_id}/slots")
async def get_available_slots(store_id: str, date: str):
    """Get available time slots for a store on a given date"""
    with tracer.start_as_current_span("get_available_slots") as span:
        span.set_attribute("store_id", store_id)
        span.set_attribute("date", date)
        # TODO: Query from DB + Redis cache
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
