from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.config import get_settings
from src.database import Base, cleanup_tables, get_db
from src.main import app, import_routers
from src.encounter.constants import BASE_URL as ENCOUNTER_URL
from src.encounter.models import Encounter
from src.encounter.schemas import EncounterBase, EncounterBaseWithId
from src.patient.constants import BASE_URL as PATIENT_URL
from src.patient.models import Patient
from src.patient.schemas import PatientBase, PatientBaseWithId
from unittest.mock import Mock, create_autospec


test_app = TestClient(app)

settings = get_settings()
TEST_DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}"
    f"/{settings.POSTGRES_DB}_test"
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def mock_session() -> tuple[Session, Mock]:
    mock_session = create_autospec(Session, instance=True)
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    return mock_session, mock_query


@pytest.fixture
def test_session():
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield test_app


@pytest.fixture
def encounter_data() -> dict:
    return {
        "patient_id": 1,
        "notes": "An encounter of the 3rd kind.",
        "visit_code": "L3T 1O1",
        "provider": "Miracle Clinic",
        "billing_code": "123.456.789-00",
        "icd10": "A11",
        "total_cost": "12.31",
        "copay": "0.12",
        "chief_complaint": "no complaints",
        "pulse": 0,
        "systolic": 1,
        "diastolic": 2,
        "date": "2024-03-11",
    }


@pytest.fixture
def encounter_base(encounter_data: dict) -> EncounterBase:
    return EncounterBase(**encounter_data)


@pytest.fixture
def encounter_base_with_id(encounter_data: dict) -> EncounterBaseWithId:
    return EncounterBaseWithId(**encounter_data, id=1)


@pytest.fixture
def encounter_model(encounter_base_with_id: EncounterBaseWithId) -> Encounter:
    return Encounter(**encounter_base_with_id.model_dump())


def create_encounter_id(
    patient_id: int,
    encounter: EncounterBase,
    client: TestClient,
) -> int:
    encounter.patient_id = patient_id
    response = client.post(
        url=ENCOUNTER_URL.format(patient_id=patient_id),
        json=encounter.model_dump(),
    )
    return response.json()["id"]


@pytest.fixture
def patient_data() -> dict:
    return {
        "first_name": "Ricky",
        "last_name": "Rando",
        "ssn": "555-55-5555",
        "email": "rrando@catalyte.io",
        "age": 35,
        "height": 69,
        "weight": 220,
        "insurance": "employer",
        "gender": "male",
        "street": "Fake St",
        "city": "Nowhere",
        "state": "OH",
        "postal": "55555",
    }


@pytest.fixture
def patient_base(patient_data: dict) -> PatientBase:
    return PatientBase(**patient_data)


@pytest.fixture
def patient_base_with_id(patient_data: dict) -> PatientBaseWithId:
    return PatientBaseWithId(**patient_data, id=1)


@pytest.fixture
def patient_model(
    patient_base_with_id: PatientBaseWithId, encounter_model: Encounter
) -> Patient:
    return Patient(
        **patient_base_with_id.model_dump(), encounters=[encounter_model]
    )


def create_patient_id(patient: PatientBase, client: TestClient) -> int:
    print(patient.model_dump())
    response = client.post(url=PATIENT_URL, json=patient.model_dump())
    return response.json()["id"]
