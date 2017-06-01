import contextlib
import time

import couchdb
import docker
import pytest


# Fixtures can have dependencies on each other
# That way you can have abstraction layers of fixtures
#
# Dependency: Two clients we need to setup docker containers
#
# 'session' scope meaning that this fixture is valid for the whole
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


#
# Dependency: A container
#
# 'module' scope meaning that this fixture is valid for all tests
# running in the same module. Because it is a "yield_fixture",
# we can have code running after the test are done, cleaning up
# the container
#
# "docker_client" and "docker_api_client" are fixtures we depend
# on. py.test will create those first and set them here.
#
# "image" will tell docker what image to pull from the registry
#
# "ports" will set what ports to expose
#
#
@pytest.yield_fixture(scope="module")
def couchdb_container(docker_client, docker_api_client,
                      ):
    # The docker hub couchdb image we use
    image = 'klaemo/couchdb'
    ports = {5984: 5984}

    with build_container(docker_client, docker_api_client, image, ports) as container:
        yield container


# Create a container running CouchDB and yield a
# session persistent server handle to the
# indivdual tests.
# After the tests are run, the container is
# stopped and removed
@pytest.yield_fixture(scope="module")
def couchdb_server(couchdb_container):

    ip = couchdb_container['NetworkSettings']['IPAddress']
    count = 0
    while count < 10:
        try:
            server = couchdb.Server('http://{}:5984'.format(ip))
            server.version()
            yield server
            break
        except ConnectionRefusedError as refused:
            count += 1
            time.sleep(5)

        if count == 10:
            raise IOError("Can't connect to CoucDB container")


# Utility function to create a new container and cleanly
# remove it after use. Should be used in fixtures that
# provide container services.
# Recommended use is with "yield_fixtures".
#
# e.g.
#   with build_container(docker_client, docker_api_client, image, ports) as container:
#     yield container
# ...
#
@contextlib.contextmanager
def build_container(docker_client, docker_api_client, image, ports=None):

    if not ports:
        ports = {}

    docker_client.images.pull(image)
    container = docker_client.containers.create(
        image=image,
        detach=True,
        labels=['integration-testing'],
        ports=ports
    )

    try:
        container.start()
        container_info = docker_api_client.inspect_container(container.id)

        yield container_info

    finally:
        container.remove(force=True)
