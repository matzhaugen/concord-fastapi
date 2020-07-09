from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_regularize():
    response = client.post("/concord/",
                           json={"covariance": [[1, 0], [0, 1]], "alpha": 0.2})
    assert response.status_code == 200
    assert set(response.json().keys()).intersection(['regularized'])


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
