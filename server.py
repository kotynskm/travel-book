from flask import Flask, render_template, request, session, redirect, jsonify, flash
import requests
import os
from pprint import pprint as pp
from model import User, Trip, Activity, connect_to_db, db
from datetime import datetime
from random import choice

TRIP_IMAGES = ['airplane.jpg', 'airplane2.jpg', 'map.jpg', 'map2.jpg', 'map3.jpg', 'map4.jpg'] # populate with images, then use random to send an img to trip_details through /trip/ route
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
    # create a class method that checks if a trip already exists?
    trip_name = request.form.get('trip-name')
    city = request.form.get('city')
    start_date = request.form.get('start')
    end_date = request.form.get('end')
    user_id = session['user_id']

    # convert date strings to date
    start_date_converted = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_converted = datetime.strptime(end_date, '%Y-%m-%d')
    # create trip and add it to database, check if trip already exists - this is not working right now
    # user = User.get_by_id(user_id)
    # user_trips = user.trips
    # for trip in user_trips:
    #     if trip_name == trip.trip_name:
    #         flash("Trip already exists!")
    #     else:
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
    trip_image = choice(TRIP_IMAGES)
    
    return render_template('homepage.html',trips=trips, trip_image=trip_image)

@app.route('/trip/<trip_id>')
def show_trip(trip_id):
    trip = Trip.get_by_id(trip_id)

    return render_template('trip_details.html',trip=trip)

@app.route('/api/activities/<trip_id>')
def show_activities(trip_id):
    """ Makes a call to the Yelp Fusion API to display activities. """
    # makes a call to yelp API to display activites in that city
    # currently not working properly.. because state is not defined in the trip location for API call,
    # user must specify City, State
    trip = Trip.get_by_id(trip_id)
    
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    location = trip.city
    # want to pass in categories (arts,active) for tourist sites, (restaurants,food) for restaurants
    params = {'location': location, 'limit':10,'sort_by':'rating', 'categories':'arts,active'}

    res = requests.get(url,headers=headers,params=params)
    data = res.json()

    return render_template('activities.html', data=data, trip=trip)

@app.route('/api/restaurants/<trip_id>')
def show_restaurants(trip_id):
    """ Makes a call to the Yelp Fusion API to display restaurants. """
    # currently not working properly.. because state is not defined in the trip location for API call,
    # user must specify City, State
    trip = Trip.get_by_id(trip_id)
    
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    location = trip.city
    params = {'location': location, 'limit':10,'sort_by':'rating', 'categories':'restaurants,food'}

    res = requests.get(url,headers=headers,params=params)
    data = res.json()

    return render_template('restaurants.html', data=data, trip=trip)

@app.route('/create-activity/<trip_id>', methods=['POST'])
def create_activity(trip_id):
    """ Create an activity for a trip. """
    trip = Trip.get_by_id(trip_id)
    names = request.form.getlist('business')

    # loop over business names returned from .getlist to create a single activity for each one
    for name in names:
        info = name.split(",")
        activity = Activity.create_activity(trip.trip_id, info[1], info[0])
        db.session.add(activity)

    db.session.commit()
    flash("Activities added!")

    return redirect(f'/trip/{trip_id}')



if __name__ == '__main__':
    connect_to_db(app)
    app.run (debug=True, host='0.0.0.0')
