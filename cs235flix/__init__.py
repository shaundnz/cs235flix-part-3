"""Initialize CS235-Flix Flask app."""

import os

from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import NullPool

import cs235flix.adapters.repository as repo
from cs235flix.adapters.memory_repository import MemoryRepository, populate
from cs235flix.adapters.orm import metadata, map_model_to_tables

from cs235flix.adapters import database_repository

def create_app(test_config=None):
    app = Flask(__name__)

    # Set up config file
    app.config.from_object('config.Config')

    # Config data path for the repository
    data_path = os.path.join('cs235flix', 'adapters', 'data')

    repo.repo_instance = MemoryRepository()

    if test_config is not None:
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']
        populate(os.path.join(data_path), "Data100movies.csv", repo.repo_instance)

    if app.config['REPOSITORY'] == 'memory':
        populate(os.path.join(data_path), "Data1000movies.csv", repo.repo_instance)
    elif app.config['REPOSITORY'] == 'database':
        # Configure database.
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']

        # We create a comparatively simple SQLite database, which is based on a single file (see .env for URI).
        # For example the file database could be located locally and relative to the application in covid-19.db,
        # leading to a URI of "sqlite:///covid-19.db".
        # Note that create_engine does not establish any actual DB connection directly!
        database_echo = app.config['SQLALCHEMY_ECHO']
        database_engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool,
                                        echo=database_echo)

        # Create the database session factory using sessionmaker (this has to be done once, in a global manner)
        session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
        # Create the SQLAlchemy DatabaseRepository instance for an sqlite3-based repository.
        repo.repo_instance = database_repository.SqlAlchemyRepository(session_factory)


        if app.config['TESTING'] == 'True' or len(database_engine.table_names()) == 0:
            print("REPOPULATING DATABASE")
            # For testing, or first-time use of the web application, reinitialise the database.
            clear_mappers()
            metadata.create_all(database_engine)  # Conditionally create database tables.
            for table in reversed(metadata.sorted_tables):  # Remove any data from the tables.
                database_engine.execute(table.delete())

            # Generate mappings that map domain model classes to the database tables.
            map_model_to_tables()

            database_repository.populate(session_factory, data_path, "Data1000movies.csv")

        else:
            # Solely generate mappings that map domain model classes to the database tables.
            map_model_to_tables()





    # repo.repo_instance = MemoryRepository()

    # Populate the MemoryRepository with data
    #populate(os.path.join(data_path), "Data1000movies.csv", repo.repo_instance)


    with app.app_context():
        # Register blueprints
        from .movies import movies
        app.register_blueprint(movies.movies_blueprint)

        from .home import home
        app.register_blueprint(home.home_blueprint)

        from .genres import genres
        app.register_blueprint(genres.genres_blueprint)

        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        from .search import search
        app.register_blueprint(search.search_blueprint)

        # Register a callback the makes sure that database sessions are associated with http requests
        # We reset the session inside the database repository before a new flask request is generated
        @app.before_request
        def before_flask_http_request_function():
            if isinstance(repo.repo_instance, database_repository.SqlAlchemyRepository):
                repo.repo_instance.reset_session()

        # Register a tear-down method that will be called after each request has been processed.
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            if isinstance(repo.repo_instance, database_repository.SqlAlchemyRepository):
                repo.repo_instance.close_session()

    return app