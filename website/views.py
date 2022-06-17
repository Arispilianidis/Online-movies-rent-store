from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user, logout_user
from .models import MovieModel, UserModel
from werkzeug.security import generate_password_hash
from . import db
from datetime import datetime

views = Blueprint('views', __name__)


@views.route('/')
def home():

    api_endpoints = ["http://127.0.0.1:5000/initializeDB/",
                     "http://127.0.0.1:5000/login (Use POST request with postman)",
                     "http://127.0.0.1:5000/logout",
                     "http://127.0.0.1:5000/movies/",
                     "http://127.0.0.1:5000/movies/Thriller (or <movie_category>)",
                     "http://127.0.0.1:5000/movies/Evil_Dead/info (or /<movie_title>/info)",
                     "http://127.0.0.1:5000/user/rent/Evil_Dead (or <movie_title>",
                     "http://127.0.0.1:5000/user/return/Evil_Dead (or <movie_title>",
                     ]
    temp = []

    username = request.values.get('username')
    if username:
        temp.append({
            "Welcome ": username
        })

    for api in api_endpoints:
        temp.append({
            'route': api,
        })

    return jsonify({'availabe_api_endpoints': temp})

#  User can get a list of all available movies.
@views.route('/movies/')
@login_required
def get_all_movies():
    movies = MovieModel.query.all()
    temp = []
    if movies:
        for movie in movies:
            temp.append({
                'title': movie.title,
                'info': movie.info,
                'category': movie.category,
            })

    return jsonify({'movies': temp})

#  User can get a list of all available movies based on category.
@views.route('/movies/<string:category>')
@login_required
def movie_category(category):

    movies = MovieModel.query.filter_by(category=category).all()
    temp = []
    if movies:
        for movie in movies:
            temp.append({
                'title': movie.title,
                'info': movie.info,
                'category': movie.category,
            })
    else:
        return jsonify({'movies_by_category': f"There is not a movie with the category {category} in the DataBase"})

    return jsonify({'movies_by_category': temp})


# User can navigate and get the details/info of a specific movie.
@views.route('/movies/<string:title>/info')
@login_required
def movie_info(title):

    movie = MovieModel.query.filter_by(title=title).first()

    if not movie:
        return jsonify({'info': f"There is not a movie with the title {title} in the DataBase"})

    return jsonify({f'{title}_info': movie.info})

# User can rent a movie (make available for play).
@views.route('/user/rent/<string:title>', methods=['GET', 'POST'])
@login_required
def rent_movie(title):

    if request.method == 'POST':
        movie = MovieModel.query.filter_by(title=title).first()
        user = UserModel.query.filter_by(id=current_user.id).first()

        if (movie):

            query = f"select * from user_movie where movie_model_id={movie.id} and user_model_id={user.id}"
            already_rented = db.session.execute(query)
            rented_movie = []
            for i in already_rented:
                rented_movie.append(i)

            if len(rented_movie) == 1:
                return f"You already rented this movie at {rented_movie[0][2]}"

            user.movies.append(movie)
            db.session.commit()

            query = f"update user_movie set rent_date = '{datetime.now()}' where movie_model_id={movie.id} and user_model_id={user.id}"
            db.session.execute(query)
            db.session.commit()
        else:
            return f"There is no movie with title {title} in the DataBase"

    return f"User {user.fname} {user.lname} rented successfully {movie}"

# User can return a movie.
@views.route('/user/return/<string:title>', methods=['GET', 'POST'])
@login_required
def return_movie(title):

    if request.method == 'POST':
        movie = MovieModel.query.filter_by(title=title).first()
        user = UserModel.query.filter_by(id=current_user.id).first()

        if (movie):

            query = f"select * from user_movie where movie_model_id={movie.id} and user_model_id={user.id}"
            already_rented = db.session.execute(query)
            rented_movie = []
            for i in already_rented:
                rented_movie.append(i)

            # User can return a movie only if he/she rented it before
            if len(rented_movie) == 1:
                # Cannot return it again
                if rented_movie[0][3] != None:
                    return f"You already returned this movie at {rented_movie[0][3]}"

                query = f"update user_movie set return_date = '{datetime.now()}' where movie_model_id={movie.id} and user_model_id={user.id}"
                db.session.execute(query)
                db.session.commit()
            else:
                return "You have not rented this movie, so you can't return it"

            # Execute this query again because now the return_date was added to the corresponding record
            query = f"select * from user_movie where movie_model_id={movie.id} and user_model_id={user.id}"
            returned_movie_query = db.session.execute(query)
            returned_movie = []
            for i in returned_movie_query:
                returned_movie.append(i)

            print(rented_movie)
            print(returned_movie)

            # Find charge based on days
            days_rented = datetime.strptime(
                returned_movie[0][3], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(returned_movie[0][2], '%Y-%m-%d %H:%M:%S.%f')

            if days_rented.days == 0:  # To cover the case the user returns the movie the same day
                charge = 1
            elif days_rented.days >= 1 and days_rented.days <= 3:
                charge = days_rented.days * 1
            else:
                charge = 3 + (days_rented.days - 3) * 0.5

            # Delete reletionship from user_movie Table
            query = f"delete from user_movie where movie_model_id={movie.id} and user_model_id={user.id}"
            db.session.execute(query)
            db.session.commit()

        else:
            return f"There is no movie with title {title} in the DataBase"

    return f"User {user.fname} {user.lname} \
    rent {movie} for {days_rented.days} days and got charged {charge} $"

# Initialize DB with some data
@views.route('/initializeDB/')
def initializeDB():

    db.drop_all()
    db.create_all()

    db.session.add(
        MovieModel(
            title=("Evil_Dead"),
            info=("This movies is about zombies"),
            category=("Thriller"),
        )
    )
    db.session.add(
        MovieModel(
            title=("Tenacious_D"),
            info=("This movies is about rock music"),
            category=("Comedy"),
        )
    )
    house = MovieModel(
        title=("DR_House"),
        info=("This movies is about medicine"),
        category=("Thriller"),
    )
    db.session.add(house)

    db.session.add(
        UserModel(
            fname=("Aris"),
            lname=("Pilianidis"),
            email=("apiliani@auth.gr"),
            password=generate_password_hash(
                "123", method='sha256'),
            movies=[house]
        )
    )

    db.session.commit()

    logout_user()

    return "Added development dataset in the DataBase"
