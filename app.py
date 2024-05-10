# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
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
db.app = app
db.init_app(app)
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
    venues = Venue.query.order_by(Venue.city).all()
    data = []
    venue_group = set()
    for venue in venues:
        venue_group.add((venue.city, venue.state)) 
    for (city, state) in venue_group:
        venue_array = []
        for venue in venues:
            if (venue.city == city) and (venue.state == state):
              upcoming = list(filter(lambda show: show.start_time >= datetime.today(), venue.venue_shows))
              venue_array.append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": len(upcoming)
              })
        data.append({
            "city": city,
            "state": state,
            "venues": venue_array
        })
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
    shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id)
    past_shows = []
    upcoming_shows = []

    for show in shows:
        show_info = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': show.start_time.strftime("%m%d%y, %H%M")
        }
        if show.start_time <= datetime.now():
            past_shows.append(show_info)
        else:
            upcoming_shows.append(show_info)
   
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue = Venue(
                name = form.name.data,
                city = form.city.data,
                state = form.state.data,
                address = form.address.data,
                phone = form.phone.data,
                image_link = form.image_link.data,
                facebook_link = form.facebook_link.data,
                genres = form.genres.data,
                website = form.website_link.data,
                seeking_talent = form.seeking_talent.data,
                seeking_description = form.seeking_description.data
            )
            db.session.add(venue)
            db.session.commit()
        except ValueError as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        flash('Venue ' + request.form['name'] +
                ' was successfully listed!') 
        return render_template('pages/home.html')
    else:
        message = []
        for field, errors in form.errors.items():
            for error in errors:
                message.append(f"{field}: {error}")
        flash('Please fix the following errors: ' + ", ".join(message))
        form = VenueForm()
        return render_template('forms/new_venue.html', form=form)


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
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.genres = form.genres.data
            venue.website = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            db.session.add(venue)
            db.session.commit()
        except ValueError as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        flash('Venue ' + request.form['name'] +
                ' was successfully updated!') 
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        message = []
        for field, errors in form.errors.items():
            for error in errors:
                message.append(f"{field}: {error}")
        flash('Please fix the following errors: ' + ", ".join(message))
        form = VenueForm()
        return render_template('forms/edit_venue.html', form=form, venue=venue)

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
    shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id)
    past_shows = []
    upcoming_shows = []

    for show in shows:
        show_info =  {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.strftime("%m%d%y, %H%M")
        }
        if show.start_time <= datetime.now():
            past_shows.append(show_info)
        else:
            upcoming_shows.append(show_info)
   
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none().format()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.image_link = form.image_link.data
            artist.facebook_link = form.facebook_link.data
            artist.genres = form.genres.data
            artist.website = form.website_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            db.session.add(artist)
            db.session.commit()
        except ValueError as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        message = []
        for field, errors in form.errors.items():
            for error in errors:
                message.append(f"{field}: {error}")
        flash('Please fix the following errors: ' + ", ".join(message))
        form = ArtistForm()
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            artist = Artist(
                name = form.name.data,
                city = form.city.data,
                state = form.state.data,
                phone = form.phone.data,
                image_link = form.image_link.data,
                facebook_link = form.facebook_link.data,
                genres = form.genres.data,
                website = form.website_link.data,
                seeking_venue = form.seeking_venue.data,
                seeking_description = form.seeking_description.data
            )
            db.session.add(artist)
            db.session.commit()
        except ValueError as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        flash('Artist ' + request.form['name'] +
                  ' was successfully listed!') 
        return render_template('pages/home.html')
    else:
        message = []
        for field, errors in form.errors.items():
            for error in errors:
                message.append(f"{field}: {error}")
        flash('Please fix the following errors: ' + ", ".join(message))
        form = ArtistForm()
        return render_template('forms/new_artist.html', form=form)


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
    form = ShowForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            show = Show(
                start_time = form.start_time.data,
                artist_id = form.artist_id.data,
                venue_id = form.venue_id.data
            )
            db.session.add(show)
            db.session.commit()
        except ValueError as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        flash('Requested show was successfully listed')
        return render_template('pages/home.html')
    else:
        message = []
        for field, errors in form.errors.items():
            for error in errors:
                message.append(f"{field}: {error}")
        flash('Please fix the following errors: ' + ", ".join(message))
        form = ShowForm()
        return render_template('forms/new_show.html', form=form)


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
