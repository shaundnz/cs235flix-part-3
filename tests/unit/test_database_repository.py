import pytest

from cs235flix.adapters.database_repository import SqlAlchemyRepository

from cs235flix.domainmodel.actor import Actor
from cs235flix.domainmodel.movie import Movie
from cs235flix.domainmodel.review import Review
from cs235flix.domainmodel.user import User
from cs235flix.domainmodel.director import Director
from cs235flix.domainmodel.genre import Genre


def test_repository_add_movie(session_factory):
    m = Movie("Cool Movie", 2018)
    repo = SqlAlchemyRepository(session_factory)

    repo.add_movie(m)
    assert m is repo.get_movie("Cool Movie", 2014)


def test_repository_get_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    m = repo.get_movie("Guardians of the Galaxy", 2014)
    assert m == Movie("Guardians of the Galaxy", 2014)


def test_repository_get_non_existent_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    m = repo.get_movie("I dont exist", 2015)
    assert m is None


def test_repository_get_number_movies(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    assert repo.get_number_movies() == 100


def test_repository_get_all_movies(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    all_movies = repo.get_all_movies()
    all_movies.sort()
    assert len(all_movies) == 100
    assert all_movies[0] == Movie("5- 25- 77", 2007)
    assert all_movies[99] == Movie("Zootopia", 2016)


def test_repository_add_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    a = Actor("John Doe")
    repo.add_actor(a)
    assert a is repo.get_actor("John Doe")


def test_repository_get_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    a = repo.get_actor("Chris Pratt")
    assert a == Actor("Chris Pratt")


def test_repository_get_non_existent_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    assert repo.get_actor("Fake Name") is None


def test_repository_add_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    d = Director("John Doe")
    repo.add_director(d)
    assert d is repo.get_director("John Doe")


def test_repository_get_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    d = repo.get_director("Christopher Nolan")
    assert d == Director("Christopher Nolan")


def test_repository_get_non_existent_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    assert repo.get_director("Fake Director") is None


def test_repository_add_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    g = Genre("Documentary")
    repo.add_genre(g)
    assert repo.get_genre("Documentary") is g


def test_repository_get_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    g = repo.get_genre("Action")
    assert g == Genre("Action")


def test_repository_get_non_existent_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    assert repo.get_genre("Fake Genre") is None


def test_repository_get_number_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    assert repo.get_number_genres() == 18


def test_repository_get_all_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    all_genres = repo.get_all_genres()
    all_genres.sort()
    assert len(all_genres) == 18
    assert all_genres[0] == Genre("Action")
    assert all_genres[17] == Genre("Western")


def test_repository_get_number_movies_for_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    action_movies_num = repo.get_number_movies_for_genre(Genre("Action"))
    assert action_movies_num == 39


def test_repository_get_movies_for_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    thriller_movies = repo.get_movies_for_genre(Genre("Thriller"))
    for movie in thriller_movies:
        assert Genre("Thriller") in movie.genres


def test_add_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    u = User("newuser1", "password")
    repo.add_user(u)
    assert repo.get_user("newuser1") is u


def test_get_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    u = User("newuser2", "pw12345")
    repo.add_user(u)
    assert repo.get_user("newuser2") == User("newuser2", "pw12345")


def test_get_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    assert repo.get_user("fakeuser") is None


def test_add_review(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    u = User("newuser1", "password")
    repo.add_user(u)
    r = Review(repo.get_movie("Guardians of the Galaxy", 2014), "This is the review text", 9, "newuser1")
    repo.add_review(r, "newuser1")
    assert r in repo.get_reviews()
    assert r in repo.get_reviews_for_movie(Movie("Guardians of the Galaxy", 2014))


def test_get_reviews_for_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    u1 = User("newuser1", "password")
    repo.add_user(u1)
    r1 = Review(repo.get_movie("Guardians of the Galaxy", 2014), "This is the review text", 9, "newuser1")
    u2= User("newuser2", "password")
    repo.add_user(u2)
    r2 = Review(repo.get_movie("Guardians of the Galaxy", 2014), "This is the other review", 2, "newuser2")

    repo.add_review(r1, "newuser1")
    repo.add_review(r2, "newuser2")

    assert len(repo.get_reviews_for_movie(Movie("Guardians of the Galaxy", 2014))) == 2
    assert r1 in repo.get_reviews_for_movie(Movie("Guardians of the Galaxy", 2014))
    assert r2 in repo.get_reviews_for_movie(Movie("Guardians of the Galaxy", 2014))