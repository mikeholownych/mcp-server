from fastapi.testclient import TestClient
from mcp_server.enhancement_approval import app

client = TestClient(app)

def test_approve_enhancement():
    response = client.post(
        "/api/approve-enhancement",
        json={"enhancement_id": "enh1", "approver_email": "approver@example.com"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "Approved"}
    # Further assertions can be made to verify that 'approves_enhancements' is updated
