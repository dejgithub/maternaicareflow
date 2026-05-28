"""
MaternAI CareFlow - Main Application Entry Point

Enterprise-grade AI-powered maternal healthcare coordination platform.
Integrates FastAPI, MongoDB, AI Agents, and UiPath Maestro orchestration.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models.patient import Patient
from app.models.referral import Referral, HealthcareFacility
from app.models.appointment import Appointment
from app.models.alert import Alert, Escalation
from app.routers import patients, referrals, appointments, alerts, analytics

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: initialize DB connection and seed data."""
    logger.info(f"Starting MaternAI CareFlow in {settings.environment} mode")
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri)
        await init_beanie(
            database=client[settings.database_name],
            document_models=[
                Patient, Referral, HealthcareFacility,
                Appointment, Alert, Escalation,
            ],
        )
        logger.info("MongoDB connection established and Beanie initialized")
        await seed_initial_data()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Starting without database - health check will report DB status")
        app.state.db_connected = False
    else:
        app.state.db_connected = True

    yield

    if client:
        client.close()
    logger.info("MaternAI CareFlow shutdown complete")


app = FastAPI(
    title="MaternAI CareFlow",
    description="AI-Powered Maternal Healthcare Referral & Postnatal Care Coordinator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(referrals.router)
app.include_router(appointments.router)
app.include_router(alerts.router)
app.include_router(analytics.router)


@app.get("/api/health")
async def health_check():
    db_ok = getattr(app.state, "db_connected", False)
    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "MaternAI CareFlow",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": "connected" if db_ok else "disconnected",
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to MaternAI CareFlow API",
        "docs": "/docs",
        "version": "1.0.0",
    }


async def seed_initial_data():
    """Seed database with initial healthcare facilities."""
    existing = await HealthcareFacility.find().count()
    if existing > 0:
        logger.info(f"Database already seeded ({existing} facilities found)")
        return

    facilities = [
        HealthcareFacility(
            facility_id="PHC-001",
            name="City Women's Health Center",
            type="primary_clinic",
            address="123 Health Street, Downtown",
            phone="+1-555-0101",
            email="citywhc@example.com",
            services=["antenatal_care", "postnatal_care", "family_planning", "vaccinations"],
            capacity=200,
            current_load=145,
            is_active=True,
        ),
        HealthcareFacility(
            facility_id="HOSP-001",
            name="University General Hospital",
            type="general_hospital",
            address="456 Medical Avenue, Central District",
            phone="+1-555-0202",
            email="ugh@example.com",
            services=["emergency", "maternity", "surgery", "pediatrics", "laboratory"],
            capacity=500,
            current_load=380,
            is_active=True,
        ),
        HealthcareFacility(
            facility_id="MAT-001",
            name="St. Mary's Maternity Hospital",
            type="maternity_hospital",
            address="789 Mother & Child Road, West Side",
            phone="+1-555-0303",
            email="stmarys@example.com",
            services=["maternity", "nicu", "postnatal_care", "lactation_consulting"],
            capacity=300,
            current_load=220,
            is_active=True,
        ),
        HealthcareFacility(
            facility_id="SPEC-001",
            name="National Women's Specialty Hospital",
            type="specialty_hospital",
            address="321 Specialist Boulevard, Medical Park",
            phone="+1-555-0404",
            email="nwsh@example.com",
            services=["high_risk_pregnancy", "fetal_medicine", "reproductive_endocrinology", "maternal_fetal_medicine"],
            capacity=250,
            current_load=195,
            is_active=True,
        ),
        HealthcareFacility(
            facility_id="TEACH-001",
            name="State University Teaching Hospital",
            type="teaching_hospital",
            address="555 Academic Drive, University District",
            phone="+1-555-0505",
            email="suth@example.com",
            services=["all_services", "emergency", "maternity", "nicu", "research"],
            capacity=800,
            current_load=620,
            is_active=True,
        ),
        HealthcareFacility(
            facility_id="PHC-002",
            name="Riverside Community Health Clinic",
            type="primary_clinic",
            address="888 Riverside Drive, Eastside",
            phone="+1-555-0606",
            email="riverside@example.com",
            services=["antenatal_care", "postnatal_care", "nutrition_counseling"],
            capacity=150,
            current_load=90,
            is_active=True,
        ),
    ]

    for facility in facilities:
        await facility.insert()
    logger.info(f"Seeded {len(facilities)} healthcare facilities")
