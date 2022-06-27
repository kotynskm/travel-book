from asyncore import file_dispatcher
from flask import Flask, render_template, request, session, redirect, jsonify, flash
import requests
import os
from pprint import pprint as pp
from model import User, Trip, Activity, Note, connect_to_db, db
from datetime import datetime, timedelta
from random import choice
import json

TRIP_IMAGES = ['airplane.jpg', 'airplane2.jpg', 'map.jpg', 'map2.jpg', 'map3.jpg', 'map4.jpg', 'airport.jpg', 'man_airport.jpg', 'globe.jpg'] # populate with images, then use random to send an img to trip_details through /trip/ route
YELP_API_KEY = os.environ['YELP_API_KEY']
AVI_API_KEY = os.environ['AVI_API_KEY']

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
    depart_city = request.form.get('depart_city')
    start_date = request.form.get('start')
    end_date = request.form.get('end')
    user_id = session['user_id']
    trip_image = choice(TRIP_IMAGES)

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
    trip = Trip.create_trip(user_id, trip_name, city, start_date_converted, end_date_converted, trip_image, depart_city)
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
   
    return render_template('homepage.html',trips=trips, user=user)

@app.route('/trip/<trip_id>')
def show_trip(trip_id):
    trip = Trip.get_by_id(trip_id)
    MAPS_API_KEY = os.environ['MAPS_API_KEY']

    return render_template('trip_details.html',trip=trip, MAPS_API_KEY=MAPS_API_KEY)

@app.route('/api/activities/<trip_id>')
def show_activities(trip_id):
    """ Makes a call to the Yelp Fusion API to display activities. """
    # makes a call to yelp API to display activites in that city
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
    # user must specify City, State
    trip = Trip.get_by_id(trip_id)
    
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    location = trip.city
    params = {'location': location, 'limit':10,'sort_by':'rating', 'categories':'restaurants,food'}

    res = requests.get(url,headers=headers,params=params)
    data = res.json()

    return render_template('restaurants.html', data=data, trip=trip)

@app.route('/api/flights/<trip_id>')
def get_flights(trip_id):
    trip = Trip.get_by_id(trip_id)
    url = 'http://api.aviationstack.com/v1/flights'
    # Get the depart city, arrival city
    depart_city = trip.depart_city
    arrival_city = trip.city
    # Get the airport IATA code for depart and arrival city
    depart_iata = get_airport_code(depart_city)
    arrival_iata = get_airport_code(arrival_city)


    params = {'access_key': AVI_API_KEY, 'limit': 10, 'dep_iata': depart_iata, 'arr_iata': arrival_iata}
    # if get airport returns none have some kind of error
    res = requests.get(url, params=params)
    data = res.json()

    return render_template('flights.html', data=data, trip=trip)

def get_airport_code(city):
    """ Helper func to get the starter city IATA and end city IATA codes. """
    iata_code = None
    # from City, ST grab the city using split and index
    city_name = city.split(',')[0]
    # open the file and store in a variable so we can view it's contents
    airport_file = open('airport_data.json')
    # use json.load to convert json string file into python dictionary
    json_airport_file = json.load(airport_file)
    # loop over each obj in data file
    for obj in json_airport_file:
        if obj['city'] == city_name:
            iata_code = obj['code']

    airport_file.close()
    return iata_code


@app.route('/create-activity/<trip_id>', methods=['POST'])
def create_activity(trip_id):
    """ Create an activity for a trip. """
    trip = Trip.get_by_id(trip_id)
    names = request.form.getlist('business')

    # loop over business names returned from .getlist to create a single activity for each one
    for name in names:
        info = name.split(",")
        activity = Activity.create_activity(trip.trip_id, info[1], info[0], info[2], info[3], info[4], info[5], info[6])
        db.session.add(activity)

    db.session.commit()
    flash("Activities added!")

    return redirect(f'/trip/{trip_id}')

@app.route('/map-coordinates/<int:trip_id>')
def marker_info(trip_id):
    """ Get JSON data for map markers. """
    trip = Trip.get_by_id(trip_id)

    activities = []
    for activity in trip.activities:
        activities.append({
            'name': activity.name,
            'lat': activity.latitude,
            'lng': activity.longitude,
            'phone': activity.phone,
            'address': activity.address,
            'zipcode': activity.zipcode
        })
    return jsonify(activities)

@app.route('/calendar/<trip_id>')
def view_calendar(trip_id):
    """ View calendar of events for trip. """
    trip = Trip.get_by_id(trip_id)
    activities = trip.activities

    days = calculate_days(trip)
    return render_template('calendar.html', trip=trip, activities=activities, days=days)

def calculate_days(trip):
    days = []
    trip_start = trip.start_date
    trip_end = trip.end_date
    delta = trip_end - trip_start
    for i in range(delta.days + 1):
        day = trip_start + timedelta(days=i)
        days.append(day)
    return days

@app.route('/update_calendar/<trip_id>', methods=['POST'])
def update_calendar(trip_id):
    """ Add event to the calendar. """
    activity_id = request.form.get('activity')
    date = request.form.get('day')
    current_activity = Activity.get_by_id(activity_id)
    current_activity.date = date
    db.session.commit()
   
    return redirect(f'/calendar/{trip_id}')

@app.route('/send_calendar_data/<int:trip_id>')
def calendar_info(trip_id):
    """ Get JSON data for calendar. """
    trip = Trip.get_by_id(trip_id)
    activities = []
    for activity in trip.activities:
        if activity.date:
            activities.append({
                'title': activity.name,
                'start': activity.date.strftime("%Y-%m-%d")
            })
    data = {
        'trip_start': trip.start_date.strftime("%Y-%m-%d"),
        'activities': activities
    }
    return jsonify(data)

@app.route('/submit_note/<trip_id>', methods=['POST'])
def add_note(trip_id):
    """ Add a note to the trip. """
    trip = Trip.get_by_id(trip_id)
    trip_id = trip.trip_id
    user = trip.user
    user_id = user.user_id
    note = request.form.get('activity-note')

    trip_note = Note.create_note(note, trip_id, user_id)
    db.session.add(trip_note)
    db.session.commit()

    return redirect(f'/trip/{trip_id}')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/home')
def redirect_homepage():
    return redirect('/homepage')




if __name__ == '__main__':
    connect_to_db(app)
    app.run (debug=True, host='0.0.0.0')
