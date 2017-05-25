import couchdb

from skeleton import sum


# Make sure we have a proper server handle
def test_couchdb_version(couchdb_server):
    assert couchdb_server.version().startswith('2.')


# Test that we can create databases
def test_couchdb_create_db(couchdb_server):
    db = couchdb_server.create('test')
    assert db is not None
