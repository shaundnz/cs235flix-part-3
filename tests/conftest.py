import os
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from cs235flix import create_app
from cs235flix.adapters import memory_repository, database_repository
from cs235flix.adapters.orm import metadata, map_model_to_tables
from cs235flix.adapters.memory_repository import MemoryRepository

TEST_DATA_PATH = os.path.join('tests', 'data')
TEST_DATABASE_URI_IN_MEMORY = 'sqlite://'
TEST_DATABASE_URI_FILE = 'sqlite:///movies.db'

@pytest.fixture
def in_mem_repo():
    repo = MemoryRepository()
    memory_repository.populate(TEST_DATA_PATH, "Data100Movies.csv", repo)
    return repo


@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,
        'TEST_DATA_PATH': TEST_DATA_PATH,
        'WTF_CSRF_ENABLED': False,
        'REPOSITORY': 'memory'
    })

    return my_app.test_client()

@pytest.fixture
def database_engine():
    engine = create_engine(TEST_DATABASE_URI_FILE)
    clear_mappers()
    metadata.create_all(engine)  # Conditionally create database tables.
    for table in reversed(metadata.sorted_tables):  # Remove any data from the tables.
        engine.execute(table.delete())
    map_model_to_tables()
    database_repository.populate(session_factory, TEST_DATA_PATH, "Data100Movies.csv")
    yield engine
    metadata.drop_all(engine)
    clear_mappers()

@pytest.fixture
def empty_session():
    engine = create_engine(TEST_DATABASE_URI_IN_MEMORY)
    metadata.create_all(engine)
    for table in reversed(metadata.sorted_tables):
        engine.execute(table.delete())
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    yield session_factory()
    metadata.drop_all(engine)
    clear_mappers()

@pytest.fixture
def session():
    clear_mappers()
    engine = create_engine(TEST_DATABASE_URI_IN_MEMORY)
    metadata.create_all(engine)
    for table in reversed(metadata.sorted_tables):
        engine.execute(table.delete())
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    database_repository.populate(session_factory, TEST_DATA_PATH, "Data100Movies.csv")
    yield session_factory()
    metadata.drop_all(engine)
    clear_mappers()

@pytest.fixture
def session_factory():
    clear_mappers()
    engine = create_engine(TEST_DATABASE_URI_IN_MEMORY)
    metadata.create_all(engine)
    for table in reversed(metadata.sorted_tables):
        engine.execute(table.delete())
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    database_repository.populate(session_factory, TEST_DATA_PATH, "Data100Movies.csv")
    yield session_factory
    metadata.drop_all(engine)
    clear_mappers()



@pytest.fixture
def auth(client):
    return AuthenticationManager(client)



class AuthenticationManager:
    def __init__(self, client):
        self._client = client

    def login(self, username='shaunp', password='pw123456'):
        return self._client.post(
            '/authentication/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/authentication/logout')
