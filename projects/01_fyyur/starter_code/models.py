
from app import db
from sqlalchemy import CheckConstraint, text, and_

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
    phone = db.Column(db.String(120), nullable=True, unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    # Relationships
    shows = db.relationship('Show', backref='venue', lazy=True)

    # Constraints
    __table_args__ = (
        CheckConstraint(and_(text("length(phone) = 10"), text("phone ~ '^[0-9]+$'")), name='check_phone_number'),
    )

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

    # Constraints
    __table_args__ = (
        CheckConstraint(and_(text("length(phone) = 10"), text("phone ~ '^[0-9]+$'")), name='check_phone_number'),
    )

class Show(db.Model):
   __tablename__ = 'Show'

   id = db.Column(db.Integer, primary_key=True)
   date = db.Column(db.DateTime, nullable=True)
   artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
   venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
