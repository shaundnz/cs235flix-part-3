import pytest

from sqlalchemy.exc import IntegrityError

from cs235flix.domainmodel.actor import Actor
from cs235flix.domainmodel.movie import Movie
from cs235flix.domainmodel.review import Review
from cs235flix.domainmodel.user import User
from cs235flix.domainmodel.director import Director
from cs235flix.domainmodel.genre import Genre


def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO User (username, password) VALUES (:username, :password)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT userID from User where username = :username',
                                {'username': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO User (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT userID from User'))
    keys = tuple(row[0] for row in rows)
    return keys


def test_loading_users(empty_session):
    users = list()
    users.append(("Andrew", "1234"))
    users.append(("Cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User("Andrew", "1234"),
        User("Cindy", "999")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = User("Andrew", "111")
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM User'))
    assert rows == [("Andrew", "111")]


def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_director(empty_session):
    empty_session.execute('INSERT INTO Director (name) VALUES ("Director Boi")')
    expected = Director("Director Boi")
    assert empty_session.query(Director).first() == expected


def test_saving_director(empty_session):
    d = Director("John Doe")
    empty_session.add(d)
    empty_session.commit()

    row = empty_session.execute('SELECT name FROM Director').fetchone()
    assert row[0] == "John Doe"


def test_loading_actor(empty_session):
    empty_session.execute('INSERT INTO Actor (name) VALUES ("Actor Boi")')
    expected = Actor("Actor Boi")
    assert empty_session.query(Actor).first() == expected


def test_saving_actor(empty_session):
    a = Actor("John Doe")
    empty_session.add(a)
    empty_session.commit()

    row = empty_session.execute('SELECT name FROM Actor').fetchone()
    assert row[0] == "John Doe"


def test_loading_genre(empty_session):
    empty_session.execute('INSERT INTO Genre (name) VALUES ("Genre Thing")')
    expected = Genre("Genre Thing")
    assert empty_session.query(Genre).first() == expected


def test_saving_genre(empty_session):
    g = Genre("Action")
    empty_session.add(g)
    empty_session.commit()

    row = empty_session.execute('SELECT name FROM Genre').fetchone()
    assert row[0] == "Action"


def test_loading_movie(empty_session):
    empty_session.execute('INSERT INTO Director (name) VALUES ("Director Boi")')
    empty_session.execute('INSERT INTO Movie (title, releaseYear, runtime, description, directorID)'
                          'VALUES ("Cool Movie", 2019, 120, "Its a cool movie trust me bro", 1)')
    expected = Movie("Cool Movie", 2019)
    actual = empty_session.query(Movie).first()
    assert actual == expected
    assert actual.runtime_minutes == 120
    assert actual.description == "Its a cool movie trust me bro"
    assert actual.director == Director("Director Boi")


def test_saving_movie(empty_session):
    d = Director("John Doe")
    empty_session.add(d)
    empty_session.commit()

    m = Movie("Cool Movie", 2019)
    m.runtime_minutes = 120
    m.description = "Its a cool movie trust me bro"
    m.director = d
    empty_session.add(m)
    empty_session.commit()

    row = empty_session.execute('SELECT * FROM Movie').fetchone()
    assert Movie(row[1], row[2]) == m
    assert row[3] == m.runtime_minutes
    assert row[4] == m.description
    assert empty_session.execute('SELECT name FROM Director WHERE directorID = {}'.format(row[5])).fetchone()[
               0] == "John Doe"


def test_loading_review(empty_session):
    u = User("John Doe", "1234")
    m = Movie("Cool Movie", 2019)
    empty_session.add(u)
    empty_session.add(m)
    empty_session.commit()
    empty_session.execute('INSERT INTO Review (movieID, userID, text, rating) VALUES (1,1,"Very nice", 9)')
    actual = empty_session.query(Review).first()
    assert actual.movie == m
    assert actual.review_text == "Very nice"
    assert actual.rating == 9


def test_saving_review(empty_session):
    u = User("John Doe", "1234")
    m = Movie("Cool Movie", 2019)
    empty_session.add(u)
    empty_session.add(m)

    r = Review(m, "Very nice", 9, "John Doe")
    empty_session.add(r)
    empty_session.commit()
    actual = empty_session.query(Review).first()
    assert actual == r


def test_loading_movie_genre(empty_session):
    m = Movie("Cool Movie", 2019)
    g = Genre("Action")
    empty_session.add(m)
    empty_session.add(g)
    empty_session.commit()
    empty_session.execute('INSERT INTO MovieGenre (movieID, genreID) VALUES (1, 1)')
    actual = empty_session.query(Movie).first()
    assert g in actual.genres


def test_saving_movie_genre(empty_session):
    m = Movie("Cool Movie", 2019)
    g = Genre("Action")
    m.add_genre(g)
    empty_session.add(m)
    empty_session.add(g)
    empty_session.commit()

    row = empty_session.execute('SELECT * FROM MovieGenre').fetchone()
    assert row[0] == 1
    assert row[1] == 1


def test_loading_reviewed_movie(empty_session):
    u = User("John Doe", "1234")
    m = Movie("Cool Movie", 2019)
    empty_session.add(u)
    empty_session.add(m)
    empty_session.commit()

    empty_session.execute('INSERT INTO Review (movieID, userID, text, rating) VALUES (1,1,"Very nice", 9)')
    assert len(m.reviews) == 1
    assert m.reviews[0].movie == m
    assert m.reviews[0].review_text == "Very nice"



def test_saving_reviewed_movie(empty_session):
    u = User("John Doe", "1234")
    m = Movie("Cool Movie", 2019)
    empty_session.add(u)
    empty_session.add(m)

    r = Review(m, "Very nice", 9, "John Doe")
    m.add_review(r)
    assert r in empty_session.query(Movie).first().reviews
