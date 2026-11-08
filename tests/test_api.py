import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
import fitz
from fastapi.testclient import TestClient
from main import app
client=TestClient(app)
def test_health():
    assert client.get("/health").json()=={"ok":True}
def test_config():
    assert client.get("/config").json()["problems_per_page"]==3
def test_invalid_pdf():
    response=client.post("/convert",files={"file":("bad.pdf",b"not a pdf","application/pdf")})
    assert response.status_code==400
