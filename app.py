# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import db, Artist, Venue, Show
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.order_by(Venue.city, Venue.state).all()
    data = []
    current_city = None
    current_state = None
    venue_group = {}

    for v in venues:
        venue = {
            'id': v.id,
            'name': v.name,
            'num_upcoming_shows': 0
        }
        if v.city == current_city and v.state == current_state:
            venue_group['venues'].append(venue)
        else:
            if current_city is not None:
                data.append(venue_group)

            venue_group['city'] = v.city
            venue_group['state'] = v.state
            venue_group['venues'] = [venue]
        current_city = v.city
        current_state = v.state

    data.append(venue_group)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(search_term))).all()

    data = []
    for v in venues:
        data.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": len(v.shows)
        })

    response = {
        "count": len(data),
        "data": data
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    current_venue = Venue.query.filter(Venue.id == venue_id).one_or_none()
    data = current_venue.format()
    past = list(
        filter(
            lambda show: show.start_time < datetime.today(),
            current_venue.venue_shows))
    upcoming = list(
        filter(
            lambda show: show.start_time >= datetime.today(),
            current_venue.venue_shows))
    data['past_shows'] = [p.format() for p in past]
    data['upcoming_shows'] = [u.format() for u in upcoming]
    data['past_shows_count'] = len(past)
    data['upcoming_shows_count'] = len(upcoming)
    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = Venue()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        generes_array = request.form.getlist('genres')
        venue.genres = ','.join(generes_array)
        venue.website = request.form['website_link']
        if request.form['seeking_talent'] is 'y':
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False
        venue.seeking_description = request.form['seeking_description']
        db.session.add(venue)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' could not be listed!')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    venue = Venue.query.get(venue_id)
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  venue.name + ' could not be deleted!')
        else:
            flash('Venue ' + venue.name +
                  ' was successfully deleted!')
    return None


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).one_or_none().format()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).one_or_none()
    error = False
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        genres_array = request.form.getlist('genres')
        venue.genres = ','.join(genres_array)
        venue.website = request.form['website_link']
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        if request.form['seeking_talent'] is 'y':
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False
        venue.seeking_description = request.form['seeking_description']
        db.session.add(venue)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated.')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = [artist.get_artist_list() for artist in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    results = Artist.query.filter(
        Artist.name.ilike('%{}%'.format(search_term))).all()
    response = {
        'count': len(results),
        'data': results
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    current_artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    data = current_artist.format()
    past = list(
        filter(
            lambda show: show.start_time < datetime.today(),
            current_artist.artist_shows))
    upcoming = list(
        filter(
            lambda show: show.start_time >= datetime.today(),
            current_artist.artist_shows))
    data['past_shows'] = [p.format() for p in past]
    data['upcoming_shows'] = [u.format() for u in upcoming]
    data['past_shows_count'] = len(past)
    data['upcoming_shows_count'] = len(upcoming)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none().format()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    error = False
    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        generes_array = request.form.getlist('genres')
        artist.genres = ','.join(generes_array)
        artist.website = request.form['website_link']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        if request.form['seeking_venue'] is 'y':
            artist.seeking_venue = True
        else:
            artist.seeking_venue = False
        artist.seeking_description = request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be updated.')
        else:
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    error = False
    try:
        artist = Artist()
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        generes_array = request.form.getlist('genres')
        artist.genres = ','.join(generes_array)
        artist.website = request.form['website_link']
        artist.seeking_description = request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
        else:
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = [s.format() for s in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        show = Show()
        show.artist_id = request.form['artist_id']
        show.venue_id = request.form['venue_id']
        show.start_time = request.form['start_time']
        db.session.add(show)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Requested show could not be listed.')
        else:
            flash('Requested show was successfully listed')
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
