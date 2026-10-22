import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

from app.main import app  # noqa: E402


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health():
    r = client().get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_get_user():
    r = client().get("/users/1")
    assert r.status_code == 200
    assert r.get_json()["name"] == "alice"


def test_unknown_user():
    assert client().get("/users/999").status_code == 404


def test_security_headers():
    r = client().get("/")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_search():
    r = client().get("/search?name=alice")
    assert r.get_json()["users"] == [{"id": 1, "name": "alice"}]
