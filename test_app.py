from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'

def test_create_and_read_equipment():
    name = 'Test-Pump-01'
    client.delete('/equipment/1')
    response = client.post('/equipment', json={"name": name, "temperature": 42.5, "status": "healthy"})
    assert response.status_code == 201
    equipment_id = response.json()['id']
    response = client.get(f'/equipment/{equipment_id}')
    assert response.status_code == 200
    assert response.json()['name'] == name

def test_invalid_temperature():
    response = client.post('/equipment', json={"name": "Bad", "temperature": 250, "status": "healthy"})
    assert response.status_code == 422

def test_alert_filter():
    response = client.post('/equipment', json={"name": "Pump-Degraded", "temperature": 91, "status": "degraded"})
    assert response.status_code == 201
    alerts = client.get('/alerts')
    assert alerts.status_code == 200
    assert any(item['name'] == 'Pump-Degraded' for item in alerts.json())
