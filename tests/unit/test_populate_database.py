from sqlalchemy import select, inspect

from cs235flix.adapters.orm import metadata


def test_database_populate_table_names(database_engine):
    inspector = inspect(database_engine)
    tables = inspector.get_table_names().sort()

    assert tables == [
        'Director',
        'Actor',
        'Genre',
        'User',
        'Movie',
        'Review',
        'MovieActor',
        'MovieGenre', ].sort()


def test_database_populate_select_all_genres(database_engine):

    with database_engine.connect() as connection:
        genres = connection.execute('SELECT name FROM Genre').fetchall()
        expected = [('Action',), ('Fantasy',), ('Family',), ('Animation',), ('Drama',), ('Music',), ('Romance',),
                    ('Biography',), ('Mystery',), ('Horror',), ('Crime',), ('Thriller',), ('War',), ('History',),
                    ('Comedy',), ('Western',), ('Adventure',), ('Sci-Fi',)]

        assert genres == expected

def test_database_populate_movies(database_engine):
    with database_engine.connect() as connection:
        all_movies = connection.execute('SELECT title FROM Movie').fetchall()
        num_movies = len(all_movies)

        assert all_movies[0][0] == 'Guardians of the Galaxy'
        assert all_movies[num_movies//2][0] == 'Prisoners'
        assert all_movies[-1][0] == 'The Nice Guys'