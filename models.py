from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


show_items = db.Table(
    'show_items', db.Column(
        'show_id', db.Integer, db.ForeignKey('Show.id'), primary_key=True), db.Column(
            'venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True), db.Column(
                'artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True))


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id'),
        nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    venue = db.relationship('Venue')
    artist = db.relationship('Artist')

    def format(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'venue_image_link': self.venue.image_link,
            'start_time': self.start_time.isoformat()
        }


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
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    artists = db.relationship('Artist', secondary=show_items)
    shows = db.relationship('Show', secondary=show_items, backref='venues')
    venue_shows = db.relationship('Show')

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres.split(','),
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description
        }


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
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    venues = db.relationship('Venue', secondary=show_items)
    shows = db.relationship('Show', secondary=show_items, backref='artists')
    artist_shows = db.relationship('Show')

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres.split(','),
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
        }

    def get_artist_list(self):
        return {
            'id': self.id,
            'name': self.name
        }
