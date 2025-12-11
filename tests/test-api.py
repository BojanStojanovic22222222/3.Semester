import os
os.environ["TESTING"] = "1"   

import json
from datetime import datetime
import pytest
from app import app, db, Measurement


@pytest.fixture(autouse=True)
def setup_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield



def test_api_data_post():
    client = app.test_client()

    payload = {
        "patient_id": 1,
        "bpm": 75,
        "spo2": 99,
        "temperature": 36.5,
        "timestamp": int(datetime.utcnow().timestamp())
    }

    response = client.post("/api/data",
                           data=json.dumps(payload),
                           content_type="application/json")

    assert response.status_code == 200
    assert response.json["status"] == "OK"



def test_api_history_get():
    client = app.test_client()
    response = client.get("/api/history")

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_database_insert():
    with app.app_context():
        m = Measurement(
            patient_id=1,
            bpm=70,
            spo2=98,
            temperature=36.7
        )
        db.session.add(m)
        db.session.commit()

        found = Measurement.query.first()
        assert found is not None
        assert found.bpm == 70
