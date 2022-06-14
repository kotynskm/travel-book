from flask import Flask, render_template, request, session, redirect, jsonify, flash
import requests
import os
import pprint as pp
from model import User, Trip, Activity, connect_to_db, db

YELP_API_KEY = os.environ['YELP_API_KEY']
yelp_url = 'https://api.yelp.com/v3'

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'


@app.route('/')
def show_login_page():
    """ View the Login page """
    
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def get_login_info():
    """ Log user in """
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.get_by_email(email)
    
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
        return redirect('/')
    else:
        # Log in user by storing the user's email in session
        session['user_email'] = user.email
        flash(f'Welcome back, {user.email}!')

    return render_template('homepage.html', password=password) # I passed variable here for testing

@app.route('/register')
def show_registration_page():
    """ View the registration page. """

    return render_template('registration.html')

@app.route('/users', methods=['POST'])
def create_user():
    """ Create a new user """
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

    


if __name__ == '__main__':
    connect_to_db(app)
    app.run (debug=True, host='0.0.0.0')
