# Travel Book

<img src="/static/img/login.png">

***

# Project Overview
Travel Book is a fullstack itinerary application for planning and organizing trips. The user can create trips, add activities, notes, photos, and friends to their trip. Furthermore, the user can view and schedule their activities on a calendar, as well as view the weather in the city where they are traveling to assist them in planning their itinerary.

## Technologies
**Languages:** Python, JavaScript (AJAX, JSON), HTML, CSS, SQL  
**Frameworks & Libraries:** Flask, jQuery, Bootstrap, Jinja, SQLAlchemy ORM  
**Database & Industry Tools:** PostgreSQL, Git, GitHub, Command Line
**APIs:** Google Maps, Yelp Fusion, OpenWeather, Cloudinary

# <a name="about"></a>Learn More About the Developer
**GitHub:** https://github.com/kotynskm/travel-book  
**LinkedIn:** https://www.linkedin.com/in/kkotynski
**Medium:** https://medium.com/@k.kotynski

# Table of Contents
- [About the Developer](#about)
- [Features](#features)
- [Installation](#installation)
- [References](#references)

## <a name="features"></a>Features
#### Create a trip/view trips
<img src="/static/img/homepage.png" align="right" width="50%">
<img src="/static/img/homepage-map.png" align="right" width="50%">
A user can create a trip, view trips/invited trips on the homepage. A google map with markers for each trip is displayed on the page using the Google Maps API and JavaScript. When the user creates a new trip, the information from the form is sent to the server as a POST request, and the trip cards are displayed on the page using React.

## <a name="installation"></a>Installation
To run Travel Book on your local machine:

Clone this repo:
```
https://github.com/kotynskm/travel-book.git
```

Create and activate a virtual environment inside your Travel Book directory:
```
virtualenv env (Mac OS)
virtualenv env --always-copy (Windows OS)
source env/bin/activate
```

Install the dependencies:
```
pip3 install -r requirements.txt
```

Set up the database:

```
createdb travel_book
```

Run the app:

```
python3 server.py
```

You can now navigate to 'localhost:5000/' to use Travel Book!






