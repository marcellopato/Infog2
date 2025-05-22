def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Lu Estilo API está funcionando!"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_not_found(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404

def test_middleware_handling(client):
    response = client.get("/health", headers={"Origin": "http://localhost"})
    assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
    assert response.headers["access-control-allow-origin"] == "*"
