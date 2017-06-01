def test_appsetup(client):
    response = client.get('/')
    assert response.json == {'message': 'hello world'}
