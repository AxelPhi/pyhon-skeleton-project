import os
import time

import couchdb
import docker
import pytest


# The docker hub coucdh image we use
IMAGE = 'klaemo/couchdb'


# 'Session' meaning that this fixture is valid for the whole
# test run (we don't need to create the client for every
# single test
@pytest.fixture(scope="session")
def docker_client():

    client = docker.DockerClient(
        base_url='unix://var/run/docker.sock', version='auto')
    client.ping()
    return client


# Same for the API client
@pytest.fixture(scope="session")
def docker_api_client():
    api_client = docker.APIClient(
        base_url='unix://var/run/docker.sock', version='auto')
    return api_client


# Create a container running CouchDB and yield a
# session persistent server handle to the
# indivdual tests.
# After the tests are run, the container is
# stopped and removed
@pytest.yield_fixture(scope="session")
def couchdb_server(docker_client, docker_api_client):

    docker_client.images.pull(IMAGE)
    container = docker_client.containers.create(
        image=IMAGE,
        detach=True,
        labels=['testing'],
        ports={
            5984: 5984
        }
    )

    try:
        container.start()
        container_info = docker_api_client.inspect_container(container.id)
        ip = container_info['NetworkSettings']['IPAddress']
        count = 0
        while count < 10:
            try:
                server = couchdb.Server('http://{}:5984'.format(ip))
                server.version()
                break
            except ConnectionRefusedError as refused:
                count += 1
                time.sleep(5)

        if count == 10:
            raise IOError("Can't connect to CoucDB container")

        yield server

    finally:
        container.remove(force=True)
