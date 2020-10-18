import csv
import os
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack
from cs235flix.adapters.repository import AbstractRepository
from cs235flix.domainmodel.actor import Actor
from cs235flix.domainmodel.director import Director
from cs235flix.domainmodel.genre import Genre
from cs235flix.domainmodel.movie import Movie
from cs235flix.adapters.movie_csv_reader import MovieFileCSVReader
from cs235flix.domainmodel.review import Review
from cs235flix.domainmodel.user import User


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_movie(self, movie: Movie):
        self._session_cm.session.add(movie)
        self._session_cm.commit()

    def get_movie(self, movie_name: str, release_year: int) -> Movie:
        movie = None
        try:
            movie = self._session_cm.session.query(Movie).filter(Movie._Movie__title == movie_name).first()
        except NoResultFound:
            pass
        return movie

    def get_all_movies(self):
        all_movies = self._session_cm.session.query(Movie).all()
        return all_movies

    def add_actor(self, actor: Actor):
        self._session_cm.session.add(actor)
        self._session_cm.commit()

    def get_actor(self, actor_name: str) -> Actor:
        actor = None
        try:
            actor = self._session_cm.session.query(Actor).filter(Actor._Actor__actor_full_name == actor_name).first()
        except NoResultFound:
            pass
        return actor

    def add_genre(self, genre: Genre):
        self._session_cm.session.add(genre)
        self._session_cm.commit()

    def get_genre(self, genre_name: str) -> Genre:
        genre = None
        try:
            genre = self._session_cm.session.query(Genre).filter(Genre._Genre__genre_name == genre_name).first()
        except NoResultFound:
            pass
        return genre


    def get_all_genres(self):
        all_genre = self._session_cm.session.query(Genre).all()
        return all_genre

    def add_director(self, director: Director):
        self._session_cm.session.add(director)
        self._session_cm.commit()

    def get_director(self, director_name: str) -> Director:
        director = None
        try:
            director = self._session_cm.session.query(Director).filter(Director._Director__director_full_name == director_name).first()
        except NoResultFound:
            pass
        return director

    def get_number_movies(self):
        number_movies = self._session_cm.session.query(Movie).count()
        return number_movies

    def get_movie_by_index(self, index: int):
        pass

    def get_number_genres(self):
        number_genres = self._session_cm.session.query(Genre).count()
        return number_genres

    def get_genre_by_index(self, index: int) -> Genre:
        pass

    def get_number_movies_for_genre(self, genre: Genre):
        count_tuple = self._session_cm.session.execute('SELECT COUNT(Movie.title) FROM MovieGenre '
                                                                      'INNER JOIN Genre ON Genre.genreID = MovieGenre.genreID '
                                                                      'INNER JOIN Movie ON Movie.movieID = MovieGenre.movieID '
                                                                      'WHERE Genre.name = \'{}\''.format(genre.genre_name)).fetchone()
        return count_tuple[0]

    def get_movies_for_genre(self, genre: Genre) -> List[Movie]:
        all_movies_for_genre_names = self._session_cm.session.execute('SELECT Movie.title FROM MovieGenre '
                                                                'INNER JOIN Genre ON Genre.genreID = MovieGenre.genreID '
                                                                'INNER JOIN Movie ON Movie.movieID = MovieGenre.movieID '
                                                                'WHERE Genre.name = \'{}\''.format(genre.genre_name)).fetchall()
        all_movies_for_genre = self._session_cm.session.query(Movie).filter(Movie._Movie__title.in_([t[0] for t in all_movies_for_genre_names ])).all()
        return all_movies_for_genre

    def add_user(self, user: User):
        self._session_cm.session.add(user)
        self._session_cm.commit()

    def get_user(self, username: str) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter(User._User__user_name == username).first()
        except NoResultFound:
            pass
        return user

    def get_reviews_for_movie(self, movie: Movie):
        movie = self._session_cm.session.query(Movie).filter(Movie._Movie__title == movie.title).first()
        return movie.reviews

    def get_reviews(self):
        all_reviews = self._session_cm.session.query(Review).all()
        return all_reviews

    def add_review(self, review: Review, username):
        self._session_cm.session.add(review)
        self._session_cm.commit()




def populate(session_factory, data_path: str, data_filename):
    filename = os.path.join(data_path, data_filename)
    movie_file_dataset = MovieFileCSVReader(filename)
    movie_file_dataset.read_csv_file()

    with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
        movie_file_reader = csv.DictReader(csvfile)
        for row in movie_file_reader:
            # The get the movie object for the row
            movie_obj = None
            for m in movie_file_dataset.dataset_of_movies:
                if m.title == row['Title'] and m.release_year == int(row['Year']):
                    movie_obj = m
                    break
            movie_obj.runtime_minutes = int(row["Runtime (Minutes)"])
            movie_obj.description = row["Description"]

            # Associate directors
            director_obj = None
            for d in movie_file_dataset.dataset_of_directors:
                if d.director_full_name == row['Director']:
                    director_obj = d
                    break
            movie_obj.director = director_obj
            #director_obj.add_directed_movie(movie_obj)

            # Associate actors
            movie_actors = [Actor(actor.strip()) for actor in row['Actors'].split(",")]
            for actor_obj in movie_file_dataset.dataset_of_actors:
                if actor_obj in movie_actors:
                    #actor_obj.add_acted_in(movie_obj)
                    movie_obj.add_actor(actor_obj)

            # Associate genres
            movie_genres = [Genre(genre.strip()) for genre in row['Genre'].split(",")]
            for genre_obj in movie_file_dataset.dataset_of_genres:
                if genre_obj in movie_genres:
                    #genre_obj.add_genre_movie(movie_obj)
                    movie_obj.add_genre(genre_obj)

    session = session_factory()
    for movie in movie_file_dataset.dataset_of_movies:
        session.add(movie)

    session.commit()

