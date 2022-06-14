from flask import Flask, render_template, request, session, redirect, jsonify, flash
import requests
import os
from pprint import pprint as pp
from model import User, Trip, Activity, connect_to_db, db
from datetime import datetime

YELP_API_KEY = os.environ['YELP_API_KEY']
yelp_url = 'https://api.yelp.com/v3'

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'


@app.route('/')
def show_login_page():
    """ View the Login page. """
    
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def get_login_info():
    """ Log user in. """
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.get_by_email(email)
    
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
        return redirect('/')
    else:
        # Log in user by storing the user's id in session
        session['user_id'] = user.user_id
        flash(f'Welcome back, {user.fname}!')

    return redirect('/homepage')

@app.route('/register')
def show_registration_page():
    """ View the registration page. """

    return render_template('registration.html')

@app.route('/users', methods=['POST'])
def create_user():
    """ Create a new user. """
    email = request.form.get('email')
    password = request.form.get('password')
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    user = User.get_by_email(email)
    if user:
        flash("This email is already in use, please try again.")
    else:
        user = User.create_user(fname, lname, email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account creation successful! Please login.")

    return redirect('/')

@app.route('/create-trip', methods=['POST'])
def create_trip():
    """ Create a new trip for the user. """
    trip_name = request.form.get('trip-name')
    city = request.form.get('city')
    start_date = request.form.get('start')
    end_date = request.form.get('end')
    user_id = session['user_id']

    # convert date strings to date
    start_date_converted = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_converted = datetime.strptime(end_date, '%Y-%m-%d')
    # create trip and add it to database
    trip = Trip.create_trip(user_id, trip_name, city, start_date_converted, end_date_converted)
    db.session.add(trip)
    db.session.commit()
    flash("Trip created!")

    return redirect('/homepage')

@app.route('/homepage')
def user_page():
    """ Display trips for the user. """
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    trips = user.trips
    
    return render_template('homepage.html',trips=trips)



if __name__ == '__main__':
    connect_to_db(app)
    app.run (debug=True, host='0.0.0.0')
