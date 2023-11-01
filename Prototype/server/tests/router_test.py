from tests import client

def test_index(client):
    index = client.get("/")
    assert index.status_code == 404     # we have no index template yet
