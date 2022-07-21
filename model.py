""" Data models for travel book itinerary app. """
from unicodedata import name
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy import nullslast
from passlib.hash import argon2

db = SQLAlchemy()

class User(db.Model):
    """ Data model for a user. """

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(40), nullable=False)
    lname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    # relationship to trips and notes
    trips = db.relationship('Trip', back_populates='user')
    # user = db.relationship('User', backref='notes')

    def __repr__(self):
        return f'<User {self.fname} password {self.password} email {self.email} lastname {self.lname}>'

    @classmethod
    def get_by_id(cls, user_id):
        """ Get user by ID. """
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """ Get user by email. """
        return cls.query.filter(User.email == email).first()

    @classmethod
    def get_by_fname(cls, fname):
        return cls.query.filter(User.fname == fname).first()

    
    @classmethod
    def create_user(cls, fname, lname, email, password):
        """ Create a new user. """
        return cls(fname=fname, lname=lname, email=email, password=password)


class Trip(db.Model):
    """ Data model for a trip. """

    __tablename__ = 'trips'

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_name = db.Column(db.String(40), nullable=False)
    city = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    trip_image = db.Column(db.String(40))

    # relationships to user, activities, and notes
    user = db.relationship('User', back_populates='trips')
    activities = db.relationship('Activity', back_populates='trip')
    invited_users = db.relationship('User', secondary='invitation', backref='invited_trips')
    # trip = db.relationship('Trip', backref='notes')

    def __repr__(self):
        return f'<Trip {self.trip_id} Name {self.trip_name} City {self.city}>'

    @classmethod
    def create_trip(cls, user_id, trip_name, city, start_date, end_date, trip_image):
        """ Create a trip. """
        return cls(user_id=user_id, trip_name=trip_name, city=city, start_date=start_date, end_date=end_date, trip_image=trip_image)

    @classmethod
    def get_by_id(cls, trip_id):
        """ Get trip by ID. """
        return cls.query.get(trip_id)

    
class Activity(db.Model):
    """ Data model for an activity. """

    __tablename__ = 'activity'

    activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))
    yelp_id = db.Column(db.String(100))
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(100))
    zipcode = db.Column(db.String(50))
    date = db.Column(db.Date)

    # relationship to trip
    trip = db.relationship('Trip', back_populates='activities')

    def __repr__(self):
        return f'<Activity {self.activity_id} Trip ID {self.trip_id} Yelp ID {self.yelp_id} Name {self.name} Lat {self.latitude} Long {self.longitude} Phone {self.phone} Address {self.address} Zip {self.zipcode}'

    @classmethod
    def create_activity(cls, trip_id, yelp_id, name, latitude, longitude, phone, address, zipcode):
        """ Create an activity. """
        return cls(trip_id=trip_id, yelp_id=yelp_id, name=name, latitude=latitude, longitude=longitude, phone=phone, address=address,
        zipcode=zipcode)

    @classmethod
    def get_by_id(cls, activity_id):
        """ Get activity by ID. """
        return cls.query.get(activity_id)
    

class Note(db.Model):
    """ Data model for a note. """

    __tablename__ = 'notes'

    note_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    note = db.Column(db.String(150))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # relationships to trip and user
    trip = db.relationship('Trip', backref='notes')
    user = db.relationship('User', backref='notes')

    def __repr__(self):
        return f'<Note: {self.note} User: {self.user_id} Trip: {self.trip_id}'


    @classmethod
    def create_note(cls, note, trip_id, user_id):
        """ Create a note. """
        return cls(note=note, trip_id=trip_id, user_id=user_id)

    @classmethod
    def get_by_id(cls, note_id):
        """ Get note by ID. """
        return cls.query.get(note_id)

class Photo(db.Model):
    """ Data model for a photo. """

    __tablename__ = 'photos'

    photo_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    photo = db.Column(db.String(150))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # relationships to trip and user
    trip = db.relationship('Trip', backref='photos')
    user = db.relationship('User', backref='photos')

    def __repr__(self):
        return f'<Photo {self.photo} Trip {self.trip_id} User {self.user_id}'
    
    @classmethod
    def create_photo(cls, photo, trip_id, user_id):
        """ Create a photo. """
        return cls(photo=photo, trip_id=trip_id, user_id=user_id)

    def get_by_id(cls, photo_id):
        """ Get photo by ID. """
        return cls.query.get(photo_id)

class Invitation(db.Model):
    """ Association table between trip and user to invite friends. """

    __tablename__ = 'invitation'

    invitation_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return f'<Invite ID {self.invitation_id} Trip {self.trip_id} User {self.user_id}'


def example_data():
    """ Create sample data for testing. """

    # in case this is run multiple times, clear existing data
    User.query.delete()
    Trip.query.delete()

    # add some sample users and trips
    user1 = User(fname = 'Linda', lname = 'Lane', email = 'one@gmail.com', password = argon2.hash('abc'))
    user2 = User(fname = 'Stacy', lname = 'Smith', email = 'two@gmail.com', password = argon2.hash('onetwo'))

    trip1 = Trip(trip_name = 'pnw hike trip', city = 'Seattle, WA', start_date = '6/16/22', end_date = '6/18/22')
    trip2 = Trip(trip_name = 'beach trip', city = 'San Diego, CA', start_date = '6/16/22', end_date = '6/18/22')

    db.session.add_all([user1, user2, trip1, trip2])
    db.session.commit()



def connect_to_db(flask_app, db_uri="postgresql:///travel_book", echo=False):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)