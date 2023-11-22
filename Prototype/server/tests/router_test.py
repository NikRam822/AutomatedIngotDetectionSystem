from tests import client

def test_index(client):
    index = client.get("/")
    assert index.status_code == 200     # we have no index template yet
