from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from cs235flix.domainmodel.director import Director
from cs235flix.domainmodel.actor import Actor
from cs235flix.domainmodel.genre import Genre
from cs235flix.domainmodel.movie import Movie
from cs235flix.domainmodel.review import Review
from cs235flix.domainmodel.user import User

metadata = MetaData()

DirectorTable = Table(
    'Director', metadata,
    Column('directorID', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255))
)

ActorTable = Table(
    'Actor', metadata,
    Column('actorID', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255))
)

GenreTable = Table(
    'Genre', metadata,
    Column('genreID', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255))
)

UserTable = Table(
    'User', metadata,
    Column('userID', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

MovieTable = Table(
    'Movie', metadata,
    Column('movieID', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('releaseYear', Integer, nullable=False),
    Column('runtime', Integer),
    Column('description', String(4096)),
    Column('directorID', ForeignKey('Director.directorID'))
)

ReviewTable = Table(
    'Review', metadata,
    Column('reviewID', Integer, primary_key=True, autoincrement=True),
    Column('movieID', ForeignKey('Movie.movieID')),
    Column('userID', ForeignKey('User.userID')),
    Column('text', String(4096)),
    Column('rating', Integer)
)

MovieActorTable = Table(
    'MovieActor', metadata,
    Column('movieID', ForeignKey('Movie.movieID'), primary_key=True),
    Column('actorID', ForeignKey('Actor.actorID'), primary_key=True)
)

MovieGenreTable = Table(
    'MovieGenre', metadata,
    Column('movieID', ForeignKey('Movie.movieID'), primary_key=True),
    Column('genreID', ForeignKey('Genre.genreID'), primary_key=True)
)


def map_model_to_tables():
    mapper(Director, DirectorTable, properties={
        '_Director__director_full_name': DirectorTable.c.name,
        '_Director__directed_movies': relationship(Movie, backref='_Movie__director')
    })

    mapper(User, UserTable, properties={
        '_User__user_name': UserTable.c.username,
        '_User__password': UserTable.c.password
    })

    movie_mapper = mapper(Movie, MovieTable, properties={
        '_Movie__title': MovieTable.c.title,
        '_Movie__release_year': MovieTable.c.releaseYear,
        '_Movie__runtime_minutes': MovieTable.c.runtime,
        '_Movie__description': MovieTable.c.description,
        '_Movie__reviews': relationship(Review, backref='_Review__movie')
    })

    mapper(Review, ReviewTable, properties={
        '_Review__review_text': ReviewTable.c.text,
        '_Review__rating': ReviewTable.c.rating
    })

    mapper(Genre, GenreTable, properties={
        '_Genre__genre_name': GenreTable.c.name,
        '_Genre__genre_movies': relationship(movie_mapper, secondary=MovieGenreTable, backref='_Movie__genres')
    })

    mapper(Actor, ActorTable, properties={
        '_Actor__actor_full_name': ActorTable.c.name,
        '_Actor__acted_in': relationship(movie_mapper, secondary=MovieActorTable, backref='_Movie__actors')
    })
