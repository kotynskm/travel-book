""" Data models for travel book itinerary app. """
from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    """ Data model for a user. """

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(40), nullable=False)
    lname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)

    trip = db.relationship('Trip', back_populates='user')

    @classmethod
    def get_by_id(cls, user_id):
        """ Get user by ID. """
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """ Get user by email. """
        return cls.query.filter(User.email == email).first()
    
    @classmethod
    def create_user(cls, fname, lname, email, password):
        """ Create a new user. """
        return cls(fname=fname, lname=lname, email=email, password=password)


    def __repr__(self):
        return f'<User {self.fname} password {self.password} email {self.email} lastname {self.lname}>'

class Trip(db.Model):
    """ Data model for a trip. """

    __tablename__ = 'trips'

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_name = db.Column(db.String(40), nullable=False)
    city = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='trip')
    activities = db.relationship('Activity', back_populates='trips')

    def __repr__(self):
        return f'<Trip {self.trip_id} Name {self.trip_name} City {self.city}>'

class Activity(db.Model):
    """ Data model for an activity. """

    __tablename__ = 'activity'

    activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))
    yelp_id = db.Column(db.String(100))

    
    trips = db.relationship('Trip', back_populates='activities')

    def __repr__(self):
        return f'<Activity {self.activity_id} Type {self.activity_category} Rating {self.rating}'


def connect_to_db(flask_app, db_uri="postgresql:///travel_book", echo=True):
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