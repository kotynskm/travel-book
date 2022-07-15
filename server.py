from asyncore import file_dispatcher
from flask import Flask, render_template, request, session, redirect, jsonify, flash
import requests
import os
from pprint import pprint as pp
from model import User, Trip, Activity, Note, Photo, connect_to_db, db
from datetime import datetime, timedelta
from random import choice
import json
import cloudinary.uploader
from passlib.hash import argon2
from sqlalchemy.sql import text
from geopy.geocoders import Nominatim

TRIP_IMAGES = ['airplane.jpg', 'airplane2.jpg', 'map.jpg', 'map2.jpg', 'map3.jpg', 'map4.jpg', 'airport.jpg', 'man_airport.jpg', 'globe.jpg'] # populate with images, then use random to send an img to trip_details through /trip/ route
YELP_API_KEY = os.environ['YELP_API_KEY']
AVI_API_KEY = os.environ['AVI_API_KEY']
CLOUDINARY_KEY = os.environ['CLOUDINARY_KEY']
CLOUDINARY_SECRET = os.environ['CLOUDINARY_SECRET']
CLOUD_NAME = 'dzkvup9at'
OPEN_WEATHER_KEY = os.environ['OPEN_WEATHER_KEY']

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

# --- login, create user, registration routes ---
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
    hashed = user.password

    if argon2.verify(password, hashed):
        session['user_id'] = user.user_id
    else:
        flash("The email or password you entered was incorrect.")
        return redirect('/')

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
    hashed = argon2.hash(password)
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    user = User.get_by_email(email)
    if user:
        flash("This email is already in use, please try again.")
    else:
        user = User.create_user(fname, lname, email, hashed)
        db.session.add(user)
        db.session.commit()
        flash("Account creation successful! Please login.")

    return redirect('/')

# --- routes for creating a trip and adding items to the trip ---
@app.route('/create-trip', methods=['POST'])
def create_trip():
    """ Create a new trip for the user. """
    # create a class method that checks if a trip already exists?
    trip_name = request.form.get('trip-name')
    city = request.form.get('city')
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
    trip = Trip.create_trip(user_id, trip_name, city, start_date_converted, end_date_converted, trip_image)
    db.session.add(trip)
    db.session.commit()

    return redirect('/homepage')

@app.route('/homepage')
def user_page():
    """ Display trips for the user. """
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    trips = user.trips
    invited_trips = user.invited_trips
    MAPS_API_KEY = os.environ['MAPS_API_KEY']
   
    return render_template('homepage.html', trips=trips, user=user, invited_trips=invited_trips, MAPS_API_KEY=MAPS_API_KEY)

@app.route('/trip/<trip_id>')
def show_trip(trip_id):
    trip = Trip.get_by_id(trip_id)
    MAPS_API_KEY = os.environ['MAPS_API_KEY']

    return render_template('trip_details.html', trip=trip, MAPS_API_KEY=MAPS_API_KEY)

# --- routes for calls to Yelp Fusion API ---
@app.route('/api/activities/<trip_id>')
def show_activities(trip_id):
    """ Makes a call to the Yelp Fusion API to display activities. """
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
    trip = Trip.get_by_id(trip_id)
    
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    location = trip.city
    params = {'location': location, 'limit':10,'sort_by':'rating', 'categories':'restaurants,food'}

    res = requests.get(url,headers=headers,params=params)
    data = res.json()

    return render_template('activities.html', data=data, trip=trip)

@app.route('/api/search/<trip_id>')
def show_custom_activities(trip_id):
    """ Makes a call to the Yelp Fusion API to display custom activities. """
    trip = Trip.get_by_id(trip_id)
    # get category from the form
    custom_category = request.args.get('activity-category')
    
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    location = trip.city
    params = {'location': location, 'limit':10,'sort_by':'rating', 'categories':f'{custom_category}'}

    res = requests.get(url,headers=headers,params=params)
    data = res.json()

    return render_template('activities.html', data=data, trip=trip)

@app.route('/show-business-info')
def show_info():
    business_id = request.args.get('business')
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}

    res = requests.get(f'https://api.yelp.com/v3/businesses/{business_id}', headers=headers)
    data = res.json()

    return jsonify(data)

# --- route for call to OpenWeather API --- #
@app.route('/api/open-weather/<trip_id>')
def show_weather(trip_id):
    """ Makes a call to OpenWeather API to display the weather. """
    trip = Trip.get_by_id(trip_id)
    location_city = trip.city
    units = 'imperial'
    geolocator = Nominatim(user_agent="MyApp")
    location = geolocator.geocode(location_city)
    days = ['Day 1: Monday', 'Day 2: Tuesday', 'Day 3: Wednesday', 'Day 4: Thursday', 'Day 5: Friday',
    'Day 6: Saturday', 'Day 7: Sunday', 'Day 8: Monday']

    res = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={location.latitude}&lon={location.longitude}&units={units}&appid={OPEN_WEATHER_KEY}')
    data = res.json()
    return render_template('weather.html', data=data, trip=trip, days=days)

""" --- routes for call to AviationStack API (function DISABLED, free plan does not allow arrival and depart date params) ---
@app.route('/api/flights/<trip_id>')
def get_flights(trip_id):
    # Get flight info from AviationStack API

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
    # Helper func to get the starter city IATA and end city IATA codes.

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
    return iata_code """
# --- route to create activity --- #
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

# --- routes for Google Maps API markers --- #

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

@app.route('/main-map-coordinates')
def main_marker_info():
    # get the user from session
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    # get the trips from user
    all_trips = user.trips

    # list to get trip city and trip name
    cities = []
    for trip in all_trips:
        cities.append({
            'city_name': trip.city,
            'trip_name': trip.trip_name
        })
    
    # geocode for lat/long for trip city and add to coords list
    coords = []
    geolocator = Nominatim(user_agent="MyApp")
    for city in cities:
        location = geolocator.geocode(city['city_name'])
        coords.append({
            'lat': location.latitude,
            'lng': location.longitude,
            'trip_name': city['trip_name']
        })
        
    return jsonify(coords)

# --- routes for calendar creation and update --- #
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

# --- route to create note --- #
@app.route('/submit_note/<trip_id>', methods=['POST'])
def add_note(trip_id):
    """ Add a note to the trip. """
    trip = Trip.get_by_id(trip_id)
    trip_id = trip.trip_id
    user = trip.user
    user_id = user.user_id
    note = request.form.get('activity-note')
    # create a note and add to db
    trip_note = Note.create_note(note, trip_id, user_id)
    db.session.add(trip_note)
    db.session.commit()
    flash("Note added!")

    return redirect(f'/trip/{trip_id}')

# --- routes for photo upload and call to Cloudinary API --- #
@app.route('/photos/<trip_id>')
def show_photo_page(trip_id):
    """ Display photo page. """
    trip = Trip.get_by_id(trip_id)
    photos = trip.photos

    return render_template('photos.html', trip=trip, photos=photos)

@app.route('/upload-photo/<trip_id>', methods=['POST'])
def upload_photo(trip_id):
    """ Upload a photo. """
    trip = Trip.get_by_id(trip_id)
    trip_id = trip.trip_id
    user = trip.user
    user_id = user.user_id
    my_file = request.files['my-file']
    # call to Cloudinary API
    result = cloudinary.uploader.upload(my_file, api_key=CLOUDINARY_KEY, api_secret=CLOUDINARY_SECRET, cloud_name=CLOUD_NAME)
    img_url = result['secure_url']
    # create a photo and add to db
    photo = Photo.create_photo(img_url, trip_id, user_id)
    db.session.add(photo)
    db.session.commit()

    return redirect(f'/photos/{trip_id}')

# --- route to send trip list to react component --- #
@app.route('/trip-info')
def get_trips():
    """ Get JSON data for trips. """
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    trips = user.trips
   
    trips_list = []
    
    for trip in trips:
        trips_list.append({
            'name': trip.trip_name,
            'url': trip.trip_image,
            'city': trip.city,
            'trip_id': trip.trip_id,
            'start_date': trip.start_date,
            'end_date': trip.end_date
        })
    
    return jsonify(trips_list)

# --- routes to add friends to trip ---
@app.route('/add-friend/<trip_id>', methods=['POST'])
def add_friend(trip_id):
    """ Add a friend to the current trip. """
    trip = Trip.get_by_id(trip_id)
    # get the friend's name from the form
    friend_fname = request.form.get('friend-fname')
    # get friend using fname
    friend = User.get_by_fname(friend_fname)
    # add friend to the invited users of the trip
    trip.invited_users.append(friend)
    db.session.commit()
    flash("Friend added to trip!")

    return redirect(f'/trip/{trip_id}')
    
@app.route('/invited-trip-details/<trip_id>')
def show_invited_trip_details(trip_id):
    """ Display details page for an invited trip. """
    trip = Trip.get_by_id(trip_id)

    return render_template('invited_trip.html', trip=trip)

# --- routes to DELETE trips, notes, activities ---
@app.route('/delete_trip/<trip_id>')
def delete_trip(trip_id):
    """ Delete a trip. """
    
    trip = Trip.get_by_id(trip_id)

    # get trip activities and notes and delete them
    notes = trip.notes
    activities = trip.activities
    invited = trip.invited_users

    for note in notes:
        db.session.delete(note)
        db.session.commit()

    for activity in activities:
        db.session.delete(activity)
        db.session.commit()

    for invitee in invited:
        db.session.delete(invitee)
        db.session.commit()

    # delete the trip
    db.session.delete(trip)
    db.session.commit()

    return "Trip deleted"

@app.route('/delete_note/<trip_id>', methods=['POST'])
def delete_note(trip_id):
    """ Delete a note from trip. """
    note_id = request.form.get('note-id')

    note = Note.get_by_id(note_id)
    db.session.delete(note)
    db.session.commit()

    return redirect(f'/trip/{trip_id}')

@app.route('/delete_activity/<trip_id>', methods=['POST'])
def delete_activity(trip_id):
    """ Delete activity from trip. """
    activity_id = request.form.get('activity-id')

    activity = Activity.get_by_id(activity_id)
    db.session.delete(activity)
    db.session.commit()

    return redirect(f'/trip/{trip_id}')

# --- nav bar routes ---
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
