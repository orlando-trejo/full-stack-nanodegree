#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import or_
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    # Relationships
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    # Relationships
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
   __tablename__ = 'Show'

   id = db.Column(db.Integer, primary_key=True)
   date = db.Column(db.DateTime, nullable=True)
   artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
   venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  areas = {}

  for venue in venues:
     key = (venue.city, venue.state)
     num_upcoming_shows = len([show for show in venue.shows if show.date > datetime.now()])

     if key not in areas:
        areas[key] = {
           "city": venue.city,
           "state": venue.state,
           "venues": []
        }
     areas[key]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
  
  data=list(areas.values())
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(or_(Venue.name.ilike(f'%{search_term}%'), 
                                  Venue.city.ilike(f'%{search_term}%'),
                                  Venue.genres.ilike(f'%{search_term}%'))).all()

  response = {
    "count": len(venues),
    "data": [{"id": venue.id, "name": venue.name} for venue in venues]
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.strip('{}').split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [{"artist_id": show.artist_id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link, "start_time": show.date.strftime('%Y-%m-%d %H:%M:%S')} for show in venue.shows if show.date < datetime.now()],
    "upcoming_shows": [{"artist_id": show.artist_id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link, "start_time": show.date.strftime('%Y-%m-%d %H:%M:%S')} for show in venue.shows if show.date >= datetime.now()],
    "past_shows_count": len([show for show in venue.shows if show.date < datetime.now()]),
    "upcoming_shows_count": len([show for show in venue.shows if show.date >= datetime.now()]),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        # Create new Venue object
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            genres=form.genres.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        
        # Add and commit the new venue to the database
        db.session.add(venue)
        db.session.commit()

        # Flash success message
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # Rollback the session in case of an error
        db.session.rollback()

        # Flash error message
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    finally:
        # Close the session
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue_to_delete = Venue.query.filter_by(id=venue_id).delete()
    if venue_to_delete:
       db.session.delete(venue_to_delete)
       db.session.commit()
       return jsonify(success=True)
    else:
      db.session.rollback()
      return jsonify(success=False, error="Venue not found")
  except Exception as e:
     db.session.rollback()
     return jsonify(success=False, error=str(e))
  finally:
     db.session.close()

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
     data.append({
        "id": artist.id,
        "name": artist.name
     })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.strip('{}').split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [{"venue_id": show.venue_id, "venue_name": show.venue.name, "venue_image_link": show.venue.image_link, "start_time": show.date.strftime('%Y-%m-%d %H:%M:%S')} for show in artist.shows if show.date < datetime.now()],
    "upcoming_shows": [{"venue_id": show.venue_id, "venue_name": show.venue.name, "venue_image_link": show.venue.image_link, "start_time": show.date.strftime('%Y-%m-%d %H:%M:%S')} for show in artist.shows if show.date >= datetime.now()],
    "past_shows_count": len([show for show in artist.shows if show.date < datetime.now()]),
    "upcoming_shows_count": len([show for show in artist.shows if show.date >= datetime.now()]),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attribute
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  artist.name = form.name.data
  artist.genres = form.genres.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.website_link = form.website_link.data
  artist.facebook_link = form.facebook_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  artist.image_link = form.image_link.data

  try:
    db.session.commit()
    flash('Artist was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  venue.name = form.name.data
  venue.genres = form.genres.data
  venue.address = form.address.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.website_link = form.website_link.data
  venue.facebook_link = form.facebook_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data
  venue.image_link = form.image_link.data

  try:
     db.session.commit()
     flash('Venue was successfully updated.')
  except:
     db.session.rollback()
     flash('An error occurred. Venue could not be upated.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
     # Create new Artist Object
     artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data
     )

     # Add and commit the new artist to the database
     db.session.add(artist)
     db.session.commit()

     # Flash success message
     flash('Artist ' + request.form['name'] + ' was successfully listed.')
  except:
     # Rollback the session in case of an error
     db.session.rollback()

     # Flash error message
     flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
     # Close the session
     db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.join(Artist).join(Venue).all()

  # Build the data strcuture
  data = []
  for show in shows:
     data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time": show.date.isoformat()
     })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm(request.form)
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = ShowForm(request.form)
  try:
     show = Show(
        date=form.start_time.data,
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data
     )

     # Add and commit the new artist to the database
     db.session.add(show)
     db.session.commit()

     # Flash success message
     flash('Show for ' + request.form['artist_id'] + ' was successfully listed.')
  except Exception as e:
     # Rollback the session in case of an error
     db.session.rollback()

     # Flash error message
     flash('An error occurred. Show for ' + request.form['artist_id'] + ' could not be listed.' + str(e))

  finally:
     # Close the session
     db.session.close()
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
