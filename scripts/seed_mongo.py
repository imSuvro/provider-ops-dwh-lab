"""Seed MongoDB with deterministic, clearly synthetic demo source data."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEED_BATCH = "portfolio_demo_v1"
COLLECTIONS = (
    "customers",
    "providers",
    "patients",
    "programs",
    "enrollments",
    "consents",
    "timer_sessions",
    "device_orders",
    "coordinator_notes",
)

PROGRAM_CODES = {"RPM", "RTM", "CCM", "CoCM", "APCM"}
ENROLLMENT_STATUSES = {
    "RECEIVED",
    "ELIGIBLE",
    "CONSENTED",
    "ONBOARDED",
    "ACTIVE",
    "DECLINED",
}
CONSENT_STATUSES = {"PENDING", "COMPLETED", "DECLINED"}
DEVICE_ORDER_STATUSES = {"ORDERED", "SHIPPED", "DELIVERED", "DELAYED"}


def utc_datetime(value: str) -> datetime:
    """Convert an ISO date or timestamp to a UTC-aware datetime."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def tagged(document: dict[str, Any]) -> dict[str, Any]:
    """Add the marker used to make seed and reset operations safely repeatable."""
    return {**document, "seed_batch": SEED_BATCH}


CUSTOMERS = [
    tagged(
        {
            "_id": "cust_001",
            "customer_code": "NORTHSTAR_DEMO",
            "customer_name": "Northstar Family Health (Demo)",
            "region": "Midwest",
            "timezone": "America/Chicago",
            "active": True,
            "contract_start_date": utc_datetime("2025-01-01"),
        }
    ),
    tagged(
        {
            "_id": "cust_002",
            "customer_code": "HARBOR_DEMO",
            "customer_name": "Harbor Community Clinic (Demo)",
            "region": "Northeast",
            "timezone": "America/New_York",
            "active": True,
            "contract_start_date": utc_datetime("2025-02-01"),
        }
    ),
    tagged(
        {
            "_id": "cust_003",
            "customer_code": "SUMMIT_DEMO",
            "customer_name": "Summit Primary Care Group (Demo)",
            "region": "Mountain",
            "timezone": "America/Denver",
            "active": True,
            "contract_start_date": utc_datetime("2025-03-01"),
        }
    ),
]

PROVIDERS = [
    tagged(
        {
            "_id": "provider_001",
            "provider_external_id": "DEMO-PROV-001",
            "customer_id": "cust_001",
            "display_name": "Dr. Mira Example",
            "specialty": "Family Medicine",
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "provider_002",
            "provider_external_id": "DEMO-PROV-002",
            "customer_id": "cust_001",
            "display_name": "Dr. Leon Sample",
            "specialty": "Internal Medicine",
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "provider_003",
            "provider_external_id": "DEMO-PROV-003",
            "customer_id": "cust_002",
            "display_name": "Dr. Priya Demo",
            "specialty": "Family Medicine",
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "provider_004",
            "provider_external_id": "DEMO-PROV-004",
            "customer_id": "cust_002",
            "display_name": "Dr. Owen Test",
            "specialty": "Behavioral Health",
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "provider_005",
            "provider_external_id": "DEMO-PROV-005",
            "customer_id": "cust_003",
            "display_name": "Dr. Hana Placeholder",
            "specialty": "Internal Medicine",
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "provider_006",
            "provider_external_id": "DEMO-PROV-006",
            "customer_id": "cust_003",
            "display_name": "Dr. Elias Fixture",
            "specialty": "Physical Medicine",
            "active": True,
        }
    ),
]


def patient(
    patient_id: str,
    external_id: str,
    customer_id: str,
    provider_id: str,
    first_name: str,
    last_name: str,
    birth_date: str,
    state: str,
) -> dict[str, Any]:
    return tagged(
        {
            "_id": patient_id,
            "patient_external_id": external_id,
            "customer_id": customer_id,
            "primary_provider_id": provider_id,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": utc_datetime(birth_date),
            "state": state,
            "active": True,
            "created_at": utc_datetime("2025-12-15T09:00:00"),
        }
    )


PATIENTS = [
    patient(
        "patient_001",
        "DEMO-PAT-001",
        "cust_001",
        "provider_001",
        "Avery",
        "Sample",
        "1958-04-12",
        "IL",
    ),
    patient(
        "patient_002",
        "DEMO-PAT-002",
        "cust_001",
        "provider_001",
        "Jordan",
        "Example",
        "1964-09-23",
        "IL",
    ),
    patient(
        "patient_003",
        "DEMO-PAT-003",
        "cust_001",
        "provider_002",
        "Taylor",
        "Demo",
        "1971-01-08",
        "WI",
    ),
    patient(
        "patient_004",
        "DEMO-PAT-004",
        "cust_001",
        "provider_002",
        "Morgan",
        "Test",
        "1955-11-30",
        "IL",
    ),
    patient(
        "patient_005",
        "DEMO-PAT-005",
        "cust_002",
        "provider_003",
        "Riley",
        "Sample",
        "1960-06-17",
        "MA",
    ),
    patient(
        "patient_006",
        "DEMO-PAT-006",
        "cust_002",
        "provider_003",
        "Casey",
        "Example",
        "1974-02-14",
        "RI",
    ),
    patient(
        "patient_007",
        "DEMO-PAT-007",
        "cust_002",
        "provider_004",
        "Quinn",
        "Demo",
        "1980-08-02",
        "MA",
    ),
    patient(
        "patient_008",
        "DEMO-PAT-008",
        "cust_002",
        "provider_004",
        "Cameron",
        "Test",
        "1968-12-19",
        "NH",
    ),
    patient(
        "patient_009",
        "DEMO-PAT-009",
        "cust_003",
        "provider_005",
        "Dakota",
        "Sample",
        "1959-03-05",
        "CO",
    ),
    patient(
        "patient_010",
        "DEMO-PAT-010",
        "cust_003",
        "provider_005",
        "Robin",
        "Example",
        "1977-07-27",
        "CO",
    ),
    patient(
        "patient_011",
        "DEMO-PAT-011",
        "cust_003",
        "provider_006",
        "Skyler",
        "Demo",
        "1966-10-10",
        "UT",
    ),
    patient(
        "patient_012",
        "DEMO-PAT-012",
        "cust_003",
        "provider_006",
        "Drew",
        "Test",
        "1983-05-21",
        "CO",
    ),
]

PROGRAMS = [
    tagged(
        {
            "_id": "program_rpm",
            "program_code": "RPM",
            "program_name": "Remote Patient Monitoring",
            "requires_device": True,
            "monthly_minimum_minutes": 20,
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "program_rtm",
            "program_code": "RTM",
            "program_name": "Remote Therapeutic Monitoring",
            "requires_device": True,
            "monthly_minimum_minutes": 20,
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "program_ccm",
            "program_code": "CCM",
            "program_name": "Chronic Care Management",
            "requires_device": False,
            "monthly_minimum_minutes": 20,
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "program_cocm",
            "program_code": "CoCM",
            "program_name": "Collaborative Care Management",
            "requires_device": False,
            "monthly_minimum_minutes": 70,
            "active": True,
        }
    ),
    tagged(
        {
            "_id": "program_apcm",
            "program_code": "APCM",
            "program_name": "Advanced Primary Care Management",
            "requires_device": False,
            "monthly_minimum_minutes": 0,
            "active": True,
        }
    ),
]

PATIENT_BY_ID = {document["_id"]: document for document in PATIENTS}
PROGRAM_BY_CODE = {document["program_code"]: document for document in PROGRAMS}


def enrollment(
    enrollment_id: str,
    patient_id: str,
    program_code: str,
    status: str,
    received_at: str,
    status_updated_at: str,
) -> dict[str, Any]:
    source_patient = PATIENT_BY_ID[patient_id]
    return tagged(
        {
            "_id": enrollment_id,
            "patient_id": patient_id,
            "customer_id": source_patient["customer_id"],
            "provider_id": source_patient["primary_provider_id"],
            "program_id": PROGRAM_BY_CODE[program_code]["_id"],
            "program_code": program_code,
            "status": status,
            "received_at": utc_datetime(received_at),
            "status_updated_at": utc_datetime(status_updated_at),
        }
    )


ENROLLMENTS = [
    enrollment(
        "enrollment_001",
        "patient_001",
        "RPM",
        "ACTIVE",
        "2025-12-18",
        "2026-01-05",
    ),
    enrollment(
        "enrollment_002",
        "patient_001",
        "CCM",
        "ONBOARDED",
        "2025-12-20",
        "2026-01-07",
    ),
    enrollment(
        "enrollment_003",
        "patient_002",
        "RTM",
        "CONSENTED",
        "2026-01-02",
        "2026-01-08",
    ),
    enrollment(
        "enrollment_004",
        "patient_003",
        "CCM",
        "ELIGIBLE",
        "2026-01-04",
        "2026-01-09",
    ),
    enrollment(
        "enrollment_005",
        "patient_004",
        "CoCM",
        "DECLINED",
        "2026-01-05",
        "2026-01-10",
    ),
    enrollment(
        "enrollment_006",
        "patient_005",
        "APCM",
        "ACTIVE",
        "2025-12-19",
        "2026-01-03",
    ),
    enrollment(
        "enrollment_007",
        "patient_005",
        "RPM",
        "ACTIVE",
        "2025-12-21",
        "2026-01-06",
    ),
    enrollment(
        "enrollment_008",
        "patient_006",
        "CCM",
        "RECEIVED",
        "2026-01-11",
        "2026-01-11",
    ),
    enrollment(
        "enrollment_009",
        "patient_007",
        "RTM",
        "ONBOARDED",
        "2025-12-28",
        "2026-01-12",
    ),
    enrollment(
        "enrollment_010",
        "patient_008",
        "CoCM",
        "CONSENTED",
        "2025-12-29",
        "2026-01-10",
    ),
    enrollment(
        "enrollment_011",
        "patient_009",
        "APCM",
        "ELIGIBLE",
        "2026-01-03",
        "2026-01-08",
    ),
    enrollment(
        "enrollment_012",
        "patient_009",
        "CCM",
        "ACTIVE",
        "2025-12-17",
        "2026-01-04",
    ),
    enrollment(
        "enrollment_013",
        "patient_010",
        "RPM",
        "DECLINED",
        "2026-01-01",
        "2026-01-07",
    ),
    enrollment(
        "enrollment_014",
        "patient_011",
        "CoCM",
        "RECEIVED",
        "2026-01-12",
        "2026-01-12",
    ),
    enrollment(
        "enrollment_015",
        "patient_012",
        "RTM",
        "ACTIVE",
        "2025-12-22",
        "2026-01-06",
    ),
    enrollment(
        "enrollment_016",
        "patient_002",
        "APCM",
        "ELIGIBLE",
        "2026-01-06",
        "2026-01-11",
    ),
]

ENROLLMENT_BY_ID = {document["_id"]: document for document in ENROLLMENTS}


def consent(
    consent_id: str,
    enrollment_id: str,
    status: str,
    requested_at: str,
    completed_at: str | None = None,
) -> dict[str, Any]:
    source_enrollment = ENROLLMENT_BY_ID[enrollment_id]
    return tagged(
        {
            "_id": consent_id,
            "enrollment_id": enrollment_id,
            "patient_id": source_enrollment["patient_id"],
            "program_code": source_enrollment["program_code"],
            "status": status,
            "requested_at": utc_datetime(requested_at),
            "completed_at": (
                utc_datetime(completed_at) if completed_at is not None else None
            ),
            "method": "PHONE" if status != "PENDING" else "PORTAL",
        }
    )


CONSENTS = [
    consent("consent_001", "enrollment_001", "COMPLETED", "2025-12-20", "2025-12-22"),
    consent("consent_002", "enrollment_002", "COMPLETED", "2025-12-22", "2025-12-28"),
    consent("consent_003", "enrollment_003", "COMPLETED", "2026-01-03", "2026-01-08"),
    consent("consent_004", "enrollment_004", "PENDING", "2026-01-09"),
    consent("consent_005", "enrollment_005", "DECLINED", "2026-01-06", "2026-01-10"),
    consent("consent_006", "enrollment_006", "COMPLETED", "2025-12-21", "2025-12-27"),
    consent("consent_007", "enrollment_007", "COMPLETED", "2025-12-23", "2025-12-29"),
    consent("consent_008", "enrollment_008", "PENDING", "2026-01-11"),
    consent("consent_009", "enrollment_009", "COMPLETED", "2025-12-30", "2026-01-04"),
    consent("consent_010", "enrollment_010", "COMPLETED", "2025-12-30", "2026-01-10"),
    consent("consent_011", "enrollment_011", "PENDING", "2026-01-08"),
    consent("consent_012", "enrollment_012", "COMPLETED", "2025-12-20", "2025-12-27"),
    consent("consent_013", "enrollment_013", "DECLINED", "2026-01-02", "2026-01-07"),
    consent("consent_014", "enrollment_014", "PENDING", "2026-01-12"),
    consent("consent_015", "enrollment_015", "COMPLETED", "2025-12-23", "2025-12-30"),
    consent("consent_016", "enrollment_016", "PENDING", "2026-01-11"),
]


def timer_session(
    session_id: str,
    enrollment_id: str,
    duration_minutes: int,
    session_date: str,
    activity_type: str,
) -> dict[str, Any]:
    source_enrollment = ENROLLMENT_BY_ID[enrollment_id]
    return tagged(
        {
            "_id": session_id,
            "enrollment_id": enrollment_id,
            "patient_id": source_enrollment["patient_id"],
            "provider_id": source_enrollment["provider_id"],
            "program_code": source_enrollment["program_code"],
            "duration_minutes": duration_minutes,
            "session_date": utc_datetime(session_date),
            "activity_type": activity_type,
        }
    )


TIMER_SESSIONS = [
    timer_session("timer_001", "enrollment_001", 12, "2026-01-08", "DEVICE_REVIEW"),
    timer_session("timer_002", "enrollment_001", 16, "2026-01-22", "CARE_COORDINATION"),
    timer_session("timer_003", "enrollment_002", 12, "2026-01-18", "CARE_PLAN_REVIEW"),
    timer_session("timer_004", "enrollment_003", 14, "2026-01-14", "THERAPY_REVIEW"),
    timer_session("timer_005", "enrollment_003", 11, "2026-01-25", "PATIENT_OUTREACH"),
    timer_session("timer_006", "enrollment_006", 8, "2026-01-15", "CARE_COORDINATION"),
    timer_session("timer_007", "enrollment_007", 13, "2026-01-10", "DEVICE_REVIEW"),
    timer_session("timer_008", "enrollment_007", 14, "2026-01-24", "PATIENT_OUTREACH"),
    timer_session("timer_009", "enrollment_009", 9, "2026-01-17", "THERAPY_REVIEW"),
    timer_session("timer_010", "enrollment_009", 7, "2026-01-28", "PATIENT_OUTREACH"),
    timer_session("timer_011", "enrollment_010", 35, "2026-01-09", "CASE_REVIEW"),
    timer_session("timer_012", "enrollment_010", 42, "2026-01-23", "CARE_COORDINATION"),
    timer_session("timer_013", "enrollment_012", 10, "2026-01-11", "CARE_PLAN_REVIEW"),
    timer_session("timer_014", "enrollment_012", 13, "2026-01-26", "PATIENT_OUTREACH"),
    timer_session("timer_015", "enrollment_015", 18, "2026-01-13", "THERAPY_REVIEW"),
    timer_session("timer_016", "enrollment_015", 14, "2026-01-27", "CARE_COORDINATION"),
]


def device_order(
    order_id: str,
    enrollment_id: str,
    status: str,
    device_type: str,
    ordered_at: str,
    status_updated_at: str,
) -> dict[str, Any]:
    source_enrollment = ENROLLMENT_BY_ID[enrollment_id]
    return tagged(
        {
            "_id": order_id,
            "enrollment_id": enrollment_id,
            "patient_id": source_enrollment["patient_id"],
            "customer_id": source_enrollment["customer_id"],
            "program_code": source_enrollment["program_code"],
            "device_type": device_type,
            "status": status,
            "ordered_at": utc_datetime(ordered_at),
            "status_updated_at": utc_datetime(status_updated_at),
            "tracking_reference": f"DEMO-TRACK-{order_id[-3:]}",
        }
    )


DEVICE_ORDERS = [
    device_order(
        "order_001",
        "enrollment_001",
        "DELIVERED",
        "Blood Pressure Monitor",
        "2025-12-23",
        "2025-12-29",
    ),
    device_order(
        "order_002",
        "enrollment_003",
        "SHIPPED",
        "Connected Therapy Sensor",
        "2026-01-09",
        "2026-01-11",
    ),
    device_order(
        "order_003",
        "enrollment_007",
        "DELIVERED",
        "Weight Scale",
        "2025-12-30",
        "2026-01-04",
    ),
    device_order(
        "order_004",
        "enrollment_009",
        "DELAYED",
        "Connected Therapy Sensor",
        "2026-01-05",
        "2026-01-12",
    ),
    device_order(
        "order_005",
        "enrollment_013",
        "ORDERED",
        "Blood Pressure Monitor",
        "2026-01-03",
        "2026-01-03",
    ),
    device_order(
        "order_006",
        "enrollment_015",
        "DELIVERED",
        "Connected Therapy Sensor",
        "2025-12-31",
        "2026-01-06",
    ),
]


def coordinator_note(
    note_id: str,
    enrollment_id: str,
    note_type: str,
    note_text: str,
    created_at: str,
) -> dict[str, Any]:
    source_enrollment = ENROLLMENT_BY_ID[enrollment_id]
    return tagged(
        {
            "_id": note_id,
            "enrollment_id": enrollment_id,
            "patient_id": source_enrollment["patient_id"],
            "customer_id": source_enrollment["customer_id"],
            "note_type": note_type,
            "note_text": note_text,
            "coordinator_name": "Demo Coordinator",
            "created_at": utc_datetime(created_at),
        }
    )


COORDINATOR_NOTES = [
    coordinator_note(
        "note_001",
        "enrollment_001",
        "ONBOARDING",
        "Demo device setup completed and first reading confirmed.",
        "2026-01-05T14:00:00",
    ),
    coordinator_note(
        "note_002",
        "enrollment_002",
        "OUTREACH",
        "Demo participant requested a follow-up call next week.",
        "2026-01-08T11:30:00",
    ),
    coordinator_note(
        "note_003",
        "enrollment_003",
        "CONSENT",
        "Synthetic consent record confirmed by phone.",
        "2026-01-08T15:15:00",
    ),
    coordinator_note(
        "note_004",
        "enrollment_004",
        "ELIGIBILITY",
        "Eligibility verified; consent outreach remains pending.",
        "2026-01-09T10:00:00",
    ),
    coordinator_note(
        "note_005",
        "enrollment_005",
        "DECLINED",
        "Demo participant declined enrollment during outreach.",
        "2026-01-10T09:45:00",
    ),
    coordinator_note(
        "note_006",
        "enrollment_007",
        "DEVICE",
        "Synthetic scale delivered and paired successfully.",
        "2026-01-04T13:20:00",
    ),
    coordinator_note(
        "note_007",
        "enrollment_009",
        "DEVICE",
        "Demo shipment delayed; coordinator will recheck status.",
        "2026-01-12T16:10:00",
    ),
    coordinator_note(
        "note_008",
        "enrollment_010",
        "CARE_PLAN",
        "Initial synthetic care plan review completed.",
        "2026-01-11T12:30:00",
    ),
    coordinator_note(
        "note_009",
        "enrollment_012",
        "OUTREACH",
        "Monthly demo outreach completed without escalation.",
        "2026-01-26T10:25:00",
    ),
    coordinator_note(
        "note_010",
        "enrollment_015",
        "ONBOARDING",
        "Demo therapy sensor training completed.",
        "2026-01-06T14:40:00",
    ),
]

SEED_DATA = {
    "customers": CUSTOMERS,
    "providers": PROVIDERS,
    "patients": PATIENTS,
    "programs": PROGRAMS,
    "enrollments": ENROLLMENTS,
    "consents": CONSENTS,
    "timer_sessions": TIMER_SESSIONS,
    "device_orders": DEVICE_ORDERS,
    "coordinator_notes": COORDINATOR_NOTES,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_seed_data() -> None:
    """Validate key business rules and relationships before writing data."""
    for collection_name, documents in SEED_DATA.items():
        ids = [document["_id"] for document in documents]
        require(
            len(ids) == len(set(ids)),
            f"Duplicate _id found in {collection_name}.",
        )
        require(
            all(document["seed_batch"] == SEED_BATCH for document in documents),
            f"Missing seed marker in {collection_name}.",
        )

    require(
        set(PROGRAM_BY_CODE) == PROGRAM_CODES,
        "Programs must include RPM, RTM, CCM, CoCM, and APCM.",
    )

    customer_ids = {document["_id"] for document in CUSTOMERS}
    provider_by_id = {document["_id"]: document for document in PROVIDERS}
    require(
        all(document["customer_code"].endswith("_DEMO") for document in CUSTOMERS),
        "Customer identifiers must remain visibly synthetic.",
    )
    require(
        all(
            document["provider_external_id"].startswith("DEMO-")
            for document in PROVIDERS
        ),
        "Provider identifiers must remain visibly synthetic.",
    )
    require(
        all(
            document["patient_external_id"].startswith("DEMO-")
            for document in PATIENTS
        ),
        "Patient identifiers must remain visibly synthetic.",
    )
    for source_patient in PATIENTS:
        require(
            source_patient["customer_id"] in customer_ids,
            f"Unknown customer for {source_patient['_id']}.",
        )
        source_provider = provider_by_id.get(source_patient["primary_provider_id"])
        require(
            source_provider is not None,
            f"Unknown provider for {source_patient['_id']}.",
        )
        require(
            source_provider["customer_id"] == source_patient["customer_id"],
            f"Provider/customer mismatch for {source_patient['_id']}.",
        )

    require(
        {document["status"] for document in ENROLLMENTS} == ENROLLMENT_STATUSES,
        "Enrollment fixtures must cover every allowed status.",
    )
    for source_enrollment in ENROLLMENTS:
        source_patient = PATIENT_BY_ID[source_enrollment["patient_id"]]
        require(
            source_enrollment["customer_id"] == source_patient["customer_id"],
            f"Enrollment/customer mismatch for {source_enrollment['_id']}.",
        )
        require(
            source_enrollment["provider_id"] == source_patient["primary_provider_id"],
            f"Enrollment/provider mismatch for {source_enrollment['_id']}.",
        )
        require(
            source_enrollment["program_code"] in PROGRAM_CODES,
            f"Unknown program for {source_enrollment['_id']}.",
        )

    require(
        {document["status"] for document in CONSENTS} == CONSENT_STATUSES,
        "Consent fixtures must cover every allowed status.",
    )
    for source_consent in CONSENTS:
        source_enrollment = ENROLLMENT_BY_ID[source_consent["enrollment_id"]]
        require(
            source_consent["patient_id"] == source_enrollment["patient_id"],
            f"Consent/patient mismatch for {source_consent['_id']}.",
        )
        require(
            source_consent["program_code"] == source_enrollment["program_code"],
            f"Consent/program mismatch for {source_consent['_id']}.",
        )

    for source_session in TIMER_SESSIONS:
        source_enrollment = ENROLLMENT_BY_ID[source_session["enrollment_id"]]
        require(
            source_session["duration_minutes"] > 0,
            f"Timer duration must be positive for {source_session['_id']}.",
        )
        require(
            source_session["patient_id"] == source_enrollment["patient_id"],
            f"Timer/patient mismatch for {source_session['_id']}.",
        )

    require(
        {document["status"] for document in DEVICE_ORDERS}
        == DEVICE_ORDER_STATUSES,
        "Device order fixtures must cover every allowed status.",
    )
    for source_order in DEVICE_ORDERS:
        source_enrollment = ENROLLMENT_BY_ID[source_order["enrollment_id"]]
        require(
            source_order["patient_id"] == source_enrollment["patient_id"],
            f"Device order/patient mismatch for {source_order['_id']}.",
        )
        require(
            source_order["program_code"] in {"RPM", "RTM"},
            f"Device order must belong to RPM or RTM for {source_order['_id']}.",
        )

    for source_note in COORDINATOR_NOTES:
        source_enrollment = ENROLLMENT_BY_ID[source_note["enrollment_id"]]
        require(
            source_note["patient_id"] == source_enrollment["patient_id"],
            f"Coordinator note/patient mismatch for {source_note['_id']}.",
        )


def mongo_uri_from_environment() -> str:
    """Build a local MongoDB URI unless a container-specific URI is provided."""
    load_dotenv(PROJECT_ROOT / ".env")
    configured_uri = os.getenv("MONGO_URI")
    if configured_uri:
        return configured_uri

    username = quote_plus(os.getenv("MONGO_USER", "mongo"))
    password = quote_plus(os.getenv("MONGO_PASSWORD", "mongo"))
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    database_name = os.getenv("MONGO_DATABASE", "provider_ops")
    auth_source = quote_plus(os.getenv("MONGO_AUTH_SOURCE", "admin"))
    return (
        f"mongodb://{username}:{password}@{host}:{port}/{database_name}"
        f"?authSource={auth_source}"
    )


def mongo_database_name() -> str:
    load_dotenv(PROJECT_ROOT / ".env")
    return os.getenv("MONGO_DATABASE", "provider_ops")


def create_mongo_client() -> MongoClient:
    return MongoClient(
        mongo_uri_from_environment(),
        serverSelectionTimeoutMS=5_000,
    )


def seed_database(database: Database) -> dict[str, int]:
    """Replace this seed batch and return inserted counts by collection."""
    inserted_counts: dict[str, int] = {}
    for collection_name in COLLECTIONS:
        collection = database[collection_name]
        collection.delete_many({"seed_batch": SEED_BATCH})
        documents = SEED_DATA[collection_name]
        if documents:
            collection.insert_many(documents)
        inserted_counts[collection_name] = len(documents)
    return inserted_counts


def main() -> None:
    validate_seed_data()
    client = create_mongo_client()
    try:
        client.admin.command("ping")
        database_name = mongo_database_name()
        inserted_counts = seed_database(client[database_name])
    finally:
        client.close()

    print(f"Seeded MongoDB database '{database_name}' with batch '{SEED_BATCH}':")
    for collection_name, inserted_count in inserted_counts.items():
        print(f"  {collection_name}: {inserted_count}")


if __name__ == "__main__":
    main()
