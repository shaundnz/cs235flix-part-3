import csv

from cs235flix.domainmodel.movie import Movie
from cs235flix.domainmodel.actor import Actor
from cs235flix.domainmodel.genre import Genre
from cs235flix.domainmodel.director import Director

class MovieFileCSVReader:

    def __init__(self, file_name: str):
        self.__file_name = file_name
        self.__dataset_of_movies = []
        self.__dataset_of_actors = []
        self.__dataset_of_directors = []
        self.__dataset_of_genres = []

    @property
    def dataset_of_movies(self):
        return self.__dataset_of_movies

    @property
    def dataset_of_actors(self):
        return self.__dataset_of_actors

    @property
    def dataset_of_directors(self):
        return self.__dataset_of_directors

    @property
    def dataset_of_genres(self):
        return self.__dataset_of_genres

    def read_csv_file(self):
        with open(self.__file_name, mode='r', encoding='utf-8-sig') as csvfile:
            # Rank,Title,Genre,Description,Director,Actors,Year,Runtime (Minutes),Rating,Votes,Revenue (Millions),Metascore
            movie_file_reader = csv.DictReader(csvfile)

            index = 0
            for row in movie_file_reader:

                title = row['Title']
                release_year = int(row['Year'])
                self.__dataset_of_movies.append(Movie(title, release_year))

                actors = [Actor(actor.strip()) for actor in row['Actors'].split(",")]
                for actor in actors:
                    if actor not in self.__dataset_of_actors:
                        self.__dataset_of_actors.append(actor)

                director = Director(row['Director'])
                if director not in self.__dataset_of_directors:
                    self.__dataset_of_directors.append(director)

                genres = [Genre(genre.strip()) for genre in row['Genre'].split(",")]
                for genre in genres:
                    if genre not in self.__dataset_of_genres:
                        self.__dataset_of_genres.append(genre)


                # print(f"Movie {index} with title: {title}, release year {release_year}")
                index += 1


