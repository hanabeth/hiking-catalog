from functools import wraps
from sqlalchemy import create_engine, update
from urlparse import urlparse
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Location, HikingTrail, User
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string
from flask import Flask, request, redirect, flash, jsonify
from flask import url_for, render_template, make_response

app = Flask(__name__)

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Hiking Catalog"

engine = create_engine('sqlite:///hiking.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


###############################################################
# Login in - create anti-forgery state token. Store is session.
###############################################################

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

###############################################################
###############################################################


###############################################################
###############################################################
# Google and Facebook connect functions..
###############################################################
###############################################################

# Route function accepts POST request
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the auth code.'), 401)
        repsonse.headers['Content-Type'] = 'application/json'
        return response

    # Check for a valid access token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # Check for access token error. If there is one, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Validate that access token is the correct one for the user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if access token is valid for app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token client ID doesn't match the app."), 401)
        print "Token's client ID doesn't match the application's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('User is currently already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check for existing user.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Hello, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    return output


# Facebook login.
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # Exchange client token for server-side token.
    app_id = json.loads(open('fb_client_secrets.json').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.12/oauth/access_token?grant_type=' +
           'fb_exchange_token&client_id=%s&client_secret=%s&' +
           'fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    # Extracting the token from the response.
    token = data['access_token']

    url = 'https://graph.facebook.com/v2.12/me?access_token=%s'
    '&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['access_token'] = token

    # Check for existing user.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Hello, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    return output

###############################################################
# End of Google and Facebook login functions.
###############################################################


###############################################################
###############################################################
# User login functions.
###############################################################
###############################################################

# login_required - function decorator for login status checks.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You do not have access to this page.")
            return redirect('/login')
    return decorated_function


# Create User - takes in login_session and creates the new user.
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get User ID -
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Get User Info - returns user object associated with the user id number.
def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None

##############################################################
# End of user login functions.
##############################################################


###############################################################
###############################################################
# Google and Facebook disconnect functions..
###############################################################
###############################################################

# Disconnect the session and revoke the current user's auth token.
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    # Check if the user is currently connected.
    if access_token is None:
        print 'Access token is none'
        response = make_response(json.dumps(
            'The current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # HTTP GET request to revoke current token.
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # If status is 200, reset the user's login session.
    if result['status'] == '200':
        print 'this is 200 status'
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps(
            'User has been disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # Invalid token was given.
        response = make_response(json.dumps(
            'There was an error when trying to revoke this token.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect Facebook login session.
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?'
    'access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have logged out...'

##############################################################
# End of Google and Facebook logout functions.
##############################################################


###############################################################
###############################################################
# Show data using JSON APIs
###############################################################
###############################################################

# Format the locations data into JSON.
@app.route('/locations/JSON/')
def locationsJSON():
    locations = session.query(Location).all()
    return jsonify(locations=[r.serialize for r in locations])


# Route to GET all hiking trails for location and display the description.
@app.route('/locations/<int:location_id>/JSON/')
def showTrailsJSON(location_id):
    location = session.query(Location).filter_by(id=location_id).one()
    trails = session.query(HikingTrail).filter_by(
        location_id=location_id).all()
    return jsonify(trails=[i.serialize for i in trails])


# Route to GET specific hiking trail and display the description of trail.
@app.route('/locations/<int:location_id>/<int:trail_id>/details/JSON/')
def showTrailDetailsJSON(location_id, trail_id):
    Hiking_Trail = session.query(HikingTrail).filter_by(id=trail_id).one()
    return jsonify(Hiking_Trail=Hiking_Trail.serialize)


###############################################################
###############################################################
# CRUD functions.
###############################################################
###############################################################

# GET locations - this route displays a list of locations that are
# currently available (available meaning that they have already been
# added to the database previously).
@app.route('/')
@app.route('/locations/')
def showLocations():
    locations = session.query(Location).all()
    latestTrails = session.query(HikingTrail).order_by(
        HikingTrail.id.desc()).limit(5)
    if 'username' not in login_session:
        return render_template('publicCatalogMain.html',
                               locations=locations, trails=latestTrails)
    else:
        return render_template('catalogMain.html',
                               locations=locations, trails=latestTrails)


# Creates a new location.
@app.route('/locations/new', methods=['GET', 'POST'])
def newLocation():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        # Login authorization of user.
        newLocation = Location(
            country=request.form['country'],
            user_id=login_session.get('user_id')
        )
        session.add(newLocation)
        session.commit()
        flash('The new location has been created.')
        return redirect(url_for('showLocations'))
    else:
        return render_template('newLocation.html')


# Update an existing location IF you are the user who created the location.
@app.route('/locations/<int:location_id>/edit', methods=['GET', 'POST'])
@login_required
def editLocation(location_id):
    updatedLocation = session.query(Location).filter_by(id=location_id).one()

    if updatedLocation.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert"
    "('You are not authorized to edit this locastion.');}</script>"
    "<body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['country']:
            updatedLocation.country = request.form['country']
            return redirect(url_for('showLocations'))
    else:
        return render_template('editLocation.html', location=updatedLocation)


# Route that the user is directed to when they select the option of deleting
# a location. This will contain a DELETE method.
@app.route('/locations/<int:location_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteLocation(location_id):
    deleteLocation = session.query(Location).filter_by(id=location_id).one()
    if deleteLocation.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert"
    "('You are not authorized to delete this location.');}</script>"
    "<body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deleteLocation)
        flash('%s has been deleted.' % deleteLocation.country)
        session.commit()
        return redirect(url_for('showLocations', location_id=location_id))
    else:
        return render_template('deleteLocation.html', location=deleteLocation)


# When a user selects a location from the main page, they will
# be directed to a list of hiking trails that are in that location.
@app.route('/locations/<int:location_id>')
def showTrails(location_id):
    location = session.query(Location).filter_by(id=location_id).one()
    creator = getUserInfo(location.user_id)
    trails = session.query(HikingTrail).filter_by(
        location_id=location_id).all()
    if ('username' not in login_session or
            location.user_id != login_session['user_id']):
        return render_template('publicTrails.html',
                               trails=trails, location=location)
    else:
        return render_template('trails.html', trails=trails,
                               location=location, creator=creator)


# This is the route that invokes a method to add a new hiking
# trail to a specific location.
@app.route('/locations/<int:location_id>/new', methods=['GET', 'POST'])
@login_required
def newTrail(location_id):
    if request.method == 'POST':
        trail = HikingTrail(
            trailName=request.form['trailName'],
            province=request.form['province'],
            park=request.form['park'],
            website=request.form['website'],
            description=request.form['description'],
            location_id=location_id,
            user_id=login_session.get('user_id')
        )
        session.add(trail)
        session.commit()
        return redirect(url_for('showTrails', location_id=location_id))
    else:
        return render_template('newTrail.html', location_id=location_id)


# This route will be used when a user clicks on a hiking trail
# to see more information. They will be redirected to a page that
# has the hiking trail's details, along with options to edit
# or remove the hiking trail.
@app.route('/locations/<int:location_id>/<int:trail_id>/details')
def showTrailDetails(location_id, trail_id):
    trail = session.query(HikingTrail).filter_by(id=trail_id).one()
    if ('username' not in login_session or
            trail.user_id != login_session['user_id']):
        return render_template('publicTrailDetails.html',
                               location_id=location_id, trail=trail)
    else:
        return render_template('trailDetails.html',
                               location_id=location_id, trail=trail)


# This method will be invoked when a user chooses the option to
# edit a specific hiking trail. This will contain a PUT method.
@app.route('/locations/<int:location_id>/<int:trail_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editTrail(trail_id, location_id):
    editTrail = session.query(HikingTrail).filter_by(id=trail_id).one()
    if editTrail.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert"
    "('You are not authorized to edit this hiking trail.');}</script>"
    "<body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['trailName']:
            editTrail.trailName = request.form['trailName']
        if request.form['province']:
            editTrail.province = request.form['province']
        if request.form['park']:
            editTrail.park = request.form['park']
        if request.form['website']:
            editTrail.website = request.form['website']
        if request.form['description']:
            editTrail.description = request.form['description']
        session.add(editTrail)
        session.commit()
        return redirect(url_for('showTrailDetails',
                                location_id=location_id, trail_id=trail_id))
    else:
        return render_template('editTrail.html', location_id=location_id,
                               trail_id=trail_id, trail=editTrail)


# Route for when the user selects that they want to delete a specific
# hiking trail from the parent locaton.
@app.route('/<int:location_id>/<int:trail_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteTrail(location_id, trail_id):
    deleteTrail = session.query(HikingTrail).filter_by(id=trail_id).one()
    if deleteTrail.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert"
    "('You are not authorized to delete this trail.');}</script>"
    "<body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deleteTrail)
        session.commit()
        return redirect(url_for('showTrails', location_id=location_id))
    else:
        return render_template('deleteTrail.html', location_id=location_id,
                               trail=deleteTrail)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
